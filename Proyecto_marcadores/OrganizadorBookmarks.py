import os
from bs4 import BeautifulSoup
from utils import gestionar_rutas

def parse_config(config_path):
    tree = []
    stack = []
    if not os.path.exists(config_path): return None
    with open(config_path, 'r', encoding='utf-8') as f:
        for line in f:
            line_content = line.strip()
            if not line_content or line_content.startswith("#"): continue
            indent = len(line) - len(line.lstrip())
            level = indent // 4
            item_type, name = line_content[:2], line_content[2:].strip()
            item = {'type': item_type, 'name': name, 'children': [], 'keywords': []}
            if item_type == 'K:':
                if stack: stack[-1]['keywords'].extend([k.strip().lower() for k in name.split(',')])
            else:
                if level == 0:
                    tree.append(item)
                    stack = [item]
                else:
                    stack = stack[:level]
                    if stack:
                        stack[-1]['children'].append(item)
                        stack.append(item)
    return tree

def clasificar_link(link_node, tree):
    texto = (link_node.text + " " + link_node.get('href', '')).lower()
    def buscar(nodos):
        for nodo in nodos:
            sub = buscar(nodo['children'])
            if sub: return [nodo['name']] + sub
            if any(k in texto for k in nodo['keywords'] if k): return [nodo['name']]
        return None
    return buscar(tree)

def escribir_dl(f, estructura, nivel=1):
    espacio = "    " * nivel
    for nombre, contenido in estructura.items():
        f.write(f'{espacio}<DT><H3>{nombre}</H3>\n{espacio}<DL><p>\n')
        if isinstance(contenido, dict): escribir_dl(f, contenido, nivel + 1)
        elif isinstance(contenido, list):
            for link in contenido: f.write(f'{"    " * (nivel+1)}{str(link)}\n')
        f.write(f'{espacio}</DL><p>\n')

def main(path_html_directo=None):
    if path_html_directo:
        path_in = path_html_directo
        base_dir = os.path.dirname(os.path.abspath(path_in))
        path_config = os.path.join(base_dir, "config.txt")
        path_out = os.path.join(base_dir, "favoritos_REORGANIZADOS.html")
    else:
        path_in, path_config, path_out = gestionar_rutas("organizador")

    if not path_in or not os.path.exists(path_config):
        print(f"❌ Error: No se encuentra el archivo config.txt en {path_config}")
        return

    tree = parse_config(path_config)
    with open(path_in, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    vistos, resultado = set(), {}
    stats = {"procesados": 0, "eliminados": 0, "clasificados": 0, "sin_clase": 0}

    for link in soup.find_all('a'):
        url = link.get('href')
        stats["procesados"] += 1
        if url in vistos:
            stats["eliminados"] += 1
            continue
        vistos.add(url)
        
        ruta = clasificar_link(link, tree)
        if ruta:
            stats["clasificados"] += 1
        else:
            ruta = ["00. Sin Clasificar"]
            stats["sin_clase"] += 1
        
        actual = resultado
        for i, carpeta in enumerate(ruta):
            if carpeta not in actual: actual[carpeta] = {} if i < len(ruta)-1 else []
            actual = actual[carpeta]
        if isinstance(actual, list): actual.append(link)

    with open(path_out, 'w', encoding='utf-8') as f:
        f.write('<!DOCTYPE NETSCAPE-Bookmark-file-1>\n<TITLE>Bookmarks</TITLE>\n<H1>Bookmarks</H1>\n<DL><p>\n')
        escribir_dl(f, resultado)
        f.write('</DL><p>\n')

    # --- BLOQUE DEL INFORME REINSTALADO ---
    print("\n" + "="*40)
    print("         INFORME DE PROCESAMIENTO")
    print("="*40)
    print(f"Total links encontrados:  {stats['procesados']}")
    print(f"Duplicados eliminados:    {stats['eliminados']}")
    print(f"Links clasificados:       {stats['clasificados']}")
    print(f"Links sin clasificar:     {stats['sin_clase']}")
    print("-" * 40)
    print(f"Archivo final: {os.path.basename(path_out)}")
    print("="*40)

if __name__ == "__main__":
    main()