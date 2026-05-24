#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de instalación de dependencias para conversión de audio
"""

import subprocess
import sys
import warnings
import shutil

def check_ffmpeg():
    """Verifica si FFmpeg está instalado y disponible"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def _command_exists(command_name):
    """Verifica si un comando existe en el PATH."""
    return shutil.which(command_name) is not None

def install_ffmpeg():
    """Verifica e instala FFmpeg automáticamente en Windows con winget."""
    
    if check_ffmpeg():
        print("   ✅ FFmpeg instalado - Máxima calidad de conversión")
        return True

    if not _command_exists("winget"):
        print("   ⚠️ winget no está disponible en este sistema")
    else:
        command = [
            "winget",
            "install",
            "--id",
            "Gyan.FFmpeg",
            "-e",
            "--accept-package-agreements",
            "--accept-source-agreements"
        ]

        try:
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode == 0 and check_ffmpeg():
                print("   ✅ FFmpeg: INSTALADO")
                return True

            print("   ⚠️ No se pudo instalar FFmpeg con winget")
            if result.stderr:
                print(f"   🔎 Detalle: {result.stderr.strip()}")
        except Exception as e:
            print(f"   ⚠️ Error ejecutando winget: {e}")
    
    return False  # FFmpeg es REQUERIDO

def install_package(package_name):
    """Instala un paquete usando pip"""
    try:
        # spotdl requiere pkg_resources, que viene en setuptools
        if package_name.startswith("spotdl"):
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "setuptools<81", "wheel"])
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package_name])
            return True

        # Para moviepy, forzar la versión específica y upgrade si es necesario
        if package_name.startswith("moviepy"):
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name, "--upgrade", "--force-reinstall"])
        else:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        return False

def check_package(package_name, import_name=None):
    """Verifica si un paquete está instalado"""
    if import_name is None:
        import_name = package_name
    
    try:
        if import_name == "pkg_resources":
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=UserWarning)
                __import__(import_name)
        else:
            __import__(import_name)
        return True
    except ImportError:
        return False

def main():
    print("=== INSTALADOR DE DEPENDENCIAS PARA CONVERSIÓN DE AUDIO ===\n")
    print("1. Verificando paquetes instalados:")

    # Verificar e instalar FFmpeg primero
    ffmpeg_ok = install_ffmpeg()
    
    packages_to_check = [
        ("FFmpeg", "ffmpeg"),
        ("setuptools<81", "pkg_resources"),
        ("pytubefix", "pytubefix"),
        ("moviepy==1.0.3", "moviepy.editor"),
        ("mutagen", "mutagen"),
        ("requests", "requests"),
        ("yt-dlp>=2023.1.0", "yt_dlp"),
        ("spotdl", "spotdl")
    ]
    
    missing_packages = []
    
    # Verificar paquetes existentes
    for package, import_name in packages_to_check:
        if check_package(package, import_name):
            print(f"   ✅ {package}: INSTALADO")
        else:
            print(f"   ❌ {package}: FALTA")
            missing_packages.append(package)
    
    # Instalar paquetes faltantes
    print("\n2. Buscando paquetes faltantes:")
    if missing_packages:
        print(f"\n Instalando {len(missing_packages)} paquete(s) faltante(s):")
        
        for package in missing_packages:
            print(f"   📦 Instalando {package}...")
            if install_package(package):
                print(f"   ✅ {package} instalado exitosamente")
            else:
                print(f"\n   ❌ Error instalando {package}")
    else:
        print("\n✅ Todos los paquetes necesarios están instalados")
    
    # Verificación final
    print("\n3. Verificación final:")
    
    # Test específico de moviepy
    try:
        from moviepy.editor import AudioFileClip
        print("   ✅ moviepy.editor: FUNCIONAL")
        moviepy_ok = True
    except Exception as e:
        print(f"   ❌ moviepy.editor: ERROR ({e})")
        moviepy_ok = False
    
    # Test específico de pytubefix
    try:
        from pytubefix import YouTube
        print("   ✅ pytubefix: FUNCIONAL")
        pytubefix_ok = True
    except Exception as e:
        print(f"   ❌ pytubefix: ERROR ({e})")
        pytubefix_ok = False
    
    # Test específico de mutagen
    try:
        from mutagen.mp3 import MP3
        from mutagen.id3 import ID3
        from mutagen.id3._frames import APIC
        print("   ✅ mutagen: FUNCIONAL")
        mutagen_ok = True
    except Exception as e:
        print(f"   ❌ mutagen: ERROR ({e})")
        mutagen_ok = False
    
    # Test específico de yt-dlp
    try:
        import yt_dlp
        print("   ✅ yt-dlp: FUNCIONAL")
        ytdlp_ok = True
    except Exception as e:
        print(f"   ❌ yt-dlp: ERROR ({e})")
        ytdlp_ok = False

    # Test específico de setuptools/pkg_resources (requerido por spotdl)
    try:
        __import__("pkg_resources")
        print("   ✅ pkg_resources (setuptools): FUNCIONAL")
        setuptools_ok = True
    except Exception as e:
        print(f"   ❌ pkg_resources (setuptools): ERROR ({e})")
        setuptools_ok = False
    
    # Test específico de spotdl (OBLIGATORIO)
    try:
        import spotdl
        print(f"   ✅ spotdl: FUNCIONAL")
        spotdl_ok = True
    except Exception as e:
        print(f"   ❌ spotdl: FALTA - OBLIGATORIO ({e})")
        print("   🚨 spotdl es REQUERIDO para metadatos confiables de Spotify")
        spotdl_ok = False

    # Mostrar resultado final
    print("\n=== RESULTADO ===")
    if moviepy_ok and pytubefix_ok and mutagen_ok and ytdlp_ok and setuptools_ok and spotdl_ok and ffmpeg_ok:
        print("🎉 ¡TODAS LAS DEPENDENCIAS ESTÁN COMPLETAS!")
    else:
        for package, import_name in packages_to_check:
            if not check_package(package, import_name):
                print(f"   ❌ {package} - {import_name} FALTA")
                print(f"   🚨 INSTALAR CON: pip install {package}")
    

if __name__ == "__main__":
    main()
