# youtube2mp3_view.py
"""Vista para el conversor de YouTube a MP3 siguiendo patrón MVC robusto"""

import os
import sys
from typing import List

# Añadir path para importaciones
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from view.conversor_view import BaseView


class YouTubeView(BaseView):
    """Vista específica para conversión de YouTube a MP3"""
    
    def __init__(self):
        """Inicializar vista de YouTube"""
        super().__init__()
        self.converter_name = "CONVERSOR DE YOUTUBE A MP3"
        self.converter_description = "Convierte videos de YouTube a archivos MP3"
    
    def get_converter_name(self) -> str:
        """Obtener nombre del convertidor"""
        return self.converter_name
    
    def get_converter_description(self) -> str:
        """Obtener descripción del convertidor"""
        return self.converter_description
    
    def get_user_input(self) -> str:
        """Obtener URL de YouTube del usuario"""
        print("🎥 Ingresa la URL del video de YouTube que quieres convertir:")
        self.show_supported_formats()
        return self.get_user_input_safe("URL: ")
    
    def show_supported_formats(self) -> None:
        """Mostrar formatos de URL soportados"""
        print("\n📋 Formatos soportados:")
        print("  • https://www.youtube.com/watch?v=VIDEO_ID")
        print("  • https://youtu.be/VIDEO_ID")
        print("  • https://m.youtube.com/watch?v=VIDEO_ID")
        print("  💡 URLs con parámetros adicionales se manejan automáticamente\n")
    
    def show_conversion_steps(self) -> None:
        """Mostrar pasos del proceso de conversión"""
        steps = [
            "📺 Extraer información del video de YouTube",
            "⬇️ Descargar audio en máxima calidad",
            "🎵 Convertir a formato MP3",
            "🏷️ Añadir metadatos básicos",
            "💾 Guardar archivo final"
        ]
        self.show_progress_steps(steps)
    
    def show_system_info(self) -> None:
        """Mostrar información del sistema"""
        print("💡 SISTEMA DE CONVERSIÓN DE YOUTUBE")
        print("✅ PyTubefix: Descarga confiable desde YouTube")
        print("✅ moviepy: Conversión de audio optimizada")
        print("✅ mutagen: Metadatos MP3 precisos")
        print("✅ Soporte para todas las calidades de video")
        print("✅ Extracción automática de metadatos\n")
    
    def show_output_info(self) -> None:
        """Mostrar información sobre el archivo de salida"""
        print("📝 INFORMACIÓN DEL ARCHIVO:")
        print("  • Formato: MP3 de alta calidad")
        print("  • Metadatos: Título, autor, duración extraídos")
        print("  • Ubicación: Carpeta data/music/")
        print("  • Compatible con todos los reproductores")
    
    def show_welcome(self) -> None:
        """Mostrar mensaje de bienvenida personalizado"""
        super().show_welcome()
        print("🎯 FUNCIONALIDADES:")
        print("  ✅ Descarga directa desde YouTube")
        print("  ✅ Conversión a MP3 de alta calidad")  
        print("  ✅ Metadatos automáticos")
        print("  ✅ Soporte para múltiples calidades")
        print("  ✅ Interfaz simple e intuitiva\n")


# Funciones de compatibilidad para código existente
def show_welcome():
    """Función de compatibilidad"""
    view = YouTubeView()
    view.show_welcome()

def get_youtube_url():
    """Función de compatibilidad"""
    view = YouTubeView()
    return view.get_user_input()

def show_message(message):
    """Función de compatibilidad"""
    view = YouTubeView()
    view.show_message(message)

def show_result(file_path):
    """Función de compatibilidad"""
    view = YouTubeView()
    view.show_result(file_path)

def show_error(error_message):
    """Función de compatibilidad"""
    view = YouTubeView()
    view.show_error(error_message)

def ask_continue():
    """Función de compatibilidad"""
    view = YouTubeView()
    return view.ask_continue()

def show_goodbye():
    """Función de compatibilidad"""
    view = YouTubeView()
    view.show_goodbye()
