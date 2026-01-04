import os
import sys
import subprocess
from utils import validar_netscape

def mostrar_ayuda():
    print("\n" + "?"*45)
    print("   AYUDA RÁPIDA")
    print("?"*45)
    print("1. Carga tu archivo HTML primero.")
    print("2. Genera el borrador para ver tus carpetas.")
    print("3. Edita 'config_GENERADO.txt' y renómbralo a 'config.txt'.")
    print("4. El validador se puede usar solo o dentro del generador.")
    print("5. Ejecuta el Organizador para terminar.")
    print("?"*45 + "\n")

def menu():
    path_html = None
    
    while True:
        # Detectamos qué herramientas están presentes
        herramientas = {
            "generador": os.path.exists("GeneradorConfig.py"),
            "organizador": os.path.exists("OrganizadorBookmarks.py"),
            "validador": os.path.exists("ValidadorLinks.py")
        }

        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n" + "="*40)
        print("   GESTOR DE MARCADORES DINÁMICO")
        print("="*40)
        print(f" ARCHIVO: {os.path.basename(path_html) if path_html else 'Ninguno'}")
        print("-"*40)
        
        print("1. Seleccionar archivo HTML")
        
        status_gen = "[OK]" if herramientas["generador"] else "[NO DISPONIBLE]"
        print(f"2. Generar borrador de configuración {status_gen}")
        
        status_org = "[OK]" if herramientas["organizador"] else "[NO DISPONIBLE]"
        print(f"3. Ejecutar Organizador (Usar config.txt) {status_org}")

        status_val = "[OK]" if herramientas["validador"] else "[NO DISPONIBLE]"
        print(f"4. Solo Validar Links (Chequeo rápido) {status_val}")
        
        print("5. Ayuda")
        print("6. Salir")
        
        op = input("\nSelecciona (1-6): ")
        
        if op == "1":
            path = input("\nArrastra el HTML aquí: ").strip('"').strip("'")
            valido, msg = validar_netscape(path)
            if valido:
                path_html = path
                print("\n✅ Archivo cargado.")
            else: 
                print(msg)
            input("\nPresiona Enter...")

        elif op == "2":
            if herramientas["generador"] and path_html:
                import GeneradorConfig
                GeneradorConfig.main(path_html)
            elif not herramientas["generador"]: print("\n❌ Script no encontrado.")
            else: print("\n⚠️ Carga un HTML primero.")
            input("\nPresiona Enter...")

        elif op == "3":
            if herramientas["organizador"] and path_html:
                if os.path.exists("config.txt"):
                    import OrganizadorBookmarks
                    OrganizadorBookmarks.main(path_html)
                else: print("\n⚠️ Falta 'config.txt'.")
            elif not herramientas["organizador"]: print("\n❌ Script no encontrado.")
            else: print("\n⚠️ Carga un HTML primero.")
            input("\nPresiona Enter...")

        elif op == "4":
            if herramientas["validador"]:
                import ValidadorLinks
                print("\n" + "-"*40)
                print("   MODO VALIDADOR")
                print("-"*40)
                print("1. Validar TODOS los links del HTML cargado")
                print("2. Validar UN SOLO LINK manualmente")
                print("3. Volver al menú principal")
                sub_op = input("\nSelecciona (1-3): ")

                if sub_op == "1":
                    if path_html:
                        try:
                            from GeneradorConfig import obtener_lista_para_validar
                            from bs4 import BeautifulSoup
                            
                            with open(path_html, 'r', encoding='utf-8', errors='ignore') as f:
                                soup = BeautifulSoup(f, 'html.parser')
                            
                            lista = obtener_lista_para_validar(soup)
                            print("\n1. Modo Paciente (con barra gráfica) | 2. Modo Turbo")
                            m = input("\nModo: ")
                            
                            resultados = []
                            if m == '2': 
                                resultados = ValidadorLinks.validar_lista_modo_turbo(lista)
                            elif m == '1': 
                                resultados = ValidadorLinks.validar_lista_modo_paciente(lista)
                            else:
                                print("\n❌ Modo de validación no válido.")
                                continue

                            if resultados:
                                # Determinamos la carpeta del HTML para guardar el reporte allí
                                carpeta_html = os.path.dirname(os.path.abspath(path_html))
                                ruta_reporte = os.path.join(carpeta_html, "REPORTE_VALIDACION.txt")
                                
                                with open(ruta_reporte, "w", encoding="utf-8") as f:
                                    f.write(f"REPORTE DE VALIDACIÓN - {os.path.basename(path_html)}\n")
                                    f.write("="*60 + "\n\n")
                                    for res in resultados:
                                        f.write(f"[{res['estado']}] {res['nombre']} -> {res['url']}\n")
                                
                                print(f"\n✅ Proceso terminado con éxito.")
                                print(f"\n📄 Reporte generado en: {ruta_reporte}")

                        except KeyboardInterrupt:
                            print("\n🛑 Validación interrumpida. Regresando al menú principal...")
                    else:
                        print("\n⚠️ Carga un HTML primero para esta opción.")
                
                elif sub_op == "2":
                    url_manual = input("Pega la URL a validar: ").strip()
                    if url_manual:
                        print(f"\n🔍 Verificando conexión...")
                        # El validador ahora se encarga de probar http/https
                        res = ValidadorLinks.validar_un_link({'nombre': 'Manual', 'url': url_manual})
                        
                        # Mostramos qué URL terminó funcionando
                        print(f"\nURL final: {res['url']}")
                        print(f"RESULTADO: {res['estado']}")
                    else:
                        print("\n❌ URL vacía.")
                
                elif sub_op == "3":
                    continue  # Salta el resto del código y vuelve al inicio del 'while' del menú

                else:
                    print("\n❌ Opción de sub-menú no válida.")
            else:
                print("\n❌ Script 'ValidadorLinks.py' no encontrado.")
            input("\nPresiona Enter para continuar...")

        elif op == "5": 
            mostrar_ayuda()
            input("Presiona Enter...")
            
        elif op == "6": break
        else: 
            print("\n❌ Opción no válida.")
            input("\nPresiona Enter...")

if __name__ == "__main__":
    menu()