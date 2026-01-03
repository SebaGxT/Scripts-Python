import os
from bs4 import BeautifulSoup
from utils import gestionar_rutas, validar_netscape

def extraer_estructura(dl_node, nivel=0):
    """
    Recorre recursivamente los nodos <DL> y <DT> del archivo Netscape
    para extraer la jerarquía de carpetas (C:) y marcadores (K:).
    """
    lineas = []
    espacios = "    " * nivel

    # Buscamos los elementos DT que son hijos directos del DL actual
    for dt in dl_node.find_all('dt', recursive=False):
        h3 = dt.find('h3', recursive=False)
        a = dt.find('a', recursive=False)
        
        if h3:
            # Detectamos una carpeta
            nombre_carpeta = h3.text.strip()
            lineas.append(f"{espacios}C: {nombre_carpeta}")

            # Buscamos el siguiente bloque <DL> que contiene los hijos de esta carpeta
            # En el formato Netscape, el <DL> suele ser un hermano del <DT> o estar dentro.
            sig_dl = dt.find('dl', recursive=False) or dt.find_next_sibling('dl')
            
            # Si el DL es hermano, verificamos que no pertenezca a otro H3
            if sig_dl:
                lineas.extend(extraer_estructura(sig_dl, nivel + 1))

        elif a:
            # Detectamos un marcador (Link)
            # Usamos el nombre del marcador como palabra clave inicial
            nombre_link = a.text.strip().replace(',', '')
            if nombre_link:
                lineas.append(f"{espacios}K: {nombre_link}")
    return lineas

def main(path_html_directo=None):
    if path_html_directo:
        path_in = path_html_directo
        base_dir = os.path.dirname(os.path.abspath(path_in))
        path_conf = os.path.join(base_dir, "config_GENERADO.txt")
        print(f"⏳ Generando configuración para: {os.path.basename(path_in)}")
    else:
         # Obtenemos las rutas usando la utilidad compartida
        # path_in: HTML original | path_conf: Donde se guardará el borrador
        path_in, path_conf, _ = gestionar_rutas("generador")
    
    if not path_in: 
        return

    print("⏳ Leyendo archivo original...")
    try:
        with open(path_in, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        dl_principal = soup.find('dl')
        if not dl_principal:
            print("❌ No se encontró estructura de marcadores.")
            return

        estructura = extraer_estructura(dl_principal)
        
        with open(path_conf, 'w', encoding='utf-8') as f:
            f.write("# ARCHIVO DE CONFIGURACIÓN GENERADO\n")
            f.write("# Instrucciones: Edita y renombra a 'config.txt'\n\n")
            f.write("\n".join(estructura))
        
        print(f"\n✅ ¡Proceso completado con éxito!")
        print(f"📂 Archivo borrador creado en: {path_conf}")
        print("\n👉 Próximo paso: Abre el archivo, edita tu estructura ideal y")
        print("   luego ejecuta el Organizador.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()