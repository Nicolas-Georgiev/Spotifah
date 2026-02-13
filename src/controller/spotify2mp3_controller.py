# spotify2mp3_controller.py
"""Controlador para conversión de Spotify a MP3 siguiendo patrón MVC robusto"""

import os
import sys
from typing import Optional

# Añadir la carpeta src al path para importaciones absolutas
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Importar usando rutas absolutas desde src
from controller.conversor_controller import BaseController
from model.spotify2mp3_model import Spotify2MP3Converter
from view.spotify2mp3_view import SpotifyView


class Spotify2MP3Controller(BaseController):
    """Controlador para conversión de Spotify a MP3"""
    
    def __init__(self):
        """Inicializar controlador de Spotify"""
        super().__init__()
        self.model = Spotify2MP3Converter()
        self.view = SpotifyView()
        self.current_session = None
    
    def validate_input(self, url: str) -> bool: # type: ignore
        """Validar que la URL sea de Spotify"""
        if not url or not url.strip():
            return False
        
        url = url.strip()
        spotify_indicators = [
            "spotify.com",
            "spotify:",
            "open.spotify.com"
        ]
        
        return any(indicator in url for indicator in spotify_indicators)
    
    def process_conversion(self, spotify_url: str) -> str: # type: ignore
        """Procesar conversión de Spotify a MP3"""
        try:
            # Iniciar sesión de descarga
            self.show_progress("🎵 Iniciando sesión de conversión...")
            self.model.start_download_session(is_batch=False)
            
            # Mostrar pasos del proceso
            self.view.show_conversion_steps()
            
            # Procesar conversión
            self.show_progress("🔍 Extrayendo metadatos de Spotify...")
            result_path = self.model.convert(spotify_url)
            
            # Finalizar sesión
            self.model.finish_download_session()
            
            return result_path
            
        except Exception as e:
            # Limpiar sesión en caso de error
            if hasattr(self.model, 'finish_download_session'):
                try:
                    self.model.finish_download_session()
                except:
                    pass
            raise e
    
    def convert_single_track(self) -> bool:
        """Convertir una sola pista - retorna True si fue exitoso"""
        try:
            # Obtener URL del usuario
            url = self.view.get_user_input()
            
            # Validar entrada
            if not self.validate_input(url):
                self.handle_error(ValueError(
                    "URL no válida. Debe ser un enlace de Spotify válido "
                    "(open.spotify.com/track/... o spotify:track:...)"
                ))
                return False
            
            # Procesar conversión
            result_path = self.process_conversion(url)
            
            # Mostrar resultado exitoso
            self.handle_success(result_path)
            
            # Mostrar información adicional
            self.view.show_metadata_info()
            
            return True
            
        except KeyboardInterrupt:
            self.show_progress("⏹️  Operación cancelada por el usuario")
            return False
        except Exception as e:
            self.handle_error(e)
            return False
    
    def show_setup_info(self) -> None:
        """Mostrar información de configuración"""
        self.view.show_setup_info()
    
    def run(self) -> None:
        """Ejecutar el flujo principal del controlador"""
        try:
            # Mostrar bienvenida
            self.view.show_welcome()
            
            # Mostrar información del sistema simplificado
            self.view.show_system_info()
            
            # Bucle principal de conversión
            while True:
                try:
                    success = self.convert_single_track()
                    
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


