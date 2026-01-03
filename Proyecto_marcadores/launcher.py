import os
from utils import validar_netscape
import GeneradorConfig
import OrganizadorBookmarks

def mostrar_ayuda():
    print("\n" + "?"*45)
    print("   AYUDA RÁPIDA")
    print("?"*45)
    print("1. Carga tu archivo HTML primero.")
    print("2. Genera el borrador para ver tus carpetas.")
    print("3. Edita 'config_GENERADO.txt' y cámbiale")
    print("   el nombre a 'config.txt'.")
    print("4. Ejecuta el Organizador para terminar.")
    print("?"*45 + "\n")

def menu():
    path_html = None
    while True:
        print("\n" + "="*40)
        print("   GESTOR DE MARCADORES")
        print("="*40)
        print(f" ARCHIVO: {os.path.basename(path_html) if path_html else 'Ninguno'}")
        print("-"*40)
        print("1. Seleccionar archivo HTML")
        print("2. Generar borrador de configuración")
        print("3. Ejecutar Organizador (Usar config.txt)")
        print("4. Ayuda")
        print("5. Salir")
        
        op = input("\nSelecciona (1-5): ")
        
        if op == "1":
            path = input("Arrastra el HTML aquí: ").strip('"').strip("'")
            valido, msg = validar_netscape(path)
            if valido:
                path_html = path
                print("✅ Archivo cargado.")
            else: print(msg)
        elif op == "2":
            if path_html: GeneradorConfig.main(path_html)
            else: print("⚠️ Carga un HTML primero.")
        elif op == "3":
            if path_html: OrganizadorBookmarks.main(path_html)
            else: print("⚠️ Carga un HTML primero.")
        elif op == "4": mostrar_ayuda()
        elif op == "5": break
        else: print("❌ Opción no válida.")

if __name__ == "__main__":
    menu()