@echo off
chcp 65001 >nul
title EKHO - Build

echo ====================================
echo  EKHO - Build de produccion
echo ====================================
echo.

:: Parametro opcional: --installer (para generar tambien el Setup.exe)
set BUILD_INSTALLER=0
for %%A in (%*) do (
    if "%%A"=="--installer" set BUILD_INSTALLER=1
)

:: -------------------------------------------------------
:: Verificar dependencias de build
:: -------------------------------------------------------
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando PyInstaller...
    pip install pyinstaller
)

:: -------------------------------------------------------
:: [1/3] Build del frontend
:: -------------------------------------------------------
echo [1/3] Construyendo frontend...
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

if not exist "web\index.html" (
    echo ERROR: No se encuentra web\index.html. Ejecuta: cd lovable-code ^&^& npm run build
    pause
    exit /b 1
)

:: -------------------------------------------------------
:: [2/3] Obtener ruta del site-packages de Python
:: -------------------------------------------------------
echo [2/3] Construyendo ejecutable...

for /f "delims=" %%i in ('python -c "import site; print(site.getsitepackages()[0])"') do set SITE_PACKAGES=%%i
echo    site-packages: %SITE_PACKAGES%

for /f "delims=" %%i in ('python -c "import webview, os; print(os.path.join(os.path.dirname(webview.__file__), \"__pyinstaller\"))"') do set WEBVIEW_HOOKS=%%i
echo    webview hooks: %WEBVIEW_HOOKS%

:: Limpiar build anterior
if exist "build\EKHO" rmdir /s /q "build\EKHO"
if exist "dist\EKHO"  rmdir /s /q "dist\EKHO"

pyinstaller ^
    --noconfirm ^
    --clean ^
    --onedir ^
    --noconsole ^
    --name "EKHO" ^
    --icon "assets\icons\logo-ekho.ico" ^
    --additional-hooks-dir "%WEBVIEW_HOOKS%" ^
    --add-data ".ENV;." ^
    --add-data "web;web" ^
    --add-data "assets\icons;assets\icons" ^
    --add-data "assets\portadas;assets\portadas" ^
    --add-data "data\BDD\ekho.db;data\BDD" ^
    --paths "src" ^
    --collect-all "yt_dlp" ^
    --collect-all "pytubefix" ^
    --collect-all "webview" ^
    --hidden-import "tls_client" ^
    --hidden-import "spotapi" ^
    --hidden-import "SpotipyFree" ^
    --hidden-import "spotdl" ^
    --hidden-import "spotdl.search.song_gatherer" ^
    --hidden-import "pykakasi" ^
    --hidden-import "moviepy.editor" ^
    --hidden-import "imageio" ^
    --hidden-import "pygame" ^
    --hidden-import "ytmusicapi" ^
    --exclude-module "spotdl.web" ^
    --exclude-module "spotdl.console" ^
    --exclude-module "torch" ^
    --exclude-module "transformers" ^
    --exclude-module "scipy" ^
    --hidden-import "model.spotify2mp3_model" ^
    --hidden-import "model.youtube2mp3_model" ^
    --hidden-import "model.soundcloud2mp3" ^
    --hidden-import "model.music_library" ^
    --hidden-import "model.conversor_model" ^
    --hidden-import "model.playlist_model" ^
    --hidden-import "model.db_adapter" ^
    --hidden-import "controller.music_controller" ^
    --hidden-import "controller.playlist_controller" ^
    --hidden-import "controller.conversor_controller" ^
    --hidden-import "controller.spotify2mp3_controller" ^
    --hidden-import "controller.youtube2mp3_controller" ^
    --hidden-import "controller.soundcloud2mp3_controller" ^
    --hidden-import "databaseManager.db" ^
    --hidden-import "databaseManager.BDD" ^
    --hidden-import "frozen_utils" ^
    --hidden-import "mutagen" ^
    --hidden-import "mutagen.mp3" ^
    --hidden-import "mutagen.id3" ^
    --hidden-import "requests" ^
    --copy-metadata "imageio" ^
    --copy-metadata "imageio-ffmpeg" ^
    --copy-metadata "moviepy" ^
    --copy-metadata "mutagen" ^
    --copy-metadata "requests" ^
    --copy-metadata "yt-dlp" ^
    --copy-metadata "spotdl" ^
    --copy-metadata "tls-client" ^
    --copy-metadata "pytubefix" ^
    --copy-metadata "pygame" ^
    --copy-metadata "pykakasi" ^
    --copy-metadata "pywebview" ^
    "app.py"

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Fallo la compilacion del ejecutable
    pause
    exit /b 1
)

echo.
echo ====================================
echo  Carpeta generada: dist\EKHO\
echo  Ejecutable:       dist\EKHO\EKHO.exe
echo ====================================

:: -------------------------------------------------------
:: [3/3] Generar installer con Inno Setup (si se solicito)
:: -------------------------------------------------------
if "%BUILD_INSTALLER%"=="1" (
    echo.
    echo [3/3] Compilando installer con Inno Setup...

    if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
        "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" installer.iss
        if errorlevel 1 (
            echo ERROR: Fallo la compilacion del installer
        ) else (
            echo.
            echo ====================================
            echo  Installer: dist\installer\EKHO-Setup-1.0.0.exe
            echo ====================================
        )
    ) else if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" (
        "%ProgramFiles%\Inno Setup 6\ISCC.exe" installer.iss
        if errorlevel 1 (
            echo ERROR: Fallo la compilacion del installer
        ) else (
            echo.
            echo ====================================
            echo  Installer: dist\installer\EKHO-Setup-1.0.0.exe
            echo ====================================
        )
    ) else (
        echo AVISO: Inno Setup no encontrado. Instala desde: https://jrsoftware.org/isinfo.php
        echo Luego ejecuta manualmente: ISCC.exe installer.iss
    )
)

pause

