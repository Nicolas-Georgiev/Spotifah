# spotify2mp3_view.py
"""Vista para el conversor de Spotify a MP3 siguiendo patrón MVC robusto"""

import os
import sys
from typing import List

# Añadir path para importaciones
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from view.conversor_view import BaseView


class SpotifyView(BaseView):
    """Vista específica para conversión de Spotify a MP3"""
    
    def __init__(self):
        """Inicializar vista de Spotify"""
        super().__init__()
        self.converter_name = "CONVERSOR DE SPOTIFY A MP3"
        self.converter_description = "Convierte pistas de Spotify a archivos MP3 usando SpotDL"
    
    def get_converter_name(self) -> str:
        """Obtener nombre del convertidor"""
        return self.converter_name
    
    def get_converter_description(self) -> str:
        """Obtener descripción del convertidor"""
        return self.converter_description
    
    def get_user_input(self) -> str:
        """Obtener URL de Spotify del usuario"""
        print("🎵 Ingresa la URL de la pista de Spotify que quieres convertir:")
        self.show_supported_formats()
        return self.get_user_input_safe("URL: ")
    
    def show_supported_formats(self) -> None:
        """Mostrar formatos de URL soportados"""
        print("\n📋 Formatos soportados:")
        print("  • https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh")
        print("  • https://open.spotify.com/intl-es/track/4iV5W9uYEdYUVa79Axb7Rh")
        print("  • spotify:track:4iV5W9uYEdYUVa79Axb7Rh")
        print("  💡 URLs con parámetros (?si=...) se manejan automáticamente")
        print("  🚀 No necesita credenciales - funciona inmediatamente\n")
    
    def show_conversion_steps(self) -> None:
        """Mostrar pasos del proceso de conversión"""
        steps = [
            "🔍 Extraer metadatos de Spotify usando SpotDL",
            "🔎 Buscar pista correspondiente en YouTube",
            "⬇️ Descargar audio desde YouTube",
            "🎵 Convertir a formato MP3",
            "🏷️ Añadir metadatos y portada",
            "💾 Guardar archivo final con metadatos"
        ]
        self.show_progress_steps(steps)
    
    def show_system_info(self) -> None:
        """Mostrar información del sistema simplificado"""
        print("💡 SISTEMA SIMPLIFICADO ACTIVADO")
        print("✅ SpotDL: Metadatos de Spotify + descarga integrada")
        print("✅ yt-dlp: Búsqueda y descarga desde YouTube")
        print("✅ moviepy: Conversión de audio optimizada")
        print("✅ mutagen: Metadatos MP3 precisos")
        print("✅ Sin múltiples bibliotecas redundantes")
        print("✅ Arquitectura limpia y eficiente\n")
    
    def show_metadata_info(self) -> None:
        """Mostrar información sobre metadatos guardados"""
        print("📝 METADATOS GUARDADOS:")
        print("  • Título, artista, álbum")
        print("  • Duración, género, fecha")
        print("  • URL de origen, ruta local")
        print("  • Portada del álbum, letra (si disponible)")
        print("  • Archivo fijo para integración con BD")
        
        # Mostrar ruta del archivo de metadatos
        try:
            from model.spotify2mp3_model import Spotify2MP3Converter
            converter = Spotify2MP3Converter()
            metadata_path = converter.info_extractor.get_metadata_file_path()
            print(f"  📁 Metadatos en: {metadata_path}")
        except:
            pass
    
    def show_setup_info(self) -> None:
        """Mostrar información de configuración y requisitos"""
        instructions = [
            "🎵 FORMATOS DE URL SOPORTADOS:",
            "   • https://open.spotify.com/track/ID",
            "   • https://open.spotify.com/intl-XX/track/ID", 
            "   • spotify:track:ID",
            "",
            "🔧 DEPENDENCIAS REQUERIDAS:",
            "   pip install \"setuptools<81\" pytubefix spotdl yt-dlp moviepy mutagen requests",
            "",
            "⚙️ FFMPEG REQUERIDO:",
            "   Windows: Descargar desde https://ffmpeg.org/",
            "   Linux: sudo apt install ffmpeg",
            "   macOS: brew install ffmpeg",
            "",
            "🎯 ARQUITECTURA SIMPLIFICADA:",
            "   • SpotDL maneja metadatos y descarga",
            "   • yt-dlp para búsquedas en YouTube",
            "   • moviepy para conversión de audio",
            "   • mutagen para metadatos MP3",
            "",
            "⚖️ NOTA LEGAL:",
            "   Este conversor busca contenido en YouTube.",
            "   Respeta derechos de autor y términos de servicio."
        ]
        self.show_instructions(instructions)
    
    def show_welcome(self) -> None:
        """Mostrar mensaje de bienvenida personalizado"""
        super().show_welcome()
        print("🎯 FUNCIONALIDADES:")
        print("  ✅ Extracción de metadatos completos de Spotify")
        print("  ✅ Búsqueda inteligente en YouTube")
        print("  ✅ Conversión a MP3 de alta calidad")
        print("  ✅ Metadatos automáticos con portada")
        print("  ✅ Guardado en archivo fijo para BD")
        print("  ✅ Sistema simplificado sin redundancias\n")


# Funciones de compatibilidad para código existente
def show_welcome():
    """Función de compatibilidad"""
    view = SpotifyView()
    view.show_welcome()

def get_spotify_url():
    """Función de compatibilidad"""
    view = SpotifyView()
    return view.get_user_input()

def show_message(message):
    """Función de compatibilidad"""
    view = SpotifyView()
    view.show_message(message)

def show_result(file_path):
    """Función de compatibilidad"""
    view = SpotifyView()
    view.show_result(file_path)

def show_error(error_message):
    """Función de compatibilidad"""
    view = SpotifyView()
    view.show_error(error_message)

def show_alternative_methods_info():
    """Función de compatibilidad"""
    view = SpotifyView()
    view.show_system_info()

def show_setup_instructions():
    """Función de compatibilidad"""
    view = SpotifyView()
    view.show_setup_info()

def ask_continue():
    """Función de compatibilidad"""
    view = SpotifyView()
    return view.ask_continue()

def show_goodbye():
    """Función de compatibilidad"""
    view = SpotifyView()
    view.show_goodbye()