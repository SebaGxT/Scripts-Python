# 📑 Suite de Organización de Marcadores (Netscape Format)

Esta suite de herramientas en Python permite gestionar, limpiar y reorganizar archivos de favoritos exportados de cualquier navegador (**Chrome, Firefox, Brave, Edge**). Utiliza una arquitectura modular para garantizar la validación de archivos y la gestión inteligente de rutas.

## 🚀 Características Principales

* **Ingeniería Inversa:** Genera automáticamente un borrador de configuración basado en tus marcadores actuales.
* **Validación de Formato:** Verifica estrictamente el estándar `NETSCAPE-Bookmark-file-1`.
* **Eliminación de Duplicados:** Filtra URLs idénticas basándose en la dirección exacta.
* **Jerarquía Dinámica:** Soporta niveles infinitos de subcarpetas mediante indentación de 4 espacios.
* **Preservación de Metadatos:** Mantiene fechas de creación (`ADD_DATE`) e iconos (`ICON`) originales.
* **Informe Final:** Estadísticas detalladas sobre links procesados, clasificados y eliminados.

---

## 🛠️ Requisitos Previos

1.  **Python 3.x** instalado.
2.  Instalar la librería necesaria:
    ```bash
    pip install beautifulsoup4
    pip install typing-extensions beautifulsoup4
    ```

---

### 💡 Solución de problemas (Conflictos de Python)
Si recibes errores de "ModuleNotFoundError" teniendo instalado Python, se recomienda usar un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: .\venv\Scripts\activate
pip install beautifulsoup4 typing-extensions
python Launcher.py

---

## 📂 Estructura del Proyecto

Para que el sistema funcione correctamente, debes tener estos tres archivos en la misma carpeta:

1.  `launcher.py`: Inicializador principal del proyecto
2.  `utils.py`: El núcleo compartido que gestiona rutas y validaciones.
3.  `GeneradorConfig.py`: Herramienta para extraer tu estructura actual a un archivo de texto.
4.  `OrganizadorBookmarks.py`: Herramienta principal que crea el nuevo archivo HTML organizado.

## 🛠️ Estructura de Archivos Recomendada

Para que el **Launcher** funcione correctamente y los scripts puedan comunicarse entre sí, asegúrate de que tu carpeta de trabajo mantenga la siguiente estructura:

* 📁 **`Proyecto_Marcadores/`**
    * 📄 `Launcher.py` → **Archivo principal** (Ejecuta este para iniciar).
    * 📄 `utils.py` → Funciones compartidas de validación y rutas.
    * 📄 `GeneradorConfig.py` → Script para crear el borrador inicial.
    * 📄 `OrganizadorBookmarks.py` → Script para la limpieza y orden final.
    * 📄 `config.txt` → Tu archivo de reglas personalizado.
    * 📄 `tus_marcadores.html` → Tu archivo exportado desde Chrome/Edge/Firefox.

---

## 🚀 Centro de Control (`Launcher.py`)

Para facilitar el uso de la suite, hemos incluido un **Launcher** interactivo. Este archivo centraliza todas las funciones en un solo menú, permitiéndote gestionar tus marcadores sin necesidad de ejecutar scripts por separado o reingresar rutas constantemente.

### Ventajas del Launcher:
* **Memoria de Sesión:** Ingresas la ruta del archivo HTML una sola vez y el Launcher la "recuerda" para el Generador y el Organizador.
* **Interfaz Intuitiva:** Menú numerado fácil de seguir.
* **Acceso Directo a Ayuda:** Incluye una guía rápida integrada en la terminal.

### Cómo usarlo con el Launcher:

1.  **Ejecuta el Launcher:**
    ```bash
    python Launcher.py
    ```
2.  **Selecciona la Opción 1:** Arrastra tu archivo de marcadores original a la terminal para cargarlo en el sistema.
3.  **Selecciona la Opción 2:** Genera automáticamente el borrador **`config_GENERADO.txt`**.
4.  **Prepara tu Configuración:** Fuera de la terminal, edita tu archivo y guárdalo como **`config.txt`**.
5.  **Selecciona la Opción 3:** Ejecuta la reorganización final. El script detectará automáticamente tu `config.txt` y creará el nuevo HTML.

