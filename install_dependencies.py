#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de instalación de dependencias para conversión de audio
"""

import subprocess
import sys
import os

def install_package(package_name):
    """Instala un paquete usando pip"""
    try:
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
    
    packages_to_check = [
        ("pytubefix", "pytubefix"),
        ("moviepy", "moviepy.editor"),
        ("mutagen", "mutagen"),
        ("requests", "requests"),
        ("pygame", "pygame")
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
        from mutagen.id3 import ID3, APIC
        print("   ✅ mutagen: FUNCIONAL")
        mutagen_ok = True
    except Exception as e:
        print(f"   ❌ mutagen: ERROR ({e})")
        mutagen_ok = False
    
    print("\n=== RESULTADO ===")
    if moviepy_ok and pytubefix_ok and mutagen_ok:
        print("🎉 ¡Todas las dependencias están listas!")
        print("✅ La conversión M4A → MP3 CON PORTADA funcionará correctamente")
    elif moviepy_ok and pytubefix_ok:
        print("⚠️ Conversión funcional, sin soporte de portadas")
        print("💡 Para portadas, ejecuta: pip install mutagen")
    elif pytubefix_ok:
        print("⚠️ Descarga funcional, conversión limitada")
        print("💡 Para conversión completa: pip install moviepy mutagen")
    else:
        print("❌ Faltan dependencias críticas")
        print("💡 Ejecuta: pip install pytubefix moviepy mutagen")

if __name__ == "__main__":
    main()
