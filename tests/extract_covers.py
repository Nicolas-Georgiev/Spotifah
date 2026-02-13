# extract_covers.py
"""
Extractor de portadas de archivos MP3
"""

import sys
from pathlib import Path
import datetime

# Intentar importar bibliotecas para metadatos
HAS_METADATA = False
METADATA_TYPE = None

try:
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3
    HAS_METADATA = True
    METADATA_TYPE = "mutagen"
    print("✅ Usando mutagen para extraer portadas")
except ImportError:
    try:
        import eyed3
        HAS_METADATA = True
        METADATA_TYPE = "eyed3"
        print("✅ Usando eyed3 para extraer portadas")
    except ImportError:
        print("❌ No hay bibliotecas de metadatos disponibles")
        print("   Instala: pip install mutagen")
        sys.exit(1)

def extract_cover_from_mp3(file_path, output_dir=None, custom_name=None):
    """Extrae la portada de un archivo MP3 específico"""
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"❌ Archivo no encontrado: {file_path}")
        return None
    
    if output_dir is None:
        # Usar carpeta assets/covers por defecto
        output_dir = Path("assets/covers")
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🎵 Extrayendo portada de: {file_path.name}")
    
    try:
        if METADATA_TYPE == "mutagen":
            audio = MP3(file_path, ID3=ID3)
            
            if audio.tags:
                cover_count = 0
                extracted_files = []
                
                for key in audio.tags.keys():
                    if key.startswith('APIC'):
                        apic = audio.tags[key]
                        cover_count += 1
                        
                        # Determinar extensión
                        if apic.mime == 'image/jpeg':
                            ext = '.jpg'
                        elif apic.mime == 'image/png':
                            ext = '.png'
                        elif apic.mime == 'image/gif':
                            ext = '.gif'
                        else:
                            ext = '.jpg'
                        
                        # Nombre personalizado o automático
                        if custom_name:
                            cover_filename = f"{custom_name}{ext}"
                        else:
                            base_name = file_path.stem
                            cover_filename = f"{base_name}_cover{f'_{cover_count}' if cover_count > 1 else ''}{ext}"
                        
                        cover_path = output_dir / cover_filename
                        
                        # Guardar imagen
                        with open(cover_path, 'wb') as f:
                            f.write(apic.data)
                        
                        print(f"🖼️ Portada {cover_count} extraída:")
                        print(f"   📁 Archivo: {cover_path}")
                        print(f"   📄 Formato: {apic.mime}")
                        print(f"   📏 Tamaño: {len(apic.data):,} bytes ({len(apic.data)/1024:.1f} KB)")
                        print(f"   📐 Tipo: {apic.type} ({'Portada frontal' if apic.type == 3 else 'Otra'})")
                        
                        extracted_files.append({
                            "archivo": str(cover_path),
                            "formato": apic.mime,
                            "tamaño_bytes": len(apic.data),
                            "tipo": apic.type
                        })
                
                if cover_count == 0:
                    print("⚠️ No se encontraron portadas en el archivo")
                    return None
                
                return extracted_files
        
        elif METADATA_TYPE == "eyed3":
            import eyed3
            audiofile = eyed3.load(file_path)
            
            if audiofile.tag and audiofile.tag.images:
                extracted_files = []
                
                for i, image in enumerate(audiofile.tag.images):
                    # Determinar extensión
                    if image.mime_type == 'image/jpeg':
                        ext = '.jpg'
                    elif image.mime_type == 'image/png':
                        ext = '.png'
                    else:
                        ext = '.jpg'
                    
                    # Nombre personalizado o automático
                    if custom_name:
                        cover_filename = f"{custom_name}{f'_{i+1}' if len(audiofile.tag.images) > 1 else ''}{ext}"
                    else:
                        base_name = file_path.stem
                        cover_filename = f"{base_name}_cover{f'_{i+1}' if len(audiofile.tag.images) > 1 else ''}{ext}"
                    
                    cover_path = output_dir / cover_filename
                    
                    # Guardar imagen
                    with open(cover_path, 'wb') as f:
                        f.write(image.image_data)
                    
                    print(f"🖼️ Portada {i+1} extraída:")
                    print(f"   📁 Archivo: {cover_path}")
                    print(f"   📄 Formato: {image.mime_type}")
                    print(f"   📏 Tamaño: {len(image.image_data):,} bytes ({len(image.image_data)/1024:.1f} KB)")
                    
                    extracted_files.append({
                        "archivo": str(cover_path),
                        "formato": image.mime_type,
                        "tamaño_bytes": len(image.image_data)
                    })
                
                return extracted_files
            else:
                print("⚠️ No se encontraron portadas en el archivo")
                return None
        
    except Exception as e:
        print(f"❌ Error al extraer portada: {e}")
        return None

