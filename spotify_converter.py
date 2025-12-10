#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de acceso directo al conversor de Spotify
Ejecuta el conversor que está en src/
"""

import os
import sys

def main():
    try:
        # Añadir src al path
        src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
        sys.path.insert(0, src_dir)
        
        # Importar y ejecutar el controlador
        from controller.spotify2mp3_controller import Spotify2MP3Controller
        
        controller = Spotify2MP3Controller()
        controller.run()
        
    except ImportError as e:
        print(f"\n❌ Error de importación: {e}")
        print("Asegúrese de que todos los archivos están en su lugar:")
        print("- src/controller/spotify2mp3_controller.py")
        print("- src/model/spotify2mp3_model.py") 
        print("- src/view/spotify2mp3_view.py")
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