---

## ⚙️ Configuración del Árbol (`config.txt`)

El archivo `config.txt` es el mapa que sigue el organizador:

* **Carpetas (`C: `):** Define el nombre de una carpeta.
* **Palabras Clave (`K: `):** Términos separados por comas. Si el script encuentra estas palabras en el **título** o la **URL**, moverá el link a esa carpeta.
* **Jerarquía:** Usa **4 espacios** para anidar carpetas o palabras clave dentro de otras.

### Ejemplo de `config.txt`:

```text
C: 01. Inteligencia Artificial
    C: Modelos de Lenguaje
        K: gpt, claude, deepseek, gemini, perplexity
    C: Herramientas Code
        K: v0.dev, blackbox, cursor, copilot
C: 02. Programacion
    C: Python
        K: python, django, flask, pandas, pip
    C: Web Dev
        K: react, nodejs, typescript, tailwind, css
C: 03. Ocio
    K: youtube, reddit, juegos, steam

---

## 💻 El Script de Python (`OrganizadorBookmarks.py`)

Crea un archivo llamado `OrganizadorBookmarks.py` y pega el código desarrollado. El flujo de ejecución es el siguiente:

* **Ingreso de ruta:** El programa solicita la ubicación del archivo `.html`.
* **Validación:** Comprueba que el archivo sea legítimo y tenga el formato correcto.
* **Detección de Configuración:** Busca automáticamente el archivo `config.txt` en la misma ubicación que el HTML.
* **Limpieza:** Identifica y elimina duplicados exactos basándose en la URL.
* **Clasificación:** Analiza y mapea cada link a su nueva carpeta según las reglas definidas.
* **Salida:** Genera un nuevo archivo llamado `favoritos_REORGANIZADOS.html`.

## 📖 Modo de Uso (Flujo de Trabajo Recomendado)

### Paso 1: Generar el borrador (Ingeniería Inversa)
Si no quieres escribir el `config.txt` desde cero, ejecuta el generador para que trabaje por ti:

```bash
python GeneradorConfig.py

* **Indica la ruta** de tus marcadores actuales cuando el script lo solicite.
* El script creará un archivo llamado **`config_GENERADO.txt`** que contiene todas tus carpetas y nombres de páginas actuales.
* **Edita este archivo:** Mueve las líneas, limpia lo que no sirva y, al finalizar, **renómbralo a `config.txt`**.

### Paso 2: Ejecutar la Reorganización
Una vez que tu archivo `config.txt` refleja la estructura que deseas, ejecuta el organizador principal:

```bash
python OrganizadorBookmarks.py

### Paso 3: Interactúa con el programa
Ambas herramientas utilizan un sistema de rutas inteligente gestionado por `utils.py`:

* **Pega la ruta** del archivo HTML (puedes arrastrar el archivo directamente a la ventana de la terminal).
* **Presiona ENTER** en las rutas de configuración o de salida si deseas usar los valores por defecto (se guardarán en la misma carpeta que el archivo original).

## 🔍 Lógica de Clasificación y Errores

El script opera bajo reglas estrictas para asegurar que ningún enlace se pierda y que la organización sea coherente:

* **Prioridad:** El script recorre el árbol de configuración de **arriba hacia abajo**. El primer grupo de palabras clave (`K:`) que coincida con el título o la URL del link definirá su destino final.
* **Sin Clasificar:** Si un link no coincide con ninguna palabra clave definida en tu `config.txt`, se moverá automáticamente a una carpeta raíz llamada `00. Sin Clasificar`. Esto garantiza que **no haya pérdida de datos**.
* **Manejo de Duplicados:** La limpieza se basa estrictamente en la **URL**. Si el script encuentra la misma dirección web repetida (incluso si tiene nombres diferentes), conservará únicamente la primera instancia procesada y eliminará las demás.

## 📊 Ejemplo de Informe Final

Al finalizar, el script mostrará un resumen como este en la terminal:

```text
========================================
         INFORME DE PROCESAMIENTO
========================================
Total links encontrados:  185
Duplicados eliminados:    12
Links clasificados:       150
Links sin clasificar:     23
----------------------------------------
Archivo final: favoritos_REORGANIZADOS.html
========================================
