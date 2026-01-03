import os

def validar_netscape(path):
    """Verifica existencia y formato del archivo."""
    if not os.path.exists(path):
        return False, "❌ Error: El archivo no existe."
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            primera_linea = f.readline()
            if "NETSCAPE-Bookmark-file-1" not in primera_linea:
                return False, "❌ Error: No es un archivo de marcadores válido."
    except Exception as e:
        return False, f"❌ Error al leer: {e}"
    return True, "OK"

def gestionar_rutas(tipo_herramienta):
    """
    Gestiona la entrada y salida de archivos para:
    - 'organizador': In(HTML), In(Config), Out(HTML)
    - 'generador': In(HTML), Out(Config)
    """
    print(f"\n--- MÓDULO: {tipo_herramienta.upper()} ---")
    
    # 1. Entrada HTML (Común para ambos)
    path_in = input("[1] Ruta del archivo marcadores .html: ").strip('"').strip("'")
    valido, msg = validar_netscape(path_in)
    if not valido:
        print(msg)
        return None, None, None

    # Directorio base para sugerencias
    base_dir = os.path.dirname(os.path.abspath(path_in))

    # 2. Gestión del Config (Input para organizador / Output para generador)
    nombre_config = "config.txt" if tipo_herramienta == "organizador" else "config_GENERADO.txt"
    label_config = "entrada" if tipo_herramienta == "organizador" else "salida"
    
    print(f"[2] Ruta de {label_config} del {nombre_config}:")
    print(f"    (Presiona ENTER para: {os.path.join(base_dir, nombre_config)})")
    
    path_conf_raw = input(" RUTA > ").strip('"').strip("'")
    path_conf = path_conf_raw if path_conf_raw else os.path.join(base_dir, nombre_config)

    # 3. Gestión de Salida HTML (Solo para el organizador)
    path_out = None
    if tipo_herramienta == "organizador":
        print(f"[3] Ruta de salida para el nuevo HTML:")
        print(f"    (Presiona ENTER para: {os.path.join(base_dir, 'favoritos_REORGANIZADOS.html')})")
        
        path_out_raw = input(" RUTA > ").strip('"').strip("'")
        path_out = path_out_raw if path_out_raw else os.path.join(base_dir, "favoritos_REORGANIZADOS.html")

    return path_in, path_conf, path_out