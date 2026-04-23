#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EKHO - Plataforma Musical 

Punto de entrada principal que utiliza el patrón MVC mejorado con:
- Controladores como comunicadores entre Model y View
- Separación clara de responsabilidades
- Bibliotecas esenciales sin redundancias
"""

import os
import sys

# Obtener el directorio actual (src) y añadirlo al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


def main():
    """Función principal que ejecuta la aplicación"""
    print(f"\n🎵 Iniciando Ekho Music Converter...")
    print(f"\n⚙️  Configurando terminal...")

    try:
        # Importar el controlador principal consolidado
        from controller.conversor_controller import ConversorController
        
        # Crear y ejecutar controlador principal consolidado
        conversor_controller = ConversorController()
        conversor_controller.run()
        
    except ImportError as e:
        print(f"\n❌ Error de importación: {e}")
        print("\n🔧 SOLUCIONES POSIBLES:")
        print("1. Verificar que todas las dependencias estén instaladas:")
        print("   python install_dependencies.py")
        print("\n2. Verificar que FFmpeg esté instalado:")
        print("   Windows: winget install Gyan.FFmpeg")
        print("   Linux: sudo apt install ffmpeg")
        print("   macOS: brew install ffmpeg")
        
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrumpido por el usuario. ¡Hasta luego!")
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        print("\n🔍 INFORMACIÓN DE DEBUG:")
        import traceback
        traceback.print_exc()
        
        print("\n💡 CONSEJOS PARA SOLUCIONAR:")
        print("1. Verificar que todas las dependencias estén correctamente instaladas")
        print("2. Ejecutar el instalador de dependencias: python install_dependencies.py")
        print("3. Verificar que FFmpeg esté disponible en el PATH del sistema")


if __name__ == "__main__":
    main()
