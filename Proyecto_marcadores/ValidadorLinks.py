import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def validar_un_link(marcador):
    """Prueba una URL intentando HTTPS y luego HTTP si es necesario."""
    url_original = marcador.get('url', '').strip()
    
    # Lista de protocolos a probar
    protocolos_a_probar = []
    if url_original.startswith(('http://', 'https://')):
        protocolos_a_probar = [url_original]
    else:
        # Si no tiene protocolo, probamos ambos empezando por el seguro
        protocolos_a_probar = [f"https://{url_original}", f"http://{url_original}"]

    ultimo_error = ""
    for url in protocolos_a_probar:
        try:
            # Usamos un timeout corto para no esperar de más
            response = requests.head(url, timeout=5, allow_redirects=True)
            if response.status_code >= 400:
                response = requests.get(url, timeout=5, stream=True)
            
            if response.status_code < 400:
                # Si tuvo éxito, devolvemos el estado y la URL que funcionó
                return {**marcador, "url": url, "estado": "ACTIVO"}
            else:
                ultimo_error = f"CAIDO ({response.status_code})"
        except Exception as e:
            ultimo_error = "ERROR (No responde)"
            continue # Probamos el siguiente protocolo si existe

    return {**marcador, "estado": ultimo_error}

def validar_lista_modo_paciente(lista_marcadores):
    """Opción A: Uno por uno con barra de progreso gráfica."""
    resultados = []
    total = len(lista_marcadores)
    ancho_barra = 30 # Tamaño de la barra en caracteres
    
    print("\nℹ️  Presiona Ctrl+C para detener y guardar lo procesado.\n")
    
    try:
        for i, m in enumerate(lista_marcadores, 1):
            # Cálculos de progreso
            porcentaje = (i / total) * 100
            bloques = int((i / total) * ancho_barra)
            barra = "█" * bloques + "-" * (ancho_barra - bloques)
            
            # Línea de estado: Barra + Porcentaje + Contador + Nombre
            # El \r al principio y el end="" hacen que la línea se sobrescriba
            print(f"\r[{barra}] {porcentaje:.1f}% ({i}/{total}) | Chequeando: {m['nombre'][:25]}...          ", end="")
            
            resultados.append(validar_un_link(m))
            
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Proceso cancelado por el usuario.")
        print(f"\n✅ Se guardaron {len(resultados)} links validados.")
    
    # Rellenar los no procesados para no perderlos
    if len(resultados) < total:
        procesados_urls = {r['url'] for r in resultados}
        for m in lista_marcadores:
            if m['url'] not in procesados_urls:
                resultados.append({**m, "estado": "SIN VALIDAR"})

    print("\n\n✅ Finalizado.")
    return resultados

def validar_lista_modo_turbo(lista_marcadores):
    """Opción B: Muchos a la vez con contador de progreso dinámico."""
    total = len(lista_marcadores)
    resultados = []
    completados = 0
    ancho_barra = 30

    print(f"\n🚀 Iniciando validación turbo de {total} links...")
    print("\nℹ️  Modo Turbo: Procesando en paralelo (10 hilos).\n")

     # Usamos el context manager pero con un truco para cancelar
    executor = ThreadPoolExecutor(max_workers=10)
    # Creamos un diccionario para rastrear qué marcador pertenece a qué futuro
    futuro_a_marcador = {executor.submit(validar_un_link, m): m for m in lista_marcadores}
    
    try:
        # as_completed nos da los resultados a medida que van saliendo
        for futuro in as_completed(futuro_a_marcador):
            resultado = futuro.result()
            resultados.append(resultado)
            completados += 1
            
            porcentaje = (completados / total) * 100
            bloques = int((completados / total) * ancho_barra)
            barra = "█" * bloques + "-" * (ancho_barra - bloques)
            print(f"\r⚡ TURBO [{barra}] {porcentaje:.1f}% ({completados}/{total})", end="")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupción detectada. Cancelando tareas pendientes inmediatamente...")
        # wait=False es la clave: no espera a que los hilos terminen
        executor.shutdown(wait=False, cancel_futures=True)
        
        # Identificamos qué URLs procesamos para marcar el resto como SIN VALIDAR
        urls_procesadas = {r['url'] for r in resultados}
        for m in lista_marcadores:
            if m['url'] not in urls_procesadas:
                resultados.append({**m, "estado": "SIN VALIDAR"})
    else:
        # Si todo termina normal, cerramos limpio
        executor.shutdown(wait=True)

    print("\n\n✅ Finalizado.")
    return resultados