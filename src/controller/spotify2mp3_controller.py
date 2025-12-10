# spotify2mp3_controller.py
import os
import sys

# Añadir la carpeta src al path para importaciones absolutas
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Importar usando rutas absolutas desde src
from model.spotify2mp3_model import Spotify2MP3Converter
from view import spotify2mp3_view as view


def validate_url(url):
    """Valida que la URL sea de Spotify"""
    return "spotify.com" in url or url.startswith("spotify:")


class Spotify2MP3Controller:
    def __init__(self):
        self.converter = Spotify2MP3Converter()
        self.view = view
        self._ensure_downloads_folder()

    @staticmethod
    def _ensure_downloads_folder():
        """Crea la carpeta downloads si no existe"""
        downloads_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "music")
        os.makedirs(downloads_dir, exist_ok=True)

    def convert_track(self):
        """Proceso completo de conversión"""
        try:
            url = self.view.get_spotify_url()

            if not validate_url(url):
                self.view.show_error("URL no válida. Debe ser un enlace de Spotify (open.spotify.com) o URI (spotify:)")
                return

            self.view.show_message("🔄 Iniciando conversión desde Spotify...")
            mp3_path = self.converter.convert(url)
            self.view.show_result(mp3_path)

        except Exception as e:
            self.view.show_error(f"No se pudo completar la conversión: {str(e)}")

    def show_setup_instructions(self):
        """Muestra instrucciones de configuración"""
        self.view.show_setup_instructions()

    def run(self):
        """Ejecuta el programa"""
        self.view.show_welcome()
        
        # Mostrar información sobre métodos alternativos
        self.view.show_alternative_methods_info()
        
        while True:
            try:
                self.convert_track()
            except KeyboardInterrupt:
                print("\n\n⏹️  Operación cancelada por el usuario")
                break
            except Exception as e:
                self.view.show_error(f"Error inesperado: {str(e)}")
            
            if not self.view.ask_continue():
                break
                
        self.view.show_goodbye()


