# youtube2mp3_controller.py
import os
import sys

# Añadir la carpeta src al path para importaciones absolutas
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Importar usando rutas absolutas desde src
from model.youtube2mp3_model import YouTube2MP3Converter
from view import youtube2mp3_view as view


def validate_url(url):
    """Valida que la URL sea de YouTube"""
    return "youtube.com" in url or "youtu.be" in url


class YouTube2MP3Controller:
    def __init__(self):
        self.converter = YouTube2MP3Converter()
        self.view = view
        self._ensure_downloads_folder()

    @staticmethod
    def _ensure_downloads_folder():
        """Crea la carpeta downloads si no existe"""
        if not os.path.exists("downloads"):
            os.makedirs("downloads")

    def convert_video(self):
        """Proceso completo de conversión"""
        try:
            url = self.view.get_youtube_url()

            if not validate_url(url):
                self.view.show_error("URL no válida. Debe ser un enlace de YouTube (youtube.com o youtu.be)")
                return

            self.view.show_message("🔄 Iniciando descarga...")
            mp3_path = self.converter.convert(url)
            self.view.show_result(mp3_path)

        except Exception as e:
            self.view.show_error(f"No se pudo completar la conversión: {str(e)}")

    def run(self):
        """Ejecuta el programa"""
        self.view.show_welcome()
        
        while True:
            try:
                self.convert_video()
            except KeyboardInterrupt:
                print("\n\n⏹️  Operación cancelada por el usuario")
                break
            except Exception as e:
                self.view.show_error(f"Error inesperado: {str(e)}")
            
            if not self.view.ask_continue():
                break
                
        self.view.show_goodbye()

