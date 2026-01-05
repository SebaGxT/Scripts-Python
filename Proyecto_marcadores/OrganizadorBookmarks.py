import os
import re
from bs4 import BeautifulSoup
from utils import gestionar_rutas

def normalizar(texto):
    """
    La clave del éxito: Quita símbolos, espacios y pone en minúsculas.
    Esto hace que 'Google, el buscador' sea igual a 'googleelbuscador'.
    """
    if not texto: return ""
    # Quitamos acentos y caracteres especiales, dejamos solo letras y números
    texto = texto.lower()
    return re.sub(r'[^a-z0-9]', '', texto)

def parse_config(config_path):
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
                contenido = line[3:].strip()
                partes = [p.strip() for p in contenido.split('|')]
                
                nombre_en_config = partes[0]
                # Si hay validador, la URL está al final. Si no, intentamos capturarla.
                url_en_config = partes[-1] if len(partes) > 1 and "http" in partes[-1] else None
                
                if carpeta_actual not in tree: tree[carpeta_actual] = []
                tree[carpeta_actual].append({
                    'nombre': nombre_en_config,
                    'url_posible': url_en_config
                })
    return tree

def escribir_dl(f, resultado):
    for carpeta, links in resultado.items():
        if not links: continue
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
        print(f"❌ Error: Archivos no encontrados.")
        return

    mapeo_deseado = parse_config(path_config)
    
    with open(path_in, 'r', encoding='utf-8', errors='ignore') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    # --- BIBLIOTECAS DE BÚSQUEDA ---
    biblio_urls = {}
    biblio_nombres_norm = {} # Usamos nombres normalizados como clave
    
    for a in soup.find_all('a'):
        url_html = a.get('href', '')
        nombre_html_norm = normalizar(a.get_text())
        
        biblio_urls[url_html] = a
        if nombre_html_norm:
            biblio_nombres_norm[nombre_html_norm] = a

    vistos = set()
    resultado_final = {}
    stats = {"procesados": 0, "eliminados": 0, "organizados": 0, "sin_config": 0}

    # --- PROCESO DE EMPAREJAMIENTO ---
    
    for carpeta, items_config in mapeo_deseado.items():
        resultado_final[carpeta] = []
        for item in items_config:
            stats["procesados"] += 1
            nombre_cfg = item['nombre']
            nombre_cfg_norm = normalizar(nombre_cfg)
            url_cfg = item['url_posible']
            
            link_obj = None
            
            # 1. Intentar por URL exacta (lo más seguro)
            if url_cfg and url_cfg in biblio_urls:
                link_obj = biblio_urls[url_cfg]
            
            # 2. Intentar por Nombre Normalizado (ignora símbolos/comas/espacios)
            if not link_obj and nombre_cfg_norm:
                link_obj = biblio_nombres_norm.get(nombre_cfg_norm)
            
            # 3. Intentar por coincidencia parcial (URLs cortadas en el config)
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

    # --- ESCRITURA ---
    with open(path_out, 'w', encoding='utf-8') as f:
        f.write('<!DOCTYPE NETSCAPE-Bookmark-file-1>\n'
                '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">\n'
                '<TITLE>Bookmarks</TITLE>\n<H1>Bookmarks</H1>\n<DL><p>\n')
        escribir_dl(f, resultado_final)
        f.write('</DL><p>\n')

    print("\n" + "="*40)
    print("         INFORME DE ORGANIZACIÓN")
    print("="*40)
    print(f"Links procesados:           {stats['procesados']}")
    print(f"Links rescatados (OK):      {stats['organizados']}")
    print(f"Duplicados omitidos:        {stats['eliminados']}")
    print(f"No encontrados (Perdidos):  {stats['sin_config']}")
    print("-" * 40)
    print(f"Archivo: {os.path.basename(path_out)}")
    print("="*40)

if __name__ == "__main__":
    main()