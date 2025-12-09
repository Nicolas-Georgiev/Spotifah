# spotify2mp3_view.py

def show_welcome():
    """Muestra mensaje de bienvenida"""
    print("\n" + "="*60)
    print("  🎵 CONVERSOR DE SPOTIFY A MP3 🎵")
    print("  Convierte pistas de Spotify a archivos MP3")
    print("  🔄 Usando métodos alternativos (sin API oficial)")
    print("="*60 + "\n")


def get_spotify_url():
    """Solicita la URL de Spotify al usuario"""
    print("Ingresa la URL de la pista de Spotify que quieres convertir:")
    print("Formatos aceptados:")
    print("  • https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh")
    print("  • https://open.spotify.com/intl-es/track/4iV5W9uYEdYUVa79Axb7Rh")
    print("  • spotify:track:4iV5W9uYEdYUVa79Axb7Rh")
    print("  💡 URLs con parámetros (?si=...) y códigos internacionales se manejan automáticamente")
    print("  🚀 No necesita credenciales - funciona inmediatamente")
    return input("URL: ").strip()


def show_message(message):
    """Muestra un mensaje genérico"""
    print(f"ℹ️  {message}")


def show_result(file_path):
    """Muestra la ruta del archivo MP3 generado"""
    print(f"\n🎉 ¡Conversión completada!")
    print(f"📁 Archivo MP3 guardado en: {file_path}")
    print(f"🔊 El archivo incluye metadatos obtenidos con métodos alternativos\n")


def show_error(error_message):
    """Muestra un mensaje de error"""
    print(f"\n❌ Error: {error_message}\n")


def show_alternative_methods_info():
    """Muestra información sobre métodos alternativos"""
    print("\n💡 INFORMACIÓN: Métodos Alternativos Activados")
    print("✅ Sin necesidad de credenciales de API")
    print("✅ Sin límites de uso")  
    print("⚠️  Los metadatos pueden ser más básicos que con API oficial")
    print("🔄 Obtiene información usando múltiples fuentes públicas\n")


def show_setup_instructions():
    """Muestra instrucciones de uso"""
    print("\n" + "="*70)
    print("  📋 INFORMACIÓN DE USO")
    print("="*70)
    print("\n1. 🎵 Formatos de URL soportados:")
    print("   • https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh")
    print("   • https://open.spotify.com/intl-es/track/4iV5W9uYEdYUVa79Axb7Rh")
    print("   • spotify:track:4iV5W9uYEdYUVa79Axb7Rh")
    print("\n2. 🔄 Métodos alternativos:")
    print("   • Extrae metadatos usando fuentes públicas")
    print("   • Busca la música en YouTube para descargar")
    print("   • Funciona sin credenciales de API")
    print("\n3. 📦 Dependencias necesarias:")
    print("   pip install yt-dlp requests mutagen eyed3")
    print("\n4. ⚖️  Nota legal:")
    print("   Este conversor busca la pista en YouTube para descargarla.")
    print("   Respeta los derechos de autor y términos de servicio.")
    print("="*70 + "\n")


def ask_continue():
    """Pregunta si el usuario desea convertir otra pista"""
    response = input("¿Deseas convertir otra pista? (s/n): ").lower().strip()
    return response in ['s', 'si', 'sí', 'y', 'yes']


def show_goodbye():
    """Muestra mensaje de despedida"""
    print("\n" + "="*50)
    print("  ¡Gracias por usar el conversor de Spotify!")
    print("="*50)
    print("="*50 + "\n")