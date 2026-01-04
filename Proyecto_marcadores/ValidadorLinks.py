import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def validar_un_link(marcador):
    """Versión optimizada para evitar falsos 400/403 en sitios como WhatsApp."""
    url_original = marcador.get('url', '').strip()
    
    # Headers extendidos para máxima compatibilidad
    headers_pro = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Referer': 'https://www.google.com/',
        'Connection': 'keep-alive'
    }

    protocolos = [url_original] if url_original.startswith(('http://', 'https://')) else [f"https://{url_original}", f"http://{url_original}"]

    ultimo_error = ""
    for url in protocolos:
        try:
            # Intento 1: HEAD (Rápido)
            res = requests.head(url, timeout=8, headers=headers_pro, allow_redirects=True)
            
            # Intento 2: Si el HEAD falla o da error de cliente (400, 403, 405)
            if res.status_code >= 400:
                res = requests.get(url, timeout=8, headers=headers_pro, stream=True, allow_redirects=True)
            
            if res.status_code < 400:
                return {**marcador, "url": url, "estado": "ACTIVO"}
            
            # --- AFINAMIENTO DE ERRORES ---
            if res.status_code in [400, 403, 405]:
                # Si llegamos aquí, el servidor respondió, por lo tanto el link NO está caído.
                # Está "Protegido" contra bots.
                return {**marcador, "url": url, "estado": "ACTIVO (Protegido)"}
            else:
                ultimo_error = f"CAIDO ({res.status_code})"
                
        except Exception:
            ultimo_error = "ERROR (Timeout/DNS)"
            continue

    return {**marcador, "estado": ultimo_error}

def validar_lista_modo_paciente(lista_marcadores):
    """Opción A: Uno por uno con barra de progreso gráfica y manejo de interrupción."""
    resultados = []
    total = len(lista_marcadores)
    ancho_barra = 30
    
    print("\nℹ️  Presiona Ctrl+C para detener y guardar lo procesado.\n")
    
    try:
        for i, m in enumerate(lista_marcadores, 1):
            porcentaje = (i / total) * 100
            bloques = int((i / total) * ancho_barra)
            barra = "█" * bloques + "-" * (ancho_barra - bloques)
            
            print(f"\r[{barra}] {porcentaje:.1f}% ({i}/{total}) | Chequeando: {m['nombre'][:25]}...          ", end="")
            resultados.append(validar_un_link(m))
            
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Proceso detenido por el usuario.")
    
    # Rellenar los faltantes si hubo interrupción
    if len(resultados) < total:
        urls_hechas = {r['url'] for r in resultados}
        for m in lista_marcadores:
            if m['url'] not in urls_hechas:
                resultados.append({**m, "estado": "SIN VALIDAR"})

    print("\n✅ Finalizado.")
    return resultados

def validar_lista_modo_turbo(lista_marcadores):
    """Opción B: Muchos a la vez con as_completed y cancelación instantánea."""
    total = len(lista_marcadores)
    resultados = []
    completados = 0
    ancho_barra = 30

    print(f"\n🚀 Iniciando validación turbo de {total} links...")
    print("ℹ️  Modo Turbo: Procesando en paralelo (10 hilos).\n")

    executor = ThreadPoolExecutor(max_workers=10)
    futuro_a_marcador = {executor.submit(validar_un_link, m): m for m in lista_marcadores}
    
    try:
        for futuro in as_completed(futuro_a_marcador):
            resultado = futuro.result()
            resultados.append(resultado)
            completados += 1
            
            porcentaje = (completados / total) * 100
            bloques = int((completados / total) * ancho_barra)
            barra = "█" * bloques + "-" * (ancho_barra - bloques)
            print(f"\r⚡ TURBO [{barra}] {porcentaje:.1f}% ({completados}/{total})", end="")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupción detectada. Cancelando tareas pendientes...")
        executor.shutdown(wait=False, cancel_futures=True)
        
        urls_procesadas = {r['url'] for r in resultados}
        for m in lista_marcadores:
            if m['url'] not in urls_procesadas:
                resultados.append({**m, "estado": "SIN VALIDAR"})
    else:
        executor.shutdown(wait=True)

    print("\n\n✅ Finalizado.")
    return resultados