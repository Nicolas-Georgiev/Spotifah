# base_converter.py
"""
Clase base para conversores de diferentes plataformas
Facilita la expansión a otras plataformas manteniendo consistencia en metadatos
"""
import os

try:
    from frozen_utils import get_music_dir as _get_music_dir
except ImportError:
    def _get_music_dir():
        return os.path.normpath(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "music")
        )

class BaseModel:
    """Clase base para todos los convertidores de audio"""
    
    # Constantes de origen para mantener consistencia
    ORIGIN_YOUTUBE = "YouTube"
    ORIGIN_SPOTIFY = "Spotify"
    ORIGIN_SOUNDCLOUD = "SoundCloud"
    ORIGIN_UNKNOWN = "Unknown"

    # Carpeta de descarga por defecto — usa frozen_utils para ser compatible con el exe
    DEFAULT_DOWNLOAD_FOLDER = _get_music_dir()
    
    def __init__(self, origin_name):
        self.origin = origin_name
        self.download_folder = self.DEFAULT_DOWNLOAD_FOLDER

    def set_download_folder(self, path):
        """
        Cambia la carpeta donde se guardarán las canciones descargadas.
        Crea la carpeta si no existe.
        """
        abs_path = os.path.normpath(os.path.abspath(path))
        os.makedirs(abs_path, exist_ok=True)
        self.download_folder = abs_path
        print(f"[FOLDER] Carpeta de descarga actualizada: {self.download_folder}")
    
    def get_standard_metadata(self, title, artist):
        """Retorna metadatos estándares simplificados para cualquier plataforma"""            
        return {
            'title': title,
            'artist': artist,
            'origin': self.origin
        }
    
    def convert(self, url):
        """Método abstracto que debe implementar cada conversor"""
        raise NotImplementedError("Cada conversor debe implementar el método convert()")
    
    def get_supported_urls(self):
        """Retorna lista de patrones de URL soportados"""
        raise NotImplementedError("Cada conversor debe definir sus URLs soportadas")
    
    @staticmethod
    def detect_platform(url):
        """Detecta qué plataforma es basado en la URL"""
        url_lower = url.lower()
        
        if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            return BaseModel.ORIGIN_YOUTUBE
        elif 'spotify.com' in url_lower:
            return BaseModel.ORIGIN_SPOTIFY
        elif 'soundcloud.com' in url_lower:
            return BaseModel.ORIGIN_SOUNDCLOUD
        else:
            return BaseModel.ORIGIN_UNKNOWN


class ConverterFactory:
    """Factory para crear el conversor apropiado según la URL"""
    
    @staticmethod
    def create_converter(url):
        """Crea el conversor apropiado basado en la URL"""
        platform = BaseModel.detect_platform(url)
        
        if platform == BaseModel.ORIGIN_YOUTUBE:
            from youtube2mp3_model import YouTube2MP3Converter
            return YouTube2MP3Converter()
        elif platform == BaseModel.ORIGIN_SPOTIFY:
            from spotify2mp3_model import Spotify2MP3Converter
            return Spotify2MP3Converter()
        elif platform == BaseModel.ORIGIN_SOUNDCLOUD:
            from model.soundcloud2mp3 import SoundCloudConverter
            return SoundCloudConverter()
        else:
            raise ValueError(f"Plataforma no soportada: {platform}")
    
    @staticmethod
    def get_supported_platforms():
        """Retorna lista de plataformas soportadas actualmente"""
        return [
            BaseModel.ORIGIN_YOUTUBE,
            BaseModel.ORIGIN_SPOTIFY,
            BaseModel.ORIGIN_SOUNDCLOUD,
        ]
