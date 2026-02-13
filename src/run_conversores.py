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
        print("   pip install -r requirements.txt")
        print("\n2. Instalar dependencias manualmente:")
        print("   pip install spotdl yt-dlp moviepy mutagen requests")
        print("\n3. Verificar que FFmpeg esté instalado:")
        print("   Windows: Descargar desde https://ffmpeg.org/")
        print("   Linux: sudo apt install ffmpeg")
        print("   macOS: brew install ffmpeg")
        print("\n4. Verificar estructura de archivos:")
        print("   - controller/main_controller.py")
        print("   - controller/spotify2mp3_controller.py") 
        print("   - controller/youtube2mp3_controller.py")
        print("   - model/spotify2mp3_model.py")
        print("   - model/youtube2mp3_model.py")
        print("   - view/spotify2mp3_view.py")
        print("   - view/youtube2mp3_view.py")
        
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
        print("4. Comprobar permisos de escritura en las carpetas del proyecto")


if __name__ == "__main__":
    main()
