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

set "PYTHON_EXE=python"
set "PIP_EXE=pip"
if exist ".venv\Scripts\python.exe" set "PYTHON_EXE=.venv\Scripts\python.exe"
if exist ".venv\Scripts\pip.exe" set "PIP_EXE=.venv\Scripts\pip.exe"

:: -------------------------------------------------------
:: Verificar dependencias de build
:: -------------------------------------------------------
"%PIP_EXE%" show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando PyInstaller...
    "%PIP_EXE%" install pyinstaller
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

for /f "delims=" %%i in ('%PYTHON_EXE% -c "import site; paths=site.getsitepackages(); print(next((p for p in paths if p.lower().endswith('site-packages')), paths[-1]))"') do set "SITE_PACKAGES=%%i"
echo    site-packages: %SITE_PACKAGES%

if not exist "%SITE_PACKAGES%\tls_client\dependencies\tls-client-64.dll" (
    echo ERROR: No se encuentra tls-client-64.dll en:
    echo        %SITE_PACKAGES%\tls_client\dependencies\tls-client-64.dll
    echo Instala/reinstala tls-client en este entorno: pip install --force-reinstall tls-client
    pause
    exit /b 1
)

for /f "delims=" %%i in ('%PYTHON_EXE% -c "import webview, os; print(os.path.join(os.path.dirname(webview.__file__), \"__pyinstaller\"))"') do set "WEBVIEW_HOOKS=%%i"
echo    webview hooks: %WEBVIEW_HOOKS%

:: Limpiar build anterior
if exist "build\EKHO" rmdir /s /q "build\EKHO"
if exist "dist\EKHO"  rmdir /s /q "dist\EKHO"

"%PYTHON_EXE%" -m PyInstaller ^
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
    --collect-all "spotdl" ^
    --collect-all "pykakasi" ^
    --collect-all "moviepy" ^
    --collect-all "imageio" ^
    --collect-all "imageio-ffmpeg" ^
    --collect-all "numpy" ^
    --collect-all "requests" ^
    --collect-all "babel" ^
    --collect-all "spotdl" ^
    --collect-all "spotipy" ^
    --collect-all "click" ^
    --collect-all "tls_client" ^
    --add-binary "%SITE_PACKAGES%\tls_client\dependencies\tls-client-64.dll;tls_client\dependencies" ^
    --hidden-import "moviepy.editor" ^
    --hidden-import "imageio.v2" ^
    --hidden-import "imageio_ffmpeg" ^
    --hidden-import "pygame" ^
    --hidden-import "ytmusicapi" ^
    --hidden-import "tls_client" ^
    --hidden-import "model.spotify2mp3_model" ^
    --hidden-import "model.youtube2mp3_model" ^
    --hidden-import "model.soundcloud2mp3" ^
    --hidden-import "controller.music_controller" ^
    --hidden-import "databaseManager.db" ^
    --hidden-import "gettext" ^
    --exclude-module "torch" ^
    --exclude-module "transformers" ^
    --exclude-module "scipy" ^
    --collect-all "moviepy" ^
    --collect-all "imageio" ^
    --collect-all "imageio_ffmpeg" ^
    --copy-metadata "imageio" ^
    --copy-metadata "imageio-ffmpeg" ^
    --copy-metadata "moviepy" ^
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

