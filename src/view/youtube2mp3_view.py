# youtube2mp3_view.py
"""View for YouTube to MP3 converter following a robust MVC pattern"""

import os
import sys
from typing import List

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from view.conversor_view import BaseView


class YouTubeView(BaseView):
    """Specific view for YouTube to MP3 conversion"""
    
    def __init__(self):
        """Initialize YouTube view"""
        super().__init__()
        self.converter_name = "CONVERSOR DE YOUTUBE A MP3"
        self.converter_description = "Convierte videos de YouTube a archivos MP3"
    
    def get_converter_name(self) -> str:
        """Get converter name"""
        return self.converter_name
    
    def get_converter_description(self) -> str:
        """Get converter description"""
        return self.converter_description
    
    def get_user_input(self) -> str:
        """Get YouTube URL from the user"""
        print("[CAM] Ingresa la URL del video de YouTube que quieres convertir:")
        self.show_supported_formats()
        return self.get_user_input_safe("URL: ")
    
    def show_supported_formats(self) -> None:
        """Show supported URL formats"""
        print("\n[LIST] Formatos soportados:")
        print("  • https://www.youtube.com/watch?v=VIDEO_ID")
        print("  • https://youtu.be/VIDEO_ID")
        print("  • https://m.youtube.com/watch?v=VIDEO_ID")
        print("  [TIP] URLs con parámetros adicionales se manejan automáticamente\n")
    
    def show_conversion_steps(self) -> None:
        """Show conversion process steps"""
        steps = [
            "[SCREEN] Extraer información del video de YouTube",
            "[DOWN] Descargar audio en máxima calidad",
            "[MUSIC] Convertir a formato MP3",
            "[TAG] Añadir metadatos básicos",
            "[SAVE] Guardar archivo final"
        ]
        self.show_progress_steps(steps)
    
    def show_system_info(self) -> None:
        """Show system information"""
        print("[TIP] SISTEMA DE CONVERSIÓN DE YOUTUBE")
        print("[OK] PyTubefix: Descarga confiable desde YouTube")
        print("[OK] moviepy: Conversión de audio optimizada")
        print("[OK] mutagen: Metadatos MP3 precisos")
        print("[OK] Soporte para todas las calidades de video")
        print("[OK] Extracción automática de metadatos\n")
    
    def show_output_info(self) -> None:
        """Show output file information"""
        print("[NOTE] INFORMACIÓN DEL ARCHIVO:")
        print("  • Formato: MP3 de alta calidad")
        print("  • Metadatos: Título, autor, duración extraídos")
        print("  • Ubicación: Carpeta data/music/")
        print("  • Compatible con todos los reproductores")
    
    def show_welcome(self) -> None:
        """Show personalized welcome message"""
        super().show_welcome()
        print("[TARGET] FUNCIONALIDADES:")
        print("  [OK] Descarga directa desde YouTube")
        print("  [OK] Conversión a MP3 de alta calidad")  
        print("  [OK] Metadatos automáticos")
        print("  [OK] Soporte para múltiples calidades")
        print("  [OK] Interfaz simple e intuitiva\n")
