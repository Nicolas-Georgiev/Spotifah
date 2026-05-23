# youtube2mp3_controller.py
"""Controlador para conversión de YouTube a MP3 siguiendo patrón MVC robusto"""

import os
import sys
from typing import Optional

# Añadir la carpeta src al path para importaciones absolutas
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Importar usando rutas absolutas desde src
from controller.conversor_controller import BaseController
from model.youtube2mp3_model import YouTube2MP3Converter
from view.youtube2mp3_view import YouTubeView


class YouTube2MP3Controller(BaseController):
    """Controlador para conversión de YouTube a MP3"""
    
    def __init__(self):
        """Inicializar controlador de YouTube"""
        super().__init__()
        self.model = YouTube2MP3Converter()
        self.view = YouTubeView()
    
    def validate_input(self, url: str) -> bool: # type: ignore
        """Validar que la URL sea de YouTube"""
        if not url or not url.strip():
            return False
        
        url = url.strip()
        youtube_indicators = [
            "youtube.com",
            "youtu.be",
            "www.youtube.com",
            "m.youtube.com"
        ]
        
        return any(indicator in url for indicator in youtube_indicators)
    
    def process_conversion(self, youtube_url: str) -> str:  # type: ignore
        """Procesar conversión de YouTube a MP3"""
        try:
            # Mostrar pasos del proceso
            self.view.show_conversion_steps()
            
            # Procesar conversión
            self.show_progress("⬇️ Descargando desde YouTube...")
            result_path = self.model.convert(youtube_url)
            
            return result_path
            
        except Exception as e:
            raise e
    
    def convert_single_video(self) -> bool:
        """Convierte un vídeo o playlist de YouTube - retorna True si fue exitoso"""
        try:
            # Obtener URL del usuario
            url = self.view.get_user_input()

            # Validar entrada
            if not self.validate_input(url):
                self.handle_error(ValueError(
                    "URL no válida. Debe ser un enlace de YouTube válido "
                    "(youtube.com/watch?v=... o youtu.be/...)"
                ))
                return False

            # — Detectar si es playlist —
            if self.model.is_playlist_url(url):
                print("\n📋 Playlist de YouTube detectada.")
                print("Obteniendo lista de vídeos... (puede tardar unos segundos)")
                try:
                    track_urls = self.model.get_playlist_track_urls(url)
                    total = len(track_urls)
                except Exception as e:
                    self.handle_error(e)
                    return False

                print(f"\n🎵 Se encontraron {total} vídeos.")
                confirm = input("\u00bfDescargar todos? [s/N]: ").strip().lower()
                if confirm not in ('s', 'si', 'yes', 'y'):
                    print("⏹️  Descarga cancelada.")
                    return False

                results = self.model.convert_playlist(url)
                print(f"\n✅ Descargados {len(results)}/{total} vídeos")
                return len(results) > 0

            # — Vídeo individual —
            result_path = self.process_conversion(url)
            self.handle_success(result_path)
            self.view.show_output_info()
            return True

            self.show_progress("⏹️  Operación cancelada por el usuario")
            return False
        except Exception as e:
            self.handle_error(e)
            return False
    
    def run(self) -> None:
        """Ejecutar el flujo principal del controlador"""
        try:
            # Mostrar bienvenida
            self.view.show_welcome()
            
            # Mostrar información del sistema
            self.view.show_system_info()
            
            # Bucle principal de conversión
            while True:
                try:
                    success = self.convert_single_video()
                    
                    # Si hubo éxito o error manejado, preguntar si continuar
                    if not self.view.ask_continue():
                        break
                        
                except KeyboardInterrupt:
                    print("\n⏹️  Programa interrumpido por el usuario")
                    break
                except Exception as e:
                    self.handle_error(e)
                    if not self.view.ask_continue():
                        break
            
            # Mostrar despedida
            self.view.show_goodbye()
            
        except KeyboardInterrupt:
            print("\n⏹️  Programa terminado")
        except Exception as e:
            self.handle_error(e)