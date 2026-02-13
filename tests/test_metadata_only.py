# test_metadata_only.py
"""
Test rápido solo para leer metadatos de archivos MP3 existentes
"""

import sys
import json
import datetime
from pathlib import Path

# Intentar importar bibliotecas para metadatos
HAS_METADATA = False
METADATA_TYPE = None

try:
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3
    HAS_METADATA = True
    METADATA_TYPE = "mutagen"
    print("✅ Usando mutagen para leer metadatos")
except ImportError:
    try:
        import eyed3
        HAS_METADATA = True
        METADATA_TYPE = "eyed3"
        print("✅ Usando eyed3 para leer metadatos")
    except ImportError:
        print("❌ No hay bibliotecas de metadatos disponibles")
        print("   Instala: pip install mutagen")
        sys.exit(1)

def read_metadata_detailed(file_path):
    """Lee y muestra los metadatos detallados de un archivo MP3"""
    print(f"\n📋 Analizando metadatos de: {file_path}")
    print("="*60)
    
    if not file_path.exists():
        print(f"❌ Archivo no encontrado: {file_path}")
        return None
    
    # Estructura de metadatos para JSON
    metadata = {
        "archivo": str(file_path),
        "nombre": file_path.name,
        "tamaño_bytes": file_path.stat().st_size,
        "tamaño_mb": round(file_path.stat().st_size / (1024*1024), 2),
        "fecha_analisis": datetime.datetime.now().isoformat(),
        "metadatos": {}
    }
    
    try:
        if METADATA_TYPE == "mutagen":
            audio = MP3(file_path, ID3=ID3)
            
            # Información básica
            titulo = str(audio.get('TIT2', ['No disponible'])[0]) if audio.get('TIT2') else 'No disponible'
            artista = str(audio.get('TPE1', ['No disponible'])[0]) if audio.get('TPE1') else 'No disponible'
            album = str(audio.get('TALB', ['No disponible'])[0]) if audio.get('TALB') else 'No disponible'
            año = str(audio.get('TDRC', ['No disponible'])[0]) if audio.get('TDRC') else 'No disponible'
            genero = str(audio.get('TCON', ['No disponible'])[0]) if audio.get('TCON') else 'No disponible'
            
            metadata["metadatos"].update({
                "titulo": titulo,
                "artista": artista,
                "album": album,
                "año": año,
                "genero": genero
            })
            
            print("🎵 INFORMACIÓN BÁSICA:")
            print(f"   📝 Título: {titulo}")
            print(f"   👤 Artista: {artista}")
            print(f"   💿 Álbum: {album}")
            print(f"   📅 Año: {año}")
            print(f"   🎭 Género: {genero}")
            
            print("\n🔊 INFORMACIÓN TÉCNICA:")
            if audio.info:
                duracion = audio.info.length
                metadata["metadatos"].update({
                    "duracion_segundos": round(duracion, 2),
                    "duracion_formato": f"{duracion//60:.0f}:{duracion%60:05.2f}",
                    "bitrate": audio.info.bitrate,
                    "canales": audio.info.channels,
                    "tipo_canales": 'Estéreo' if audio.info.channels == 2 else 'Mono' if audio.info.channels == 1 else 'Multi-canal',
                    "frecuencia_muestreo": audio.info.sample_rate
                })
                
                print(f"   🕐 Duración: {metadata['metadatos']['duracion_segundos']} segundos ({metadata['metadatos']['duracion_formato']})")
                print(f"   🎧 Bitrate: {metadata['metadatos']['bitrate']} kbps")
                print(f"   📊 Canales: {metadata['metadatos']['canales']} ({metadata['metadatos']['tipo_canales']})")
                print(f"   🔊 Frecuencia: {metadata['metadatos']['frecuencia_muestreo']} Hz")
                print(f"   📦 Tamaño: {metadata['tamaño_mb']} MB")
            
            print("\n🖼️ INFORMACIÓN DE PORTADA:")
            cover_found = False
            for key in audio.tags.keys() if audio.tags else []:
                if key.startswith('APIC'):
                    cover_found = True
                    apic = audio.tags[key]
                    metadata["metadatos"]["portada"] = {
                        "presente": True,
                        "tipo": apic.type,
                        "tipo_descripcion": 'Portada frontal' if apic.type == 3 else 'Otra',
                        "formato": apic.mime,
                        "tamaño_bytes": len(apic.data)
                    }
                    print(f"   ✅ Portada encontrada:")
                    print(f"      📐 Tipo: {apic.type} ({metadata['metadatos']['portada']['tipo_descripcion']})")
                    print(f"      📄 Formato: {apic.mime}")
                    print(f"      📏 Tamaño: {len(apic.data)} bytes")
                    break
            
            if not cover_found:
                metadata["metadatos"]["portada"] = {"presente": False}
                print("   ❌ No se encontró portada")
            
            print("\n🏷️ TODOS LOS METADATOS:")
            if audio.tags:
                metadata["metadatos"]["todos_los_tags"] = {}
                for key, value in audio.tags.items():
                    if not key.startswith('APIC'):  # No mostrar datos binarios de imagen
                        try:
                            metadata["metadatos"]["todos_los_tags"][key] = str(value)
                            print(f"   {key}: {value}")
                        except:
                            metadata["metadatos"]["todos_los_tags"][key] = "Error al convertir"
                            print(f"   {key}: Error al convertir")
            else:
                print("   ⚠️ No se encontraron metadatos")
        
        elif METADATA_TYPE == "eyed3":
            import eyed3
            audiofile = eyed3.load(file_path)
            
            print("🎵 INFORMACIÓN BÁSICA:")
            if audiofile.tag:
                titulo = audiofile.tag.title or 'No disponible'
                artista = audiofile.tag.artist or 'No disponible'
                album = audiofile.tag.album or 'No disponible'
                año = str(audiofile.tag.recording_date) if audiofile.tag.recording_date else 'No disponible'
                genero = audiofile.tag.genre.name if audiofile.tag.genre else 'No disponible'
                
                metadata["metadatos"].update({
                    "titulo": titulo,
                    "artista": artista,
                    "album": album,
                    "año": año,
                    "genero": genero
                })
                
                print(f"   📝 Título: {titulo}")
                print(f"   👤 Artista: {artista}")
                print(f"   💿 Álbum: {album}")
                print(f"   📅 Año: {año}")
                print(f"   🎭 Género: {genero}")
            
            print("\n🔊 INFORMACIÓN TÉCNICA:")
            if audiofile.info:
                duracion = audiofile.info.time_secs
                metadata["metadatos"].update({
                    "duracion_segundos": round(duracion, 2),
                    "duracion_formato": f"{duracion//60:.0f}:{duracion%60:05.2f}",
                    "bitrate": audiofile.info.bit_rate[1]
                })
                
                print(f"   🕐 Duración: {metadata['metadatos']['duracion_segundos']} segundos")
                print(f"   🎧 Bitrate: {metadata['metadatos']['bitrate']} kbps")
                print(f"   📦 Tamaño: {metadata['tamaño_mb']} MB")
                
            print("\n🖼️ INFORMACIÓN DE PORTADA:")
            if audiofile.tag and audiofile.tag.images:
                metadata["metadatos"]["portada"] = {
                    "presente": True,
                    "cantidad": len(audiofile.tag.images),
                    "formato": audiofile.tag.images[0].mime_type,
                    "tamaño_bytes": len(audiofile.tag.images[0].image_data)
                }
                for i, image in enumerate(audiofile.tag.images):
                    print(f"   ✅ Portada {i+1}:")
                    print(f"      📄 Formato: {image.mime_type}")
                    print(f"      📏 Tamaño: {len(image.image_data)} bytes")
            else:
                metadata["metadatos"]["portada"] = {"presente": False}
                print("   ❌ No se encontró portada")
                
    except Exception as e:
        print(f"❌ Error al leer metadatos: {e}")
        metadata["metadatos"]["error"] = str(e)
    
    return metadata

