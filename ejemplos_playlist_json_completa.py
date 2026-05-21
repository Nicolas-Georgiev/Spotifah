#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejemplos de uso de playlists completas como JSON con imágenes BLOB.
Demuestra las nuevas funcionalidades implementadas.
"""

import os
import sys
import json

# Asegurar que podemos importar desde src
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from model.db_adapter import (
    guardar_playlist_json_completa,
    obtener_playlist_json_completa,
    actualizar_playlist_json_completa,
    upsert_cancion_json,
    imagen_url_a_blob,
    blob_a_base64,
    blob_a_data_uri
)


def ejemplo_1_guardar_playlist_completa():
    """Ejemplo 1: Guardar una playlist completa con todas sus canciones en un JSON"""
    print("\n" + "="*70)
    print("EJEMPLO 1: Guardar playlist completa como JSON único")
    print("="*70)
    
    # Primero, asegurémonos de tener algunas canciones en la BD
    print("\n📥 Guardando canciones de ejemplo...")
    cancion1 = upsert_cancion_json({
        'titulo': 'Bohemian Rhapsody',
        'artista': 'Queen',
        'album': 'A Night at the Opera',
        'duracion_seg': 354,
        'genero': 'Rock',
        'caratula_url': 'https://picsum.photos/300/300?random=1'
    })
    
    cancion2 = upsert_cancion_json({
        'titulo': 'Stairway to Heaven',
        'artista': 'Led Zeppelin',
        'album': 'Led Zeppelin IV',
        'duracion_seg': 482,
        'genero': 'Rock'
    })
    
    cancion3 = upsert_cancion_json({
        'titulo': 'Hotel California',
        'artista': 'Eagles',
        'album': 'Hotel California',
        'duracion_seg': 391,
        'genero': 'Rock'
    })
    
    if not all([cancion1, cancion2, cancion3]):
        print("❌ Error al guardar canciones de ejemplo")
        return None
    
    print(f"✅ Canciones guardadas: {cancion1['id_cancion']}, {cancion2['id_cancion']}, {cancion3['id_cancion']}")
    
    # Ahora crear la playlist completa
    print("\n📚 Creando playlist completa...")
    playlist = guardar_playlist_json_completa(
        id_usuario=1,
        nombre="Rock Clásico",
        descripcion="Las mejores canciones de rock clásico de todos los tiempos",
        canciones=[cancion1['id_cancion'], cancion2['id_cancion'], cancion3['id_cancion']],
        publica=True,
        caratula_url='https://picsum.photos/400/400?random=playlist1'
    )
    
    if playlist:
        print("\n✅ Playlist guardada exitosamente!")
        print(f"   ID: {playlist['id_playlist']}")
        print(f"   Nombre: {playlist['nombre']}")
        print(f"   Descripción: {playlist['descripcion']}")
        print(f"   Total canciones: {playlist['total_canciones']}")
        print(f"   Duración total: {playlist['duracion_total']} segundos")
        print(f"   ¿Tiene carátula?: {'Sí' if playlist.get('caratula_base64') else 'No'}")
        
        print("\n🎵 Canciones incluidas:")
        for cancion in playlist['canciones']:
            print(f"   {cancion['orden']}. {cancion['titulo']} - {cancion['artista']} ({cancion['duracion_seg']}s)")
        
        print("\n📄 JSON completo (primeros 500 caracteres):")
        json_str = json.dumps(playlist, indent=2, ensure_ascii=False)
        print(json_str[:500] + "..." if len(json_str) > 500 else json_str)
        
        return playlist['id_playlist']
    else:
        print("❌ Error al guardar playlist")
        return None


def ejemplo_2_obtener_playlist_completa(id_playlist):
    """Ejemplo 2: Obtener una playlist completa desde la BD"""
    print("\n" + "="*70)
    print("EJEMPLO 2: Obtener playlist completa desde BD")
    print("="*70)
    
    print(f"\n🔍 Obteniendo playlist ID {id_playlist}...")
    playlist = obtener_playlist_json_completa(id_playlist)
    
    if playlist:
        print("\n✅ Playlist obtenida!")
        print(f"   Nombre: {playlist['nombre']}")
        print(f"   Creada: {playlist.get('fecha_creacion', 'N/A')}")
        print(f"   Total canciones: {len(playlist['canciones'])}")
        print(f"   Duración total: {playlist.get('duracion_total', 0)} segundos ({playlist.get('duracion_total', 0) // 60} minutos)")
        
        print("\n🎵 Lista de canciones:")
        for cancion in playlist['canciones']:
            print(f"   {cancion['orden']}. {cancion['titulo']}")
            print(f"      Artista: {cancion['artista']}")
            print(f"      Álbum: {cancion.get('album', 'N/A')}")
            print(f"      Duración: {cancion['duracion_seg']}s")
            if cancion.get('caratula_base64'):
                print(f"      ✅ Tiene carátula en base64 ({len(cancion['caratula_base64'])} chars)")
        
        # Si tiene carátula de playlist, mostrar info
        if playlist.get('caratula_base64'):
            print(f"\n🖼️ Carátula de playlist disponible ({len(playlist['caratula_base64'])} caracteres en base64)")
            print(f"   Para usar en HTML: <img src=\"data:image/jpeg;base64,{playlist['caratula_base64'][:50]}...\" />")
        
        return playlist
    else:
        print("❌ No se pudo obtener la playlist")
        return None


def ejemplo_3_actualizar_playlist(id_playlist):
    """Ejemplo 3: Actualizar una playlist completa"""
    print("\n" + "="*70)
    print("EJEMPLO 3: Actualizar playlist completa")
    print("="*70)
    
    # Agregar una nueva canción
    print("\n📥 Agregando nueva canción...")
    nueva_cancion = upsert_cancion_json({
        'titulo': 'Sweet Child O Mine',
        'artista': 'Guns N Roses',
        'album': 'Appetite for Destruction',
        'duracion_seg': 356,
        'genero': 'Rock'
    })
    
    if not nueva_cancion:
        print("❌ Error al agregar canción")
        return False
    
    # Obtener playlist actual
    print(f"\n🔍 Obteniendo playlist actual...")
    playlist_actual = obtener_playlist_json_completa(id_playlist)
    
    if not playlist_actual:
        print("❌ No se pudo obtener playlist")
        return False
    
    # Agregar la nueva canción a la lista
    canciones_ids = [c['id_cancion'] for c in playlist_actual['canciones']]
    canciones_ids.append(nueva_cancion['id_cancion'])
    
    print(f"\n🔄 Actualizando playlist con {len(canciones_ids)} canciones...")
    playlist_actualizada = actualizar_playlist_json_completa(
        id_playlist=id_playlist,
        nombre="Rock Clásico [Actualizada]",
        canciones=canciones_ids
    )
    
    if playlist_actualizada:
        print("\n✅ Playlist actualizada!")
        print(f"   Nuevo nombre: {playlist_actualizada['nombre']}")
        print(f"   Total canciones: {playlist_actualizada['total_canciones']}")
        print(f"   Duración total: {playlist_actualizada['duracion_total']}s")
        
        print("\n🎵 Nuevas canciones:")
        for cancion in playlist_actualizada['canciones']:
            print(f"   {cancion['orden']}. {cancion['titulo']} - {cancion['artista']}")
        
        return True
    else:
        print("❌ Error al actualizar playlist")
        return False


def ejemplo_4_playlist_con_imagen_local():
    """Ejemplo 4: Crear playlist con imagen desde archivo local (simulado)"""
    print("\n" + "="*70)
    print("EJEMPLO 4: Playlist con imagen local (base64)")
    print("="*70)
    
    # Simular una imagen en base64 (un pixel rojo de 1x1)
    imagen_base64_ejemplo = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="
    )
    
    print("\n📚 Creando playlist con imagen local...")
    playlist = guardar_playlist_json_completa(
        id_usuario=1,
        nombre="Mi Playlist Personalizada",
        descripcion="Playlist con carátula personalizada",
        canciones=[],  # Vacía por ahora
        publica=False,
        caratula_base64=imagen_base64_ejemplo
    )
    
    if playlist:
        print("\n✅ Playlist creada con carátula!")
        print(f"   ID: {playlist['id_playlist']}")
        print(f"   Nombre: {playlist['nombre']}")
        print(f"   Tiene carátula: {'Sí' if playlist.get('caratula_base64') else 'No'}")
        
        if playlist.get('caratula_base64'):
            print(f"\n🖼️ Carátula almacenada en base64")
            print(f"   Tamaño: {len(playlist['caratula_base64'])} caracteres")
            print(f"   Primeros 100 chars: {playlist['caratula_base64'][:100]}...")
            
            # Ejemplo de uso en HTML
            print("\n💡 Uso en HTML:")
            print(f'   <img src="data:image/png;base64,{playlist["caratula_base64"][:50]}..." />')
        
        return playlist['id_playlist']
    else:
        print("❌ Error al crear playlist")
        return None


def ejemplo_5_exportar_playlist_completa(id_playlist):
    """Ejemplo 5: Exportar playlist completa a archivo JSON"""
    print("\n" + "="*70)
    print("EJEMPLO 5: Exportar playlist completa a archivo JSON")
    print("="*70)
    
    print(f"\n🔍 Obteniendo playlist {id_playlist}...")
    playlist = obtener_playlist_json_completa(id_playlist)
    
    if not playlist:
        print("❌ No se pudo obtener playlist")
        return False
    
    # Crear directorio de exportación
    export_dir = os.path.join(os.path.dirname(__file__), 'data', 'temp')
    os.makedirs(export_dir, exist_ok=True)
    
    export_file = os.path.join(export_dir, f'playlist_{id_playlist}_completa.json')
    
    print(f"\n💾 Exportando a {export_file}...")
    
    try:
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(playlist, f, indent=2, ensure_ascii=False)
        
        file_size = os.path.getsize(export_file)
        print(f"\n✅ Playlist exportada exitosamente!")
        print(f"   Archivo: {export_file}")
        print(f"   Tamaño: {file_size:,} bytes ({file_size / 1024:.2f} KB)")
        print(f"   Canciones incluidas: {len(playlist['canciones'])}")
        
        # Mostrar estructura del JSON
        print("\n📋 Estructura del JSON exportado:")
        print(f"   - id_playlist: {playlist.get('id_playlist')}")
        print(f"   - nombre: {playlist.get('nombre')}")
        print(f"   - descripcion: {playlist.get('descripcion')}")
        print(f"   - canciones: [{len(playlist['canciones'])} elementos]")
        print(f"   - total_canciones: {playlist.get('total_canciones')}")
        print(f"   - duracion_total: {playlist.get('duracion_total')}s")
        print(f"   - caratula_base64: {'Sí (' + str(len(playlist.get('caratula_base64', ''))) + ' chars)' if playlist.get('caratula_base64') else 'No'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al exportar: {e}")
        return False


def main():
    """Ejecuta todos los ejemplos"""
    print("\n" + "🎵"*35)
    print("EJEMPLOS DE PLAYLISTS COMPLETAS COMO JSON CON IMÁGENES BLOB")
    print("🎵"*35)
    
    try:
        # Ejemplo 1: Guardar playlist completa
        id_playlist = ejemplo_1_guardar_playlist_completa()
        
        if id_playlist:
            # Ejemplo 2: Obtener playlist completa
            ejemplo_2_obtener_playlist_completa(id_playlist)
            
            # Ejemplo 3: Actualizar playlist
            ejemplo_3_actualizar_playlist(id_playlist)
            
            # Ejemplo 5: Exportar a JSON
            ejemplo_5_exportar_playlist_completa(id_playlist)
        
        # Ejemplo 4: Playlist con imagen local
        ejemplo_4_playlist_con_imagen_local()
        
        print("\n" + "="*70)
        print("✅ TODOS LOS EJEMPLOS COMPLETADOS")
        print("="*70)
        
        print("\n📋 Resumen de características:")
        print("   ✅ Playlists se guardan como JSON completo")
        print("   ✅ Todas las canciones incluidas en un solo campo")
        print("   ✅ Imágenes almacenadas como BLOB en la BD")
        print("   ✅ Imágenes decodificadas a base64 para visualización")
        print("   ✅ Compatibilidad con formato antiguo (playlist_canciones)")
        print("   ✅ Exportación completa a archivos JSON")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
