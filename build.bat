@echo off
chcp 65001 >nul
title EKHO - Build

if not exist web\index.html (
    echo ERROR: No se encuentra web\index.html
    echo.
    echo Copia el build de Lovable (dist\ ^<---^> web\) antes de empaquetar.
    echo Ejemplo: xcopy /E /I dist\ web\
    pause
    exit /b 1
)

echo ====================================
echo  Empaquetando EKHO con PyInstaller
echo ====================================
echo.

pyinstaller --onefile --windowed --name EKHO ^
    --add-data "web;web" ^
    --add-data "src;src" ^
    --hidden-import=pygame ^
    --hidden-import=mutagen ^
    --hidden-import=yt_dlp ^
    --hidden-import=requests ^
    --hidden-import=spotdl ^
    --hidden-import=sqlite3 ^
    --hidden-import=pytubefix ^
    --hidden-import=moviepy.editor ^
    app.py

echo.
if %errorlevel% equ 0 (
    echo ====================================
    echo  Ejecutable creado: dist\EKHO.exe
    echo.
    echo  Los datos de usuario se guardan en:
    echo    %%APPDATA%%\EKHO\
    echo ====================================
) else (
    echo [31mERRO: Error durante el empaquetado[0m
    echo Revisa los mensajes de error de PyInstaller.
)
echo.
pause
