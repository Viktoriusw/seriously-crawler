@echo off
REM Script de ejecución rápida del SEO Crawler (Windows)

echo ========================================
echo   SEO Crawler Professional
echo ========================================
echo.

REM Verificar si existe el entorno virtual
if not exist "venv" (
    echo [ERROR] No se encontro el entorno virtual.
    echo.
    echo Por favor, ejecuta primero la instalacion:
    echo    python -m venv venv
    echo    venv\Scripts\activate
    echo    pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Activar entorno virtual
echo [OK] Activando entorno virtual...
call venv\Scripts\activate.bat

REM Verificar argumentos
if "%1"=="" (
    echo [OK] Lanzando interfaz grafica...
    python seo_crawler\main.py gui
) else if "%1"=="gui" (
    echo [OK] Lanzando interfaz grafica...
    python seo_crawler\main.py gui
) else if "%1"=="help" (
    python seo_crawler\main.py --help
) else (
    REM Pasar todos los argumentos al programa
    python seo_crawler\main.py %*
)

REM Desactivar entorno virtual
deactivate