def save_metadata_json(metadata_list, output_file="metadata_detallado.json"):
    """Guarda los metadatos en un archivo JSON"""
    try:
        json_data = {
            "fecha_generacion": datetime.datetime.now().isoformat(),
            "total_archivos": len(metadata_list),
            "herramienta": "Test Metadatos MP3",
            "version": "1.0",
            "archivos": metadata_list
        }
        
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Metadatos detallados guardados en: {output_path}")
        print(f"📊 Total de archivos analizados: {len(metadata_list)}")
        return True
        
    except Exception as e:
        print(f"❌ Error al guardar JSON: {e}")
        return False

def find_mp3_files():
    """Busca archivos MP3 en carpetas de descarga"""
    search_dirs = [
        Path("data/music"),
        Path("test_downloads"),
        Path("test_downloads_ytdlp"),
        Path("downloads"),
        Path("downloads/soundcloud"),
        Path("descargas"),
        Path("."),
    ]
    
    found_files = []
    for dir_path in search_dirs:
        if dir_path.exists():
            mp3_files = list(dir_path.glob("*.mp3"))
            found_files.extend(mp3_files)
    
    return found_files

if __name__ == "__main__":
    print("🎵 Test de Metadatos MP3")
    print("=" * 50)
    
    metadata_list = []
    
    # Verificar si se pasó un archivo específico
    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
        metadata = read_metadata_detailed(file_path)
        if metadata:
            metadata_list.append(metadata)
    else:
        # Buscar archivos MP3 automáticamente
        mp3_files = find_mp3_files()
        
        if mp3_files:
            print(f"🔍 Encontrados {len(mp3_files)} archivos MP3:")
            for i, file in enumerate(mp3_files, 1):
                print(f"   {i}. {file}")
            
            print("\n📋 Analizando metadatos de todos los archivos:")
            for file in mp3_files:
                metadata = read_metadata_detailed(file)
                if metadata:
                    metadata_list.append(metadata)
                print("\n" + "="*60)
        else:
            print("❌ No se encontraron archivos MP3")
            print("💡 Uso:")
            print(f"   python {__file__} ruta/al/archivo.mp3")
            print("   O coloca archivos MP3 en las carpetas: test_downloads, downloads, etc.")
    
    # Guardar metadatos en JSON
    if metadata_list:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        json_filename = f"metadata_detallado_{timestamp}.json"
        save_metadata_json(metadata_list, json_filename)
        
        print(f"\n📄 Resumen:")
        print(f"   📁 Archivos analizados: {len(metadata_list)}")
        print(f"   💾 JSON generado: {json_filename}")
    else:
        print("\n⚠️ No se analizaron archivos")