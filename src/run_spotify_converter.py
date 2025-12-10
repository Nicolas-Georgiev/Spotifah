#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Conversor de Spotify a MP3
Script principal usando métodos alternativos (sin credenciales API)
"""

import os
import sys

# Obtener el directorio actual (src) y añadirlo al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def main():
    try:
        from controller.spotify2mp3_controller import Spotify2MP3Controller
        
        controller = Spotify2MP3Controller()
        controller.run()
        
    except ImportError as e:
        print(f"\n❌ Error de importación: {e}")
        print("Asegúrese de que todas las dependencias están instaladas:")
        print("pip install yt-dlp requests mutagen eyed3 moviepy")
        print("\nY que todos los archivos están en su lugar:")
        print("- controller/spotify2mp3_controller.py")
        print("- model/spotify2mp3_model.py") 
        print("- view/spotify2mp3_view.py")
    except KeyboardInterrupt:
        print("\n\nPrograma interrumpido por el usuario. ¡Hasta luego!")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        print("Asegúrese de que todas las dependencias están instaladas.")
        print("Ejecute: pip install spotipy yt-dlp")
        print("Y configure las credenciales de Spotify API.")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()