@echo off
:: Esto asegura que el script se ejecute en la carpeta donde esta el .bat
cd /d "%~dp0"

echo Lanzando Organizador de Marcadores...
:: Usamos el python del entorno virtual directamente
".\venv\Scripts\python.exe" Launcher.py

pause