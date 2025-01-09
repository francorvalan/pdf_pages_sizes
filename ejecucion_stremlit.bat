@echo off
REM Cambiar al directorio del script
cd /d "%~dp0"

REM Activar el entorno de Conda
call conda activate streamlit

REM Ejecutar la aplicación Streamlit
streamlit run app.py
