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
echo [1/3] Reconstruyendo frontend...
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

:: Verificar que web/index.html existe
if not exist "web\index.html" (
    echo ERROR: No se encuentra web/index.html
    pause
    exit /b 1
)

echo [2/3] Construyendo ejecutable...

pyinstaller ^
    --onefile ^
    --noconsole ^
    --name "EKHO" ^
    --icon "assets\icons\logo-ekho.ico" ^
    --add-data "assets\icons\logo-ekho.ico;assets\icons" ^
    --add-data "web;web" ^
    --add-data "src;src" ^
    --hidden-import "pywebview" ^
    --hidden-import "pygame" ^
    --hidden-import "mutagen" ^
    --hidden-import "moviepy" ^
    --hidden-import "moviepy.editor" ^
    --copy-metadata "imageio" ^
    --hidden-import "requests" ^
    --hidden-import "yt_dlp" ^
    --collect-all "spotdl" ^
    --collect-data "pykakasi" ^
    --hidden-import "pytubefix" ^
    --hidden-import "model.spotify2mp3_model" ^
    --hidden-import "model.youtube2mp3_model" ^
    --hidden-import "model.soundcloud2mp3" ^
    --hidden-import "controller.music_controller" ^
    --hidden-import "model.music_library" ^
    --hidden-import "databaseManager.db" ^
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
