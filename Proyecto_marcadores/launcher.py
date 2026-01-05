import os
import sys
import subprocess
from utils import validar_netscape, seleccionar_archivos_html

def mostrar_ayuda():
    print("\n" + "?"*45)
    print("   AYUDA RÁPIDA - MODO FUSIÓN")
    print("?"*45)
    print("1. Selecciona uno o VARIOS HTML (manten presionando Ctrl).")
    print("2. Generar borrador: Unirá todos los links en un solo TXT.")
    print("3. Organizador: Creará el HTML final sin duplicados.")
    print("4. Validador: Reporte de salud de todos los archivos.")
    print("?"*45 + "\n")

def menu():
    lista_paths = [] # Ahora manejamos una lista de archivos
    
    while True:
        herramientas = {
            "generador": os.path.exists("GeneradorConfig.py"),
            "organizador": os.path.exists("OrganizadorBookmarks.py"),
            "validador": os.path.exists("ValidadorLinks.py")
        }

        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n" + "="*45)
        print("   GESTOR DE MARCADORES (MODO FUSIÓN)")
        print("="*45)
        
        # Mostrar archivos cargados
        if not lista_paths:
            print(" ARCHIVOS: Ninguno seleccionado")
        else:
            print(f" ARCHIVOS ({len(lista_paths)}):")
            for p in lista_paths:
                print(f"  > {os.path.basename(p)}")
        
        print("-" * 45)
        print("1. Seleccionar archivos HTML (Soporta múltiples)")
        
        status_gen = "[OK]" if herramientas["generador"] else "[NO DISPONIBLE]"
        print(f"2. Generar borrador unificado {status_gen}")
        
        status_org = "[OK]" if herramientas["organizador"] else "[NO DISPONIBLE]"
        print(f"3. Ejecutar Organizador Final {status_org}")

        status_val = "[OK]" if herramientas["validador"] else "[NO DISPONIBLE]"
        print(f"4. Solo Validar Links (Reporte global) {status_val}")
        
        print("5. Ayuda")
        print("6. Salir")
        
        op = input("\nSelecciona (1-6): ")
        
        if op == "1":
            # Usamos la ventana de selección múltiple de utils.py
            nuevas_rutas = seleccionar_archivos_html()
            if nuevas_rutas:
                # Validamos que todos sean formato Netscape
                validos = []
                for r in nuevas_rutas:
                    es_valido, msg = validar_netscape(r)
                    if es_valido:
                        validos.append(r)
                    else:
                        print(f"\n⚠️ Saltando {os.path.basename(r)}: {msg}")
                
                lista_paths = validos
                print(f"\n✅ {len(lista_paths)} archivos cargados.")
            input("\nPresiona Enter...")

        elif op == "2":
            if herramientas["generador"] and lista_paths:
                import GeneradorConfig
                # Adaptamos para que reciba la lista completa
                try:
                    GeneradorConfig.main(lista_paths)
                except KeyboardInterrupt:
                    # Esto atrapa el Ctrl+C y evita que el programa falle
                    print("\n\n [!] Operación cancelada por el usuario. Volviendo al menú...")
                except Exception as e:
                    # Esto atrapa cualquier otro error inesperado para que no se cierre el Launcher
                    print(f"\n❌ Error crítico en el generador: {e}")
            elif not herramientas["generador"]: 
                print("\n❌ Script no encontrado.")
            else: 
                print("\n⚠️ Selecciona al menos un HTML primero.")
            
            input("\nPresiona Enter para continuar...")

        elif op == "3":
            if herramientas["organizador"] and lista_paths:
                carpeta_html = os.path.dirname(os.path.abspath(lista_paths[0]))
                
                # Buscamos el config (ya sea el original o el generado)
                ruta_final = os.path.join(carpeta_html, "config.txt")
                ruta_generada = os.path.join(carpeta_html, "config_GENERADO.txt")
                
                if not os.path.exists(ruta_final) and os.path.exists(ruta_generada):
                    os.rename(ruta_generada, ruta_final)

                if os.path.exists(ruta_final):
                    directorio_original = os.getcwd()
                    try:
                        # 1. Cambiamos a la carpeta del HTML
                        os.chdir(carpeta_html)
                        
                        # 2. Importación segura
                        import importlib
                        import OrganizadorBookmarks
                        importlib.reload(OrganizadorBookmarks) # Asegura que tome cambios
                        
                        # 3. Llamada inyectando el primer HTML de la lista
                        print(f"\n🚀 Iniciando organización de: {os.path.basename(lista_paths[0])}")
                        OrganizadorBookmarks.main(lista_paths[0])
                        
                    except Exception as e:
                        print(f"\n❌ Error durante la ejecución: {e}")
                    finally:
                        os.chdir(directorio_original)
                else:
                    print(f"\n⚠️ No se encontró 'config.txt' en {carpeta_html}")
            else:
                print("\n⚠️ Selecciona archivos (Opción 1) y asegúrate de tener el script.")
            input("\nPresiona Enter para continuar...")

        elif op == "4":
            if herramientas["validador"]:
                import ValidadorLinks
                print("\n" + "-"*40)
                print("   MODO VALIDADOR GLOBAL")
                print("-"*40)
                print("1. Validar TODOS los links de los archivos cargados")
                print("2. Validar UN SOLO LINK manualmente")
                print("3. Volver")
                sub_op = input("\nSelecciona (1-3): ")

                if sub_op == "1":
                    if lista_paths:
                        try:
                            from GeneradorConfig import obtener_lista_para_validar
                            from bs4 import BeautifulSoup
                            
                            lista_total = []
                            print("\n📖 Extrayendo links de todos los archivos...")
                            for p in lista_paths:
                                with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                                    soup = BeautifulSoup(f, 'html.parser')
                                    lista_total.extend(obtener_lista_para_validar(soup))
                            
                            lista_unica = list({v['url']:v for v in lista_total}.values())
                            print(f"\n📦 Total de links únicos a validar: {len(lista_unica)}")

                            print("\n1. Modo Paciente | 2. Modo Turbo")
                            m = input("\nModo: ")
                            
                            resultados = []
                            # Las siguientes líneas son las que más tardan:
                            if m == '2': 
                                resultados = ValidadorLinks.validar_lista_modo_turbo(lista_unica)
                            elif m == '1': 
                                resultados = ValidadorLinks.validar_lista_modo_paciente(lista_unica)
                            
                            if resultados:
                                ruta_reporte = os.path.join(os.path.dirname(lista_paths[0]), "REPORTE_GLOBAL.txt")
                                with open(ruta_reporte, "w", encoding="utf-8") as f:
                                    f.write("REPORTE GLOBAL DE VALIDACIÓN\n")
                                    f.write(f"Archivos analizados: {len(lista_paths)}\n")
                                    f.write("="*60 + "\n\n")
                                    for res in resultados:
                                        f.write(f"[{res['estado']}] {res['nombre']} -> {res['url']}\n")
                                print(f"\n📄 Reporte generado en: {ruta_reporte}")

                        except KeyboardInterrupt:
                            print("\n\n [!] Validación masiva cancelada por el usuario. No se guardó el reporte.")
                        except Exception as e:
                            print(f"\n❌ Error durante la validación: {e}")
                    else:
                        print("\n⚠️ Selecciona archivos primero.")
                
                elif sub_op == "2":
                    url_manual = input("URL a validar: ").strip()
                    if url_manual:
                        try:
                            res = ValidadorLinks.validar_un_link({'nombre': 'Manual', 'url': url_manual})
                            print(f"\nRESULTADO: {res['estado']} | URL: {res['url']}")
                        except KeyboardInterrupt:
                            print("\n [!] Cancelado.")

            input("\nPresiona Enter...")

        elif op == "5": 
            mostrar_ayuda()
            input("Presiona Enter...")
            
        elif op == "6": break

if __name__ == "__main__":
    menu()