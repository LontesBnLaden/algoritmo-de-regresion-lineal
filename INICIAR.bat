@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    where py >nul 2>nul
    if errorlevel 1 (
        python -m venv .venv
    ) else (
        py -3 -m venv .venv
    )
    if errorlevel 1 goto error
)

".venv\Scripts\python.exe" -c "import streamlit" >nul 2>nul
if errorlevel 1 (
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto error
)

start "Regresion Lab" /D "%CD%" "%CD%\.venv\Scripts\python.exe" -m streamlit run app.py --server.headless true --server.address 127.0.0.1 --server.port 8501
for /L %%i in (1,1,20) do (
    ".venv\Scripts\python.exe" -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health', timeout=1)" >nul 2>nul
    if not errorlevel 1 goto open_browser
    timeout /t 1 /nobreak >nul
)
echo La aplicacion no respondio en http://127.0.0.1:8501.
pause
exit /b 1

:open_browser
start "" "http://127.0.0.1:8501"
exit /b 0

:error
echo No se pudo preparar la aplicacion. Revisa que Python 3.10 o posterior este instalado y que haya conexion a Internet.
pause
exit /b 1
