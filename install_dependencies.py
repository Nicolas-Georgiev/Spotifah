#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de instalación de dependencias para conversión de audio
"""

import subprocess
import sys
import os

def check_ffmpeg():
    """Verifica si FFmpeg está instalado y disponible"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_ffmpeg():
    """Verifica e instala FFmpeg (OBLIGATORIO para máxima calidad)"""
    print("\n🎬 Verificando FFmpeg (OBLIGATORIO)...")
    
    if check_ffmpeg():
        print("   ✅ FFmpeg instalado - Máxima calidad de conversión")
        return True
    
    print("   ❌ FFmpeg NO ENCONTRADO - Es OBLIGATORIO para funcionalidad completa")
    print("   🚨 INSTALACIÓN REQUERIDA DE FFmpeg:")
    print("   " + "="*45)
    print("   🚀 MÉTODO AUTOMÁTICO (recomendado):")
    print("      winget install Gyan.FFmpeg")
    print()
    print("   🚀 MÉTODO MANUAL:")
    print("      1. Ve a: https://www.gyan.dev/ffmpeg/builds/")
    print("      2. Descarga: 'ffmpeg-release-essentials.zip'")
    print("      3. Extrae a: C:\\ffmpeg\\")
    print("      4. Añade al PATH: C:\\ffmpeg\\bin\\")
    print("      5. Reinicia terminal y ejecuta: ffmpeg -version")
    print("   " + "="*45)
    print()
    print("   ❌ SIN FFmpeg: Funcionalidad LIMITADA y calidad REDUCIDA")
    print("   🚨 INSTALAR FFmpeg para funcionalidad COMPLETA")
    
    return False  # FFmpeg es REQUERIDO

def install_package(package_name):
    """Instala un paquete usando pip"""
    try:
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
        __import__(import_name)
        return True
    except ImportError:
        return False

