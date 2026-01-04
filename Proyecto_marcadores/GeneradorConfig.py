import os
from bs4 import BeautifulSoup
from utils import gestionar_rutas, validar_netscape
import ValidadorLinks

def extraer_estructura(soup, resultados_validados=None):
    """
    Recorre los elementos y genera las líneas. 
    Mantiene el rastro de la carpeta actual para clasificar los errores.
    """
    lineas = []
    caidos_por_carpeta = {} 
    carpeta_actual = "Raíz"
    
    # Mapeamos los estados. Si no hubo validación, mapa_estados será un dict vacío.
    mapa_estados = {res['url']: res['estado'] for res in resultados_validados} if resultados_validados else {}

    elementos = soup.find_all(['h3', 'a'])
    
    for el in elementos:
        if el.name == 'h3':
            carpeta_actual = el.get_text().strip()
            lineas.append(f"C: {carpeta_actual}")
        elif el.name == 'a':
            url = el.get('href', '')
            # Limpiamos el nombre de comas para evitar conflictos en el futuro
            nombre = el.get_text().strip().replace(',', '')
            if not nombre: 
                nombre = url[:30]
            
            estado = mapa_estados.get(url, "ACTIVO")
            
            # --- MEJORA: Incluimos DUDOSO en la revisión ---
            if any(palabra in estado for palabra in ["CAIDO", "ERROR", "DUDOSO"]):
                if carpeta_actual not in caidos_por_carpeta:
                    caidos_por_carpeta[carpeta_actual] = []
                # Guardamos el formato con el pipe para que el Organizador sepa que es un caído
                caidos_por_carpeta[carpeta_actual].append(f"    K: {nombre} | {estado} | {url}")
            else:
                lineas.append(f"    K: {nombre}")

    # --- SECCIÓN DE REVISIÓN ORGANIZADA ---
    if caidos_por_carpeta:
        lineas.append("\n" + "#" * 45)
        lineas.append("C: REVISAR - LINKS CAIDOS O CON DUDAS")
        lineas.append("#" * 45)
        
        for carpeta_origen, links in caidos_por_carpeta.items():
            lineas.append(f"  C: Origen - {carpeta_origen}")
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

def main(path_html_directo=None):
    if path_html_directo:
        path_in = path_html_directo
        base_dir = os.path.dirname(os.path.abspath(path_in))
        path_conf = os.path.join(base_dir, "config_GENERADO.txt")
        print(f"\n⏳ Generando configuración para: {os.path.basename(path_in)}")
    else:
        path_in, path_conf, _ = gestionar_rutas("generador")
    
    if not path_in or not os.path.exists(path_in):
        print(f"\n❌ No se encontró el archivo de entrada en: {path_in}")
        return
    
    try:
        # Usamos errors='ignore' para evitar que caracteres raros rompan la lectura
        with open(path_in, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        dl_principal = soup.find('dl') or soup.find('DL')

        if not dl_principal:
            print("\n❌ No se encontró estructura de marcadores (falta etiqueta DL).")
            return

        resultados = None
        respuesta = input("\n¿Deseas validar si los links están caídos? (S/N): ").lower()
        
        if respuesta == 's':
            lista_preparada = obtener_lista_para_validar(dl_principal)
            print(f"📦 Total de links a verificar: {len(lista_preparada)}")
            print("\n1. Modo Paciente (Barra gráfica)")
            print("2. Modo Turbo (Rápido)")
            modo = input("\nSelecciona modo (1/2): ")
            
            if modo == '2':
                resultados = ValidadorLinks.validar_lista_modo_turbo(lista_preparada)
            else:
                resultados = ValidadorLinks.validar_lista_modo_paciente(lista_preparada)

        print(f"\n⏳ Analizando estructura y guardando borrador...")
        
        estructura = extraer_estructura(dl_principal, resultados)
        
        if not estructura:
            print("\n⚠️ No se pudieron extraer marcadores del archivo.")
            return

        with open(path_conf, 'w', encoding='utf-8') as f:
            f.write("# ARCHIVO DE CONFIGURACIÓN GENERADO\n")
            f.write("# Instrucciones: Edita las carpetas (C:) y nombres (K:).\n")
            f.write("# Luego renombra este archivo a 'config.txt' para el Organizador.\n\n")
            f.write("\n".join(estructura))
        
        print(f"\n✅ ¡Borrador creado con éxito!")
        print(f"📂 Ubicación: {path_conf}")
        print("\n👉 Siguiente paso: Revisa el .txt, elimina lo que no quieras y ejecuta el Organizador.")

    except Exception as e:
        print(f"\n❌ Error crítico en el Generador: {e}")

if __name__ == "__main__":
    main()