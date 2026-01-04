import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# Definimos una identidad de navegador para evitar bloqueos 403 (Forbidden)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
}

def validar_un_link(marcador):
    """Prueba una URL intentando HTTPS y luego HTTP, usando headers de navegador."""
    url_original = marcador.get('url', '').strip()
    
    # Determinamos protocolos a probar
    if url_original.startswith(('http://', 'https://')):
        protocolos_a_probar = [url_original]
    else:
        protocolos_a_probar = [f"https://{url_original}", f"http://{url_original}"]

    ultimo_error = ""
    for url in protocolos_a_probar:
        try:
            # 1. Intentamos HEAD (más rápido) con Headers de navegador
            response = requests.head(url, timeout=7, headers=HEADERS, allow_redirects=True)
            
            # 2. Si falla (muchos sitios bloquean HEAD), intentamos GET
            if response.status_code >= 400:
                response = requests.get(url, timeout=7, headers=HEADERS, stream=True, allow_redirects=True)
            
            if response.status_code < 400:
                return {**marcador, "url": url, "estado": "ACTIVO"}
            
            # Si el error es 403, lo marcamos como Dudoso (el sitio está vivo pero bloquea bots)
            if response.status_code == 403:
                ultimo_error = "DUDOSO (403 - Protegido)"
            else:
                ultimo_error = f"CAIDO ({response.status_code})"
                
        except Exception:
            ultimo_error = "ERROR (No responde)"
            continue # Probar el siguiente protocolo

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