import os
from bs4 import BeautifulSoup
from utils import gestionar_rutas, validar_netscape
import ValidadorLinks

def extraer_estructura(soup, resultados_validados=None):
    """
    Recorre los elementos y genera las líneas. 
    Si recibe resultados_validados (dict), separa los caídos al final.
    """
    lineas = []
    caidos = []
    # Creamos un mapa rápido de URL -> Estado para no buscar en lista mil veces
    mapa_estados = {res['url']: res['estado'] for res in resultados_validados} if resultados_validados else {}

    # Buscamos todos los H3 (carpetas) y A (links) en el orden en que aparecen
    elementos = soup.find_all(['h3', 'a'])
    
    for el in elementos:
        if el.name == 'h3':
            # Es una carpeta
            nombre = el.get_text().strip()
            lineas.append(f"C: {nombre}")
        elif el.name == 'a':
            # Es un marcador
            url = el.get('href', '')
            nombre = el.get_text().strip().replace(',', '')
            if not nombre: 
                nombre = url[:30]
            
            # Verificamos si este link fue validado como caído
            estado = mapa_estados.get(url, "ACTIVO")
            if "CAIDO" in estado or "ERROR" in estado:
                caidos.append(f"    K: {nombre} | {estado} | {url}")
            else:
                lineas.append(f"    K: {nombre}")

    # Si hubo caídos, creamos la carpeta especial al final del archivo
    if caidos:
        lineas.append("\nC: REVISAR - LINKS CAIDOS O ERRORES")
        lineas.extend(caidos)
        
    return lineas

def obtener_lista_para_validar(soup):
    """Extrae una lista de diccionarios para el validador"""
    marcadores = []
    for a in soup.find_all('a'):
        marcadores.append({
            'nombre': a.get_text().strip() or a.get('href', '')[:30],
            'url': a.get('href', '')
        })
    return marcadores

def main(path_html_directo=None):
    if path_html_directo:
        path_in = path_html_directo
        base_dir = os.path.dirname(os.path.abspath(path_in))
        path_conf = os.path.join(base_dir, "config_GENERADO.txt")
        print(f"\n⏳ Generando configuración para: {os.path.basename(path_in)}")
    else:
        # path_in: HTML original | path_conf: Donde se guardará el borrador
        path_in, path_conf, _ = gestionar_rutas("generador")
    
    if not path_in or not os.path.exists(path_in):
        print(f"❌ No se encontró el archivo de entrada en: {path_in}")
        return
    
    try:
        with open(path_in, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        dl_principal = soup.find('dl') or soup.find('DL')

        if not dl_principal:
            print("❌ No se encontró estructura de marcadores.")
            return

        # --- LÓGICA DE VALIDACIÓN OPCIONAL ---
        resultados = None
        respuesta = input("¿Deseas validar si los links están caídos? (S/N): ").lower()
        
        if respuesta == 's':
            lista_preparada = obtener_lista_para_validar(dl_principal)
            print("1. Modo Paciente (Uno por uno)")
            print("2. Modo Turbo (Rápido - recomendado)")
            modo = input("Selecciona modo (1/2): ")
            
            if modo == '2':
                resultados = ValidadorLinks.validar_lista_modo_turbo(lista_preparada)
            else:
                resultados = ValidadorLinks.validar_lista_modo_paciente(lista_preparada)

        print(f"\n⏳ Analizando: {os.path.basename(path_in)}...")
        
        # Generamos la estructura (pasando los resultados si existen)
        estructura = extraer_estructura(dl_principal, resultados)
        
        if not estructura:
            print("⚠️ Se leyó el archivo pero la estructura resultó vacía.")
            return

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