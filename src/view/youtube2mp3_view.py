# youtube2mp3_view.py

def show_welcome():
    """Muestra mensaje de bienvenida"""
    print("\n" + "="*60)
    print("  🎵 CONVERSOR DE YOUTUBE A MP3 🎵")
    print("  Convierte videos de YouTube a archivos MP3")
    print("="*60 + "\n")


def get_youtube_url():
    """Solicita la URL de YouTube al usuario"""
    print("Ingresa la URL del video de YouTube que quieres convertir:")
    return input("URL: ").strip()


def show_message(message):
    """Muestra un mensaje genérico"""
    print(f"ℹ️  {message}")


def show_result(file_path):
    """Muestra la ruta del archivo MP3 generado"""
    print(f"\n🎉 ¡Conversión completada!")
    print(f"📁 Archivo MP3 guardado en: {file_path}")
    print(f"🔊 El archivo debería reproducirse correctamente ahora\n")


def show_error(error_message):
    """Muestra un mensaje de error"""
    print(f"\n❌ Error: {error_message}\n")


def ask_continue():
    """Pregunta si el usuario desea convertir otro video"""
    response = input("¿Deseas convertir otro video? (s/n): ").lower().strip()
    return response in ['s', 'si', 'sí', 'y', 'yes']


def show_goodbye():
    """Muestra mensaje de despedida"""
    print("\n" + "="*50)
    print("  ¡Cerrando el conversor!")
    print("="*50 + "\n")
