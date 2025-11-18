#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Conversor de YouTube a MP3
Script principal para ejecutar la aplicación
"""

import os
import sys

# Obtener el directorio actual (src) y el directorio padre
current_dir = os.path.dirname(os.path.abspath(__file__))
# Ya estamos en src, así que añadimos el directorio actual al path
sys.path.insert(0, current_dir)

def main():
    try:
        from controller.youtube2mp3_controller import YouTube2MP3Controller
        
        controller = YouTube2MP3Controller()
        
        controller.run()
        
    except ImportError as e:
        print(f"\n❌ Error de importación: {e}")
        print("Asegúrese de que todos los archivos están en su lugar:")
        print("- controller/youtube2mp3_controller.py")
        print("- model/youtube2mp3_model.py") 
        print("- view/youtube2mp3_view.py")
    except KeyboardInterrupt:
        print("\n\nPrograma interrumpido por el usuario. ¡Hasta luego!")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        print("Asegúrese de que todas las dependencias están instaladas.")
        print("Ejecute: pip install -r requierments.txt")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
