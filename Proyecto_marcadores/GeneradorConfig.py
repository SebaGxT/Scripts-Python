import os
from bs4 import BeautifulSoup
from utils import gestionar_rutas, validar_netscape
import ValidadorLinks

def extraer_estructura(soup, resultados_validados=None):
    """
    Clasifica links en: Activos, Caídos (Borrar) y Bloqueados (Revisar).
    """
    lineas = []
    caidos_por_carpeta = {}      
    bloqueados_por_carpeta = {}   
    carpeta_actual = "Raíz"
    
    # Mapeo de estados para consulta rápida
    mapa_estados = {res['url']: res['estado'] for res in resultados_validados} if resultados_validados else {}
    elementos = soup.find_all(['h3', 'a'])
    
    for el in elementos:
        if el.name == 'h3':
            carpeta_actual = el.get_text().strip()
            lineas.append(f"C: {carpeta_actual}")
        elif el.name == 'a':
            url = el.get('href', '')
            nombre = el.get_text().strip().replace(',', '') or url[:30]
            estado = mapa_estados.get(url, "ACTIVO")
            
            # Clasificación según el estado del validador
            if any(p in estado for p in ["CAIDO", "ERROR"]):
                if carpeta_actual not in caidos_por_carpeta: 
                    caidos_por_carpeta[carpeta_actual] = []
                caidos_por_carpeta[carpeta_actual].append(f"    K: {nombre} | {estado} | {url}")
            
            elif "Protegido" in estado or "DUDOSO" in estado:
                if carpeta_actual not in bloqueados_por_carpeta: 
                    bloqueados_por_carpeta[carpeta_actual] = []
                bloqueados_por_carpeta[carpeta_actual].append(f"    K: {nombre} | {estado} | {url}")
            
            else:
                lineas.append(f"    K: {nombre}")

    # --- SECCIÓN A: LINKS CAÍDOS (Para Borrar) ---
    if caidos_por_carpeta:
        lineas.append("\n" + "!"*45)
        lineas.append("C: REVISAR - LINKS CAIDOS (PROBABLE BORRADO)")
        lineas.append("!"*45)
        for origen, links in caidos_por_carpeta.items():
            lineas.append(f"  C: Origen Caído - {origen}")
            lineas.extend(links)

    # --- SECCIÓN B: LINKS BLOQUEADOS (Probablemente Activos) ---
    if bloqueados_por_carpeta:
        lineas.append("\n" + "?"*45)
        lineas.append("C: REVISAR - LINKS BLOQUEADOS (VERIFICAR MANUAL)")
        lineas.append("?"*45)
        for origen, links in bloqueados_por_carpeta.items():
            lineas.append(f"  C: Origen Bloqueado - {origen}")
            lineas.extend(links)
        
    return lineas

def obtener_lista_para_validar(soup):
    """Extrae una lista de diccionarios para el validador."""
    marcadores = []
    for a in soup.find_all('a'):
        marcadores.append({
            'nombre': a.get_text().strip() or a.get('href', '')[:30],
            'url': a.get('href', '')
        })
    return marcadores

def main(input_data=None):
    """
    input_data puede ser una ruta (str) o una lista de rutas (list).
    """
    # Convertimos a lista si viene un solo archivo
    rutas_html = [input_data] if isinstance(input_data, str) else input_data
    
    if not rutas_html:
        print("\n❌ No hay archivos para procesar.")
        return

    todas_las_sopas = []
    print(f"\n📖 Cargando {len(rutas_html)} archivo(s) HTML...")
    
    for r in rutas_html:
        try:
            with open(r, 'r', encoding='utf-8', errors='ignore') as f:
                todas_las_sopas.append({
                    'nombre': os.path.basename(r),
                    'soup': BeautifulSoup(f, 'html.parser')
                })
        except Exception as e:
            print(f"\n⚠️ Error leyendo {r}: {e}")

    # --- LÓGICA DE VALIDACIÓN ---
    resultados = None
    respuesta = input("\n¿Deseas validar si los links están caídos? (S/N): ").lower()
    
    if respuesta == 's':
        lista_preparada = []
        for item in todas_las_sopas:
            lista_preparada.extend(obtener_lista_para_validar(item['soup']))
        
        # Eliminamos duplicados por URL antes de validar para ir más rápido
        lista_unica = list({m['url']: m for m in lista_preparada}.values())
        
        print(f"\n📦 Total de links únicos a verificar: {len(lista_unica)}")
        print("\n1. Modo Paciente (Barra gráfica) | 2. Modo Turbo (Rápido)")
        modo = input("\nSelecciona modo (1/2): ")
        
        if modo == '2':
            resultados = ValidadorLinks.validar_lista_modo_turbo(lista_unica)
        else:
            resultados = ValidadorLinks.validar_lista_modo_paciente(lista_unica)

    # --- GENERACIÓN DEL CONFIG.TXT ---
    print(f"\n⏳ Generando estructura unificada...")
    lineas_totales = [
        "# ARCHIVO DE CONFIGURACIÓN GENERADO",
        "# Instrucciones: Edita y renombra a 'config.txt' para el Organizador.",
        f"# Total de archivos fusionados: {len(todas_las_sopas)}\n"
    ]
    
    for item in todas_las_sopas:
        lineas_totales.append(f"\n{'='*45}")
        lineas_totales.append(f"# CONTENIDO DE: {item['nombre']}")
        lineas_totales.append(f"{'='*45}")
        lineas_totales.extend(extraer_estructura(item['soup'], resultados))

    # Guardamos donde esté el primer archivo seleccionado
    path_conf = os.path.join(os.path.dirname(os.path.abspath(rutas_html[0])), "config_GENERADO.txt")
    
    try:
        with open(path_conf, 'w', encoding='utf-8') as f:
            f.write("\n".join(lineas_totales))
        
        print(f"\n✅ ¡Proceso completado!")
        print(f"📂 Archivo borrador creado en: {path_conf}")
        print("\n👉 Próximo paso: Edita el archivo y luego ejecuta el Organizador.")
    except Exception as e:
        print(f"\n❌ Error al escribir el config: {e}")

if __name__ == "__main__":
    main()