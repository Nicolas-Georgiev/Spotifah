@echo off
chcp 65001 >nul
title EKHO - Build

echo ====================================
echo  EKHO - Build de produccion
echo ====================================
echo.

:: Verificar que PyInstaller esta instalado
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando PyInstaller...
    pip install pyinstaller
)

:: Reconstruir frontend
echo [1/4] Reconstruyendo frontend...
if exist "lovable-code\node_modules\.bin\vite.cmd" (
    pushd lovable-code
    call npx vite build
    if %errorlevel% neq 0 (
        echo ERROR: Fallo la compilacion del frontend
        popd
        pause
        exit /b 1
    )
    popd
) else (
    echo WARNING: node_modules no encontrado, saltando build del frontend...
)

:: Copiar assets a web/
echo [2/4] Copiando assets...
if exist "lovable-code\dist\client\assets" (
    xcopy /E /I /Y "lovable-code\dist\client\assets\*" "web\assets\" >nul
    echo OK - Assets copiados
) else (
    echo WARNING: No se encontraron assets compilados, usando existentes...
)

:: Verificar que web/index.html existe
if not exist "web\index.html" (
    echo ERROR: No se encuentra web/index.html
    pause
    exit /b 1
)

echo [3/4] Construyendo ejecutable...

pyinstaller ^
    --onefile ^
    --noconsole ^
    --name "EKHO" ^
    --add-data "web;web" ^
    --hidden-import "pywebview" ^
    --hidden-import "pygame" ^
    --hidden-import "mutagen" ^
    --hidden-import "moviepy" ^
    --hidden-import "requests" ^
    "app.py"

if %errorlevel% equ 0 (
    echo.
    echo ====================================
    echo  EXE generado: dist\EKHO.exe
    echo ====================================
) else (
    echo.
    echo ERROR: Fallo la compilacion
    pause
    exit /b 1
)

pause
