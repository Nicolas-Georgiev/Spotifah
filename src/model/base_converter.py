# base_converter.py
"""
Clase base para conversores de diferentes plataformas
Facilita la expansión a otras plataformas manteniendo consistencia en metadatos
"""

class BaseConverter:
    """Clase base para todos los convertidores de audio"""
    
    # Constantes de origen para mantener consistencia
    ORIGIN_YOUTUBE = "YouTube"
    ORIGIN_SPOTIFY = "Spotify"
    ORIGIN_SOUNDCLOUD = "SoundCloud"
    ORIGIN_UNKNOWN = "Unknown"
    
    def __init__(self, origin_name):
        self.origin = origin_name
    
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
            return BaseConverter.ORIGIN_YOUTUBE
        elif 'spotify.com' in url_lower:
            return BaseConverter.ORIGIN_SPOTIFY
        elif 'soundcloud.com' in url_lower:
            return BaseConverter.ORIGIN_SOUNDCLOUD
        else:
            return BaseConverter.ORIGIN_UNKNOWN


class ConverterFactory:
    """Factory para crear el conversor apropiado según la URL"""
    
    @staticmethod
    def create_converter(url):
        """Crea el conversor apropiado basado en la URL"""
        platform = BaseConverter.detect_platform(url)
        
        if platform == BaseConverter.ORIGIN_YOUTUBE:
            from youtube2mp3_model import YouTube2MP3Converter
            return YouTube2MP3Converter()
        elif platform == BaseConverter.ORIGIN_SPOTIFY:
            from spotify2mp3_model import Spotify2MP3Converter
            return Spotify2MP3Converter()
        elif platform == BaseConverter.ORIGIN_SOUNDCLOUD:
            # TODO: Implementar SoundCloudConverter en el futuro
            raise NotImplementedError("SoundCloud converter no implementado aún")
        else:
            raise ValueError(f"Plataforma no soportada: {platform}")
    
    @staticmethod
    def get_supported_platforms():
        """Retorna lista de plataformas soportadas actualmente"""
        return [
            BaseConverter.ORIGIN_YOUTUBE,
            BaseConverter.ORIGIN_SPOTIFY,
            # BaseConverter.ORIGIN_SOUNDCLOUD,  # Futuro
        ]