def main():
    print("=== INSTALADOR DE DEPENDENCIAS PARA CONVERSIÓN DE AUDIO ===\n")
    
    # Verificar e instalar FFmpeg primero
    ffmpeg_ok = install_ffmpeg()
    
    packages_to_check = [
        ("pytubefix", "pytubefix"),
        ("moviepy==1.0.3", "moviepy.editor"),
        ("mutagen", "mutagen"),
        ("requests", "requests"),
        ("eyed3", "eyed3"),
        ("yt-dlp>=2023.1.0", "yt_dlp"),
        ("spotdl", "spotdl")
    ]
    
    missing_packages = []
    
    # Verificar paquetes existentes
    print("1. Verificando paquetes instalados:")
    for package, import_name in packages_to_check:
        if check_package(package, import_name):
            print(f"   ✅ {package}: INSTALADO")
        else:
            print(f"   ❌ {package}: FALTA")
            missing_packages.append(package)
    
    # Instalar paquetes faltantes
    if missing_packages:
        print(f"\n2. Instalando {len(missing_packages)} paquete(s) faltante(s):")
        
        for package in missing_packages:
            print(f"   📦 Instalando {package}...")
            if install_package(package):
                print(f"   ✅ {package} instalado exitosamente")
                
                # Verificación especial para moviepy después de instalación
                if package.startswith("moviepy"):
                    try:
                        # Forzar reimportación de moviepy
                        if 'moviepy' in sys.modules:
                            del sys.modules['moviepy']
                        if 'moviepy.editor' in sys.modules:
                            del sys.modules['moviepy.editor']
                        
                        from moviepy.editor import AudioFileClip
                        print(f"   ✅ {package} verificado y funcionando correctamente")
                    except ImportError as e:
                        print(f"   ⚠️ {package} instalado pero hay problemas de importación: {e}")
            else:
                print(f"   ❌ Error instalando {package}")
    else:
        print("\n2. ✅ Todos los paquetes necesarios están instalados")
    
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
    
    # Test específico de eyed3
    try:
        import eyed3
        print("   ✅ eyed3: FUNCIONAL")
        eyed3_ok = True
    except Exception as e:
        print(f"   ❌ eyed3: ERROR ({e})")
        eyed3_ok = False
    
    # Test específico de yt-dlp
    try:
        import yt_dlp
        print("   ✅ yt-dlp: FUNCIONAL")
        ytdlp_ok = True
    except Exception as e:
        print(f"   ❌ yt-dlp: ERROR ({e})")
        ytdlp_ok = False
    
    # Test específico de spotdl (OBLIGATORIO)
    try:
        from spotdl import Spotdl
        print("   ✅ spotdl: FUNCIONAL (REQUERIDO para Spotify)")
        spotdl_ok = True
    except Exception as e:
        print(f"   ❌ spotdl: FALTA - OBLIGATORIO ({e})")
        print("   🚨 spotdl es REQUERIDO para metadatos confiables de Spotify")
        spotdl_ok = False
    
    print("\n=== RESULTADO ===")
    if moviepy_ok and pytubefix_ok and mutagen_ok and eyed3_ok and ytdlp_ok and spotdl_ok and ffmpeg_ok:
        print("🎉 ¡TODAS LAS DEPENDENCIAS ESTÁN COMPLETAS!")
        print("✅ Los conversores de YouTube y Spotify funcionarán a MÁXIMA CAPACIDAD")
        print("🔥 FFmpeg disponible - Máxima calidad de conversión")
        print("🔥 SpotDL disponible - Metadatos perfectos de Spotify")
        print("💡 Configuración ÓPTIMA alcanzada")
    elif moviepy_ok and pytubefix_ok and mutagen_ok and eyed3_ok and ytdlp_ok:
        print("⚠️ Dependencias básicas listas pero FALTAN COMPONENTES CRÍTICOS")
        if not spotdl_ok:
            print("❌ FALTA spotdl: pip install spotdl")
        if not ffmpeg_ok:
            print("❌ FALTA FFmpeg: Instalar desde https://www.gyan.dev/ffmpeg/builds/")
    elif moviepy_ok and pytubefix_ok and mutagen_ok:
        print("⚠️ Conversor de YouTube parcial")
        print("❌ Para Spotify completo OBLIGATORIO: pip install eyed3 yt-dlp spotdl")
        if not ffmpeg_ok:
            print("❌ FFmpeg REQUERIDO para calidad completa")
    elif moviepy_ok and pytubefix_ok:
        print("⚠️ Funcionalidad MUY LIMITADA - Faltan dependencias críticas")
        print("❌ OBLIGATORIO: pip install mutagen eyed3 yt-dlp spotdl + FFmpeg")
    elif pytubefix_ok:
        print("⚠️ Solo descarga básica de YouTube disponible")
        print("❌ CRÍTICO: pip install moviepy mutagen eyed3 yt-dlp spotdl + FFmpeg")
    else:
        print("❌ CONFIGURACIÓN INCOMPLETA - Dependencias críticas faltantes")
        print("🚨 EJECUTAR: pip install pytubefix moviepy mutagen eyed3 yt-dlp spotdl")
        print("🚨 ADEMÁS: Instalar FFmpeg desde https://www.gyan.dev/ffmpeg/builds/")
    
    if not ffmpeg_ok or not spotdl_ok:
        print("\n🚨 DEPENDENCIAS CRÍTICAS FALTANTES:")
        if not ffmpeg_ok:
            print("   ❌ FFmpeg REQUERIDO para conversión de máxima calidad")
            print("   🔧 Sin FFmpeg: Calidad reducida y limitaciones de formato")
        if not spotdl_ok:
            print("   ❌ SpotDL REQUERIDO para metadatos confiables de Spotify")
            print("   🔧 Sin SpotDL: Metadatos incompletos o incorrectos")
        print("   💻 Ambos componentes son OBLIGATORIOS para funcionalidad completa")

if __name__ == "__main__":
    main()
