import os
from bs4 import BeautifulSoup
from utils import gestionar_rutas

def parse_config(config_path):
    """Lee el config.txt y extrae carpetas y links (soporta nombres con URLs)."""
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
                # Extraemos el contenido después de 'K: '
                contenido = line[3:].strip()
                # Si el config tiene pipes '|', la URL suele ser la última parte
                partes = [p.strip() for p in contenido.split('|')]
                nombre_en_config = partes[0]
                url_en_config = partes[-1] if len(partes) > 1 else None
                
                if carpeta_actual not in tree: tree[carpeta_actual] = []
                tree[carpeta_actual].append({
                    'nombre': nombre_en_config,
                    'url_posible': url_en_config
                })
                
    return tree

def escribir_dl(f, resultado):
    for carpeta, links in resultado.items():
        if not links: continue # No crear carpetas vacías
        f.write(f'    <DT><H3>{carpeta}</H3>\n    <DL><p>\n')
        for link in links:
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

    mapeo_deseado = parse_config(path_config)
    
    with open(path_in, 'r', encoding='utf-8', errors='ignore') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    # --- MEJORA: DOBLE BIBLIOTECA DE BÚSQUEDA ---
    biblio_nombres = {}
    biblio_urls = {}
    for a in soup.find_all('a'):
        nombre_html = a.get_text().strip()
        url_html = a.get('href', '')
        biblio_nombres[nombre_html] = a
        biblio_urls[url_html] = a

    vistos = set()
    resultado_final = {}
    stats = {"procesados": 0, "eliminados": 0, "organizados": 0, "sin_config": 0}

    for carpeta, items_config in mapeo_deseado.items():
        resultado_final[carpeta] = []
        for item in items_config:
            stats["procesados"] += 1
            nombre_cfg = item['nombre']
            url_cfg = item['url_posible']
            
            # ESTRATEGIA DE BÚSQUEDA:
            # 1. Intentar por URL (es lo más seguro si el config la tiene)
            link_obj = biblio_urls.get(url_cfg) if url_cfg else None
            
            # 2. Si no, intentar por nombre exacto
            if not link_obj:
                link_obj = biblio_nombres.get(nombre_cfg)
            
            # 3. Si no, intentar ver si el nombre en config es una URL recortada
            if not link_obj:
                for url_h, obj in biblio_urls.items():
                    if url_h.startswith(nombre_cfg):
                        link_obj = obj
                        break

            if link_obj:
                url_final = link_obj.get('href')
                if url_final in vistos:
                    stats["eliminados"] += 1
                    continue
                
                vistos.add(url_final)
                resultado_final[carpeta].append(link_obj)
                stats["organizados"] += 1
            else:
                stats["sin_config"] += 1

    with open(path_out, 'w', encoding='utf-8') as f:
        f.write('<!DOCTYPE NETSCAPE-Bookmark-file-1>\n'
                '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">\n'
                '<TITLE>Bookmarks</TITLE>\n<H1>Bookmarks</H1>\n<DL><p>\n')
        escribir_dl(f, resultado_final)
        f.write('</DL><p>\n')

    print("\n" + "="*40)
    print("         INFORME DE ORGANIZACIÓN")
    print("="*40)
    print(f"Links procesados:          {stats['procesados']}")
    print(f"Duplicados eliminados:    {stats['eliminados']}")
    print(f"Links rescatados (OK):    {stats['organizados']}")
    if stats['sin_config'] > 0:
        print(f"No encontrados:           {stats['sin_config']}")
        print("💡 Los 'No encontrados' ahora son solo aquellos que")
        print("   realmente no existen en el HTML original.")
    print("-" * 40)
    print(f"Archivo final: {os.path.basename(path_out)}")
    print("="*40)

if __name__ == "__main__":
    main()