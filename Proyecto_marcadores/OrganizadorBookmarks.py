import os
from bs4 import BeautifulSoup
from utils import gestionar_rutas

def parse_config(config_path):
    """
    Lee el config.txt adaptado a nuestra estructura de C: (Carpeta) y K: (Link).
    """
    tree = {}
    carpeta_actual = "00. Sin Clasificar"
    if not os.path.exists(config_path): return None
    
    with open(config_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"): continue
            
            if line.startswith("C: "):
                carpeta_actual = line[3:].strip()
                if carpeta_actual not in tree:
                    tree[carpeta_actual] = []
            elif line.startswith("K: "):
                # Extraemos el nombre. Si hay pipes '|', tomamos solo la primera parte
                contenido = line[3:].strip()
                nombre_limpio = contenido.split('|')[0].strip()
                if carpeta_actual not in tree: tree[carpeta_actual] = []
                tree[carpeta_actual].append(nombre_limpio)
                
    return tree

def escribir_dl(f, resultado):
    """Escribe el HTML final respetando las carpetas."""
    for carpeta, links in resultado.items():
        f.write(f'    <DT><H3>{carpeta}</H3>\n    <DL><p>\n')
        for link in links:
            # 'link' ya es un objeto de BeautifulSoup, str(link) devuelve el HTML <A HREF="...">...</a>
            f.write(f'        <DT>{str(link)}\n')
        f.write(f'    </DL><p>\n')

def main(path_html_directo=None):
    if path_html_directo:
        path_in = path_html_directo
        base_dir = os.path.dirname(os.path.abspath(path_in))
        path_config = os.path.join(base_dir, "config.txt")
        path_out = os.path.join(base_dir, "Favoritos_ORGANIZADOS.html")
    else:
        path_in, path_config, path_out = gestionar_rutas("organizador")

    if not path_in or not os.path.exists(path_config):
        print(f"❌ Error: No se encuentra 'config.txt' en {path_config}")
        return

    # 1. Cargar la estructura deseada desde el config
    mapeo_deseado = parse_config(path_config)
    
    # 2. Leer el HTML original para tener los objetos de los links
    with open(path_in, 'r', encoding='utf-8', errors='ignore') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    # Creamos un diccionario de búsqueda rápida: { "Nombre del Link": Objeto_BeautifulSoup }
    biblioteca_links = {}
    for a in soup.find_all('a'):
        nombre = a.get_text().strip()
        if nombre not in biblioteca_links:
            biblioteca_links[nombre] = a

    vistos = set()
    resultado_final = {}
    stats = {"procesados": 0, "eliminados": 0, "organizados": 0, "sin_config": 0}

    # 3. Construir el resultado basado en el orden del config.txt
    for carpeta, nombres_en_config in mapeo_deseado.items():
        resultado_final[carpeta] = []
        for nombre in nombres_en_config:
            stats["procesados"] += 1
            
            # Buscar el objeto original por nombre
            link_obj = biblioteca_links.get(nombre)
            
            if link_obj:
                url = link_obj.get('href')
                # --- CONTROL DE DUPLICADOS ---
                if url in vistos:
                    stats["eliminados"] += 1
                    continue
                
                vistos.add(url)
                resultado_final[carpeta].append(link_obj)
                stats["organizados"] += 1
            else:
                stats["sin_config"] += 1

    # 4. Escribir el archivo
    with open(path_out, 'w', encoding='utf-8') as f:
        f.write('<!DOCTYPE NETSCAPE-Bookmark-file-1>\n'
                '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">\n'
                '<TITLE>Bookmarks</TITLE>\n<H1>Bookmarks</H1>\n<DL><p>\n')
        escribir_dl(f, resultado_final)
        f.write('</DL><p>\n')

    # --- INFORME ---
    print("\n" + "="*40)
    print("         INFORME DE ORGANIZACIÓN")
    print("="*40)
    print(f"Links procesados:         {stats['procesados']}")
    print(f"Duplicados eliminados:    {stats['eliminados']}")
    print(f"Links en nuevo HTML:      {stats['organizados']}")
    if stats['sin_config'] > 0:
        print(f"Links no encontrados*:    {stats['sin_config']}")
        print("(* Nombres que editaste y no coinciden con el original)")
    print("-" * 40)
    print(f"Archivo final: {os.path.basename(path_out)}")
    print("="*40)

if __name__ == "__main__":
    main()