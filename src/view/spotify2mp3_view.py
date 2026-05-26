# spotify2mp3_view.py
"""View for Spotify to MP3 converter following a robust MVC pattern"""

import os
import sys
from typing import List

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from view.conversor_view import BaseView


class SpotifyView(BaseView):
    """Specific view for Spotify to MP3 conversion"""
    
    def __init__(self):
        """Initialize Spotify view"""
        super().__init__()
        self.converter_name = "CONVERSOR DE SPOTIFY A MP3"
        self.converter_description = "Convierte pistas de Spotify a archivos MP3 usando SpotDL"
    
    def get_converter_name(self) -> str:
        """Get converter name"""
        return self.converter_name
    
    def get_converter_description(self) -> str:
        """Get converter description"""
        return self.converter_description
    
    def get_user_input(self) -> str:
        """Get Spotify URL from the user"""
        print("[MUSIC] Ingresa la URL de la pista de Spotify que quieres convertir:")
        self.show_supported_formats()
        return self.get_user_input_safe("URL: ")
    
    def show_supported_formats(self) -> None:
        """Show supported URL formats"""
        print("\n[LIST] Formatos soportados:")
        print("  • https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh")
        print("  • https://open.spotify.com/intl-es/track/4iV5W9uYEdYUVa79Axb7Rh")
        print("  • spotify:track:4iV5W9uYEdYUVa79Axb7Rh")
        print("  [TIP] URLs con parámetros (?si=...) se manejan automáticamente")
        print("  [FAST] No necesita credenciales - funciona inmediatamente\n")
    
    def show_conversion_steps(self) -> None:
        """Show conversion process steps"""
        steps = [
            "[SEARCH] Extraer metadatos de Spotify usando SpotDL",
            "[SEARCH] Buscar pista correspondiente en YouTube",
            "[DOWN] Descargar audio desde YouTube",
            "[MUSIC] Convertir a formato MP3",
            "[TAG] Añadir metadatos y portada",
            "[SAVE] Guardar archivo final con metadatos"
        ]
        self.show_progress_steps(steps)
    
    def show_system_info(self) -> None:
        """Show simplified system information"""
        print("[TIP] SISTEMA SIMPLIFICADO ACTIVADO")
        print("[OK] SpotDL: Metadatos de Spotify + descarga integrada")
        print("[OK] yt-dlp: Búsqueda y descarga desde YouTube")
        print("[OK] moviepy: Conversión de audio optimizada")
        print("[OK] mutagen: Metadatos MP3 precisos")
        print("[OK] Sin múltiples bibliotecas redundantes")
        print("[OK] Arquitectura limpia y eficiente\n")
    
    def show_metadata_info(self) -> None:
        """Show information about saved metadata"""
        print("[NOTE] METADATOS GUARDADOS:")
        print("  • Título, artista, álbum")
        print("  • Duración, género, fecha")
        print("  • URL de origen, ruta local")
        print("  • Portada del álbum, letra (si disponible)")
        print("  • Archivo fijo para integración con BD")
        
        try:
            from model.spotify2mp3_model import Spotify2MP3Converter
            converter = Spotify2MP3Converter()
            metadata_path = converter.info_extractor.get_metadata_file_path()
            print(f"  [FOLDER] Metadatos en: {metadata_path}")
        except:
            pass
    
    def show_setup_info(self) -> None:
        """Show setup and requirements information"""
        instructions = [
            "[MUSIC] FORMATOS DE URL SOPORTADOS:",
            "   • https://open.spotify.com/track/ID",
            "   • https://open.spotify.com/intl-XX/track/ID", 
            "   • spotify:track:ID",
            "",
            "[TOOL] DEPENDENCIAS REQUERIDAS:",
            "   pip install \"setuptools<81\" pytubefix spotdl yt-dlp moviepy mutagen requests",
            "",
            "[CONFIG] FFMPEG REQUERIDO:",
            "   Windows: Descargar desde https://ffmpeg.org/",
            "   Linux: sudo apt install ffmpeg",
            "   macOS: brew install ffmpeg",
            "",
            "[TARGET] ARQUITECTURA SIMPLIFICADA:",
            "   • SpotDL maneja metadatos y descarga",
            "   • yt-dlp para búsquedas en YouTube",
            "   • moviepy para conversión de audio",
            "   • mutagen para metadatos MP3",
            "",
            "[SCALE] NOTA LEGAL:",
            "   Este conversor busca contenido en YouTube.",
            "   Respeta derechos de autor y términos de servicio."
        ]
        self.show_instructions(instructions)
    
    def show_welcome(self) -> None:
        """Show personalized welcome message"""
        super().show_welcome()
        print("[TARGET] FUNCIONALIDADES:")
        print("  [OK] Extracción de metadatos completos de Spotify")
        print("  [OK] Búsqueda inteligente en YouTube")
        print("  [OK] Conversión a MP3 de alta calidad")
        print("  [OK] Metadatos automáticos con portada")
        print("  [OK] Guardado en archivo fijo para BD")
        print("  [OK] Sistema simplificado sin redundancias\n")
