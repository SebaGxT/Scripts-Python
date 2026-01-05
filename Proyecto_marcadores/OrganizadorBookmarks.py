import os
import re
from bs4 import BeautifulSoup
from utils import gestionar_rutas

def normalizar(texto):
    if not texto: return ""
    return re.sub(r'[^a-z0-9]', '', texto.lower())

def escribir_recursivo(f, nombre, contenido, nivel=1):
    """Escribe la estructura DL/DT respetando niveles y cierres."""
    indent = "    " * nivel
    f.write(f'{indent}<DT><H3>{nombre}</H3>\n')
    f.write(f'{indent}<DL><p>\n')
    
    # 1. Links de esta carpeta
    for link_obj in contenido["links"]:
        f.write(f'{indent}    <DT>{str(link_obj)}\n')
    
    # 2. Subcarpetas (Recursión)
    for sub_nombre, sub_contenido in contenido["subcarpetas"].items():
        escribir_recursivo(f, sub_nombre, sub_contenido, nivel + 1)
        
    f.write(f'{indent}</DL><p>\n')

def main(path_html_directo=None): # Corregido: Ahora acepta el argumento
    if path_html_directo:
        path_in = path_html_directo
        base_dir = os.path.dirname(os.path.abspath(path_in))
        path_config = os.path.join(base_dir, "config.txt")
        path_out = os.path.join(base_dir, "Favoritos_ORGANIZADOS.html")
    else:
        path_in, path_config, path_out = gestionar_rutas("organizador")

    if not path_in or not os.path.exists(path_config):
        print("❌ Error: No se encontraron los archivos necesarios.")
        return

    # 1. Cargar Biblioteca
    with open(path_in, 'r', encoding='utf-8', errors='ignore') as f:
        soup = BeautifulSoup(f, 'html.parser')
    biblio_urls = {a.get('href', ''): a for a in soup.find_all('a')}
    biblio_norm = {normalizar(a.get_text()): a for a in soup.find_all('a')}

    # 2. Construir Árbol mientras leemos el Config
    arbol = {}
    vistos = set()
    stats = {"procesados": 0, "organizados": 0, "eliminados": 0, "fail": 0}
    punto_insercion = {"links": [], "subcarpetas": {}}

    with open(path_config, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"): continue
            
            if line.startswith("C: "):
                nombre_raw = line[3:].strip()
                # Regla para agrupar revisiones
                if "Origen" in nombre_raw or "REVISAR" in nombre_raw:
                    ruta = ["REVISIÓN DE LINKS", nombre_raw]
                else:
                    ruta = [p.strip() for p in nombre_raw.split('/') if p.strip()]
                
                # Navegación profunda en el árbol
                nodo = arbol
                for p in ruta:
                    if p not in nodo:
                        nodo[p] = {"links": [], "subcarpetas": {}}
                    punto_insercion = nodo[p]
                    nodo = nodo[p]["subcarpetas"]
                
            elif line.startswith("K: "):
                stats["procesados"] += 1
                partes_k = [p.strip() for p in line[3:].split('|')]
                nombre_k = partes_k[0]
                url_k = partes_k[-1] if len(partes_k) > 1 else None
                
                link_obj = biblio_urls.get(url_k) or biblio_norm.get(normalizar(nombre_k))
                
                if link_obj:
                    url_final = link_obj.get('href')
                    if url_final not in vistos:
                        vistos.add(url_final)
                        punto_insercion["links"].append(link_obj)
                        stats["organizados"] += 1
                    else:
                        stats["eliminados"] += 1
                else:
                    stats["fail"] += 1

    # 3. Escribir HTML
    with open(path_out, 'w', encoding='utf-8') as f:
        f.write('<!DOCTYPE NETSCAPE-Bookmark-file-1>\n'
                '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">\n'
                '<TITLE>Bookmarks</TITLE>\n<H1>Bookmarks</H1>\n<DL><p>\n')
        
        for n_raiz, cont in arbol.items():
            escribir_recursivo(f, n_raiz, cont)
            
        f.write('</DL><p>\n')

    # --- INFORME ---
    print("\n" + "="*40)
    print("         INFORME DE ORGANIZACIÓN")
    print("="*40)
    print(f"Links procesados:           {stats['procesados']}")
    print(f"Links rescatados (OK):      {stats['organizados']}")
    print(f"Duplicados omitidos:        {stats['eliminados']}")
    print(f"No encontrados (Perdidos):  {stats['fail']}")
    print("-" * 40)
    print(f"Archivo: {os.path.basename(path_out)}")
    print("="*40)

if __name__ == "__main__":
    main()