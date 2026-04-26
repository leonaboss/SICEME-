@echo off
REM Cambia el directorio a la ubicacion del script (raiz del proyecto)
cd /d "%~dp0"

REM Activa el entorno virtual
CALL .venv\Scripts\activate

REM Inicia el servidor de Django, accesible desde cualquier IP en la red
python manage.py runserver 0.0.0.0:8000