def extract_covers_from_directory(directory, output_dir=None):
    """Extrae portadas de todos los MP3 en un directorio"""
    directory = Path(directory)
    
    if not directory.exists():
        print(f"❌ Directorio no encontrado: {directory}")
        return
    
    mp3_files = list(directory.glob("*.mp3"))
    
    if not mp3_files:
        print(f"❌ No se encontraron archivos MP3 en: {directory}")
        return
    
    print(f"🔍 Encontrados {len(mp3_files)} archivos MP3")
    print("="*60)
    
    total_extracted = 0
    total_files = 0
    
    for mp3_file in mp3_files:
        total_files += 1
        print(f"\n📁 Procesando {total_files}/{len(mp3_files)}: {mp3_file.name}")
        
        extracted = extract_cover_from_mp3(mp3_file, output_dir)
        if extracted:
            total_extracted += len(extracted)
    
    print(f"\n🎉 Proceso completado:")
    print(f"   📁 Archivos MP3 procesados: {total_files}")
    print(f"   🖼️ Portadas extraídas: {total_extracted}")

def find_mp3_files():
    """Busca archivos MP3 en carpetas comunes"""
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
    print("🖼️ Extractor de Portadas MP3")
    print("=" * 50)
    
    if len(sys.argv) == 1:
        # Buscar archivos MP3 automáticamente
        mp3_files = find_mp3_files()
        
        if mp3_files:
            print(f"🔍 Encontrados {len(mp3_files)} archivos MP3")
            
            # Crear carpeta para portadas
            covers_dir = Path("assets/covers")
            covers_dir.mkdir(parents=True, exist_ok=True)
            
            total_extracted = 0
            for i, mp3_file in enumerate(mp3_files, 1):
                print(f"\n📁 Procesando {i}/{len(mp3_files)}: {mp3_file.name}")
                extracted = extract_cover_from_mp3(mp3_file, covers_dir)
                if extracted:
                    total_extracted += len(extracted)
            
            print(f"\n🎉 Proceso completado:")
            print(f"   📁 Archivos MP3 procesados: {len(mp3_files)}")
            print(f"   🖼️ Portadas extraídas: {total_extracted}")
            print(f"   📂 Guardadas en: {covers_dir}")
        else:
            print("❌ No se encontraron archivos MP3")
            print("\n💡 Uso:")
            print(f"   python {__file__} archivo.mp3                    # Extraer de un archivo")
            print(f"   python {__file__} archivo.mp3 carpeta_destino   # Extraer a carpeta específica")
            print(f"   python {__file__} carpeta/                      # Extraer de todos los MP3 en carpeta")
    
    elif len(sys.argv) == 2:
        target = Path(sys.argv[1])
        
        if target.is_file() and target.suffix.lower() == '.mp3':
            # Extraer de un archivo específico
            extracted = extract_cover_from_mp3(target)
            if extracted:
                print(f"\n✅ Extraídas {len(extracted)} portadas")
            else:
                print("\n❌ No se pudieron extraer portadas")
        
        elif target.is_dir():
            # Extraer de todos los MP3 en el directorio
            extract_covers_from_directory(target)
        
        else:
            print(f"❌ Archivo o directorio no válido: {target}")
    
    elif len(sys.argv) == 3:
        file_path = Path(sys.argv[1])
        output_dir = Path(sys.argv[2])
        
        if file_path.is_file() and file_path.suffix.lower() == '.mp3':
            output_dir.mkdir(exist_ok=True)
            extracted = extract_cover_from_mp3(file_path, output_dir)
            if extracted:
                print(f"\n✅ Extraídas {len(extracted)} portadas en: {output_dir}")
            else:
                print("\n❌ No se pudieron extraer portadas")
        else:
            print(f"❌ Archivo MP3 no válido: {file_path}")
    
    else:
        print("❌ Demasiados argumentos")
        print("\n💡 Uso:")
        print(f"   python {__file__}                            # Buscar y extraer automáticamente")
        print(f"   python {__file__} archivo.mp3                # Extraer de un archivo")
        print(f"   python {__file__} archivo.mp3 carpeta_dest   # Extraer a carpeta específica")
        print(f"   python {__file__} carpeta/                   # Extraer de directorio")