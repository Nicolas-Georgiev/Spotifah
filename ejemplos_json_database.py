#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejemplos de uso de las funciones JSON de la base de datos.
Este script demuestra todas las operaciones disponibles.
"""

import os
import sys
import json

# Asegurar que podemos importar desde src
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from model.db_adapter import (
    upsert_cancion_json,
    guardar_cancion_desde_json,
    get_cancion_json,
    get_todas_canciones_json,
    get_playlist_json,
    get_todas_playlists_json
)


def ejemplo_1_guardar_cancion_dict():
    """Ejemplo 1: Guardar una canción desde un diccionario"""
    print("\n" + "="*60)
    print("EJEMPLO 1: Guardar canción desde diccionario")
    print("="*60)
    
    metadata = {
        'titulo': 'Bohemian Rhapsody',
        'artista': 'Queen',
        'album': 'A Night at the Opera',
        'duracion_seg': 354,
        'genero': 'Rock',
        'plataforma_origen': 'Spotify',
        'url_origen': 'https://open.spotify.com/track/example',
        'ruta_local': '/music/queen/bohemian_rhapsody.mp3',
        'caratula_url': 'https://example.com/cover.jpg',
    }
    
    print("\n📥 Guardando canción...")
    cancion_json = upsert_cancion_json(metadata)
    
    if cancion_json:
        print("\n✅ Canción guardada exitosamente!")
        print(f"   ID: {cancion_json['id_cancion']}")
        print(f"   Título: {cancion_json['titulo']}")
        print(f"   Artista: {cancion_json['artista']}")
        print(f"   Álbum: {cancion_json['album']}")
        print(f"   Duración: {cancion_json['duracion_seg']} segundos")
        print(f"   Fecha importación: {cancion_json['fecha_importacion']}")
        
        print("\n📄 JSON completo:")
        print(json.dumps(cancion_json, indent=2, ensure_ascii=False))
        
        return cancion_json['id_cancion']
    else:
        print("❌ Error al guardar la canción")
        return None


def ejemplo_2_guardar_desde_json_string():
    """Ejemplo 2: Guardar una canción desde un string JSON"""
    print("\n" + "="*60)
    print("EJEMPLO 2: Guardar canción desde string JSON")
    print("="*60)
    
    json_string = '''
    {
        "titulo": "Stairway to Heaven",
        "artista": "Led Zeppelin",
        "album": "Led Zeppelin IV",
        "duracion_seg": 482,
        "genero": "Rock",
        "plataforma_origen": "YouTube"
    }
    '''
    
    print("\n📥 Guardando canción desde JSON string...")
    cancion_json = guardar_cancion_desde_json(json_string)
    
    if cancion_json:
        print("\n✅ Canción guardada exitosamente!")
        print(f"   ID: {cancion_json['id_cancion']}")
        print(f"   Título: {cancion_json['titulo']}")
        print(f"   Artista: {cancion_json['artista']}")
        return cancion_json['id_cancion']
    else:
        print("❌ Error al guardar la canción")
        return None


def ejemplo_3_obtener_cancion_por_id(id_cancion):
    """Ejemplo 3: Obtener una canción por ID"""
    print("\n" + "="*60)
    print("EJEMPLO 3: Obtener canción por ID")
    print("="*60)
    
    print(f"\n🔍 Buscando canción con ID {id_cancion}...")
    cancion = get_cancion_json(id_cancion=id_cancion)
    
    if cancion:
        print("\n✅ Canción encontrada!")
        print(f"   Título: {cancion['titulo']}")
        print(f"   Artista: {cancion['artista']}")
        print(f"   Álbum: {cancion['album']}")
        print(f"   Plataforma: {cancion['plataforma_origen']}")
        print(f"   Ruta local: {cancion['ruta_local']}")
    else:
        print("❌ Canción no encontrada")


def ejemplo_4_obtener_cancion_por_titulo_artista():
    """Ejemplo 4: Obtener una canción por título y artista"""
    print("\n" + "="*60)
    print("EJEMPLO 4: Obtener canción por título y artista")
    print("="*60)
    
    titulo = "Bohemian Rhapsody"
    artista = "Queen"
    
    print(f"\n🔍 Buscando '{titulo}' de {artista}...")
    cancion = get_cancion_json(titulo=titulo, artista=artista)
    
    if cancion:
        print("\n✅ Canción encontrada!")
        print(f"   ID: {cancion['id_cancion']}")
        print(f"   Título: {cancion['titulo']}")
        print(f"   Artista: {cancion['artista']}")
        print(f"   Duración: {cancion['duracion_seg']}s")
        print(f"   Género: {cancion['genero']}")
    else:
        print("❌ Canción no encontrada")


def ejemplo_5_listar_todas_canciones():
    """Ejemplo 5: Listar todas las canciones"""
    print("\n" + "="*60)
    print("EJEMPLO 5: Listar todas las canciones")
    print("="*60)
    
    print("\n📚 Obteniendo todas las canciones...")
    canciones = get_todas_canciones_json()
    
    print(f"\n✅ Se encontraron {len(canciones)} canciones:")
    for i, cancion in enumerate(canciones, 1):
        print(f"\n{i}. {cancion['titulo']} - {cancion['artista']}")
        print(f"   ID: {cancion['id_cancion']} | Álbum: {cancion['album'] or 'N/A'}")
        print(f"   Duración: {cancion['duracion_seg']}s | Género: {cancion['genero'] or 'N/A'}")
        print(f"   Plataforma: {cancion['plataforma_origen']}")


def ejemplo_6_obtener_playlist():
    """Ejemplo 6: Obtener una playlist completa"""
    print("\n" + "="*60)
    print("EJEMPLO 6: Obtener playlist con todas sus canciones")
    print("="*60)
    
    id_playlist = 1  # Playlist de ejemplo de la BD semilla
    
    print(f"\n🔍 Obteniendo playlist {id_playlist}...")
    playlist = get_playlist_json(id_playlist=id_playlist)
    
    if playlist:
        print("\n✅ Playlist encontrada!")
        print(f"   Nombre: {playlist['nombre']}")
        print(f"   Descripción: {playlist['descripcion']}")
        print(f"   Creada por: {playlist['nombre_usuario']}")
        print(f"   Estado: {'Pública' if playlist['publica'] else 'Privada'}")
        print(f"   Fecha creación: {playlist['fecha_creacion']}")
        
        print(f"\n🎵 Canciones ({len(playlist['canciones'])}):")
        for cancion in playlist['canciones']:
            print(f"   {cancion['orden']}. {cancion['titulo']} - {cancion['artista']}")
            print(f"      Duración: {cancion['duracion_seg']}s | Género: {cancion['genero']}")
    else:
        print("❌ Playlist no encontrada")


def ejemplo_7_listar_todas_playlists():
    """Ejemplo 7: Listar todas las playlists"""
    print("\n" + "="*60)
    print("EJEMPLO 7: Listar todas las playlists")
    print("="*60)
    
    print("\n📚 Obteniendo todas las playlists...")
    playlists = get_todas_playlists_json()
    
    print(f"\n✅ Se encontraron {len(playlists)} playlists:")
    for playlist in playlists:
        print(f"\n• {playlist['nombre']} (ID: {playlist['id_playlist']})")
        print(f"  Creada por: {playlist['nombre_usuario']}")
        print(f"  Canciones: {playlist['num_canciones']}")
        print(f"  Estado: {'Pública' if playlist['publica'] else 'Privada'}")


def ejemplo_8_exportar_a_json():
    """Ejemplo 8: Exportar toda la biblioteca a un archivo JSON"""
    print("\n" + "="*60)
    print("EJEMPLO 8: Exportar biblioteca a archivo JSON")
    print("="*60)
    
    output_file = os.path.join(os.path.dirname(__file__), 'data', 'temp', 'biblioteca_export.json')
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    print("\n📚 Obteniendo todas las canciones...")
    canciones = get_todas_canciones_json()
    
    print(f"💾 Exportando {len(canciones)} canciones a {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(canciones, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Exportación completada!")
    print(f"   Archivo: {output_file}")
    print(f"   Tamaño: {os.path.getsize(output_file)} bytes")


def ejemplo_9_actualizar_cancion_existente():
    """Ejemplo 9: Actualizar una canción existente"""
    print("\n" + "="*60)
    print("EJEMPLO 9: Actualizar canción existente")
    print("="*60)
    
    # Guardar una canción
    metadata = {
        'titulo': 'Test Song',
        'artista': 'Test Artist',
        'plataforma_origen': 'local'
    }
    
    print("\n📥 Guardando canción inicial...")
    cancion_json = upsert_cancion_json(metadata)
    
    if cancion_json:
        print(f"✅ Canción guardada con ID {cancion_json['id_cancion']}")
        print(f"   Ruta local: {cancion_json['ruta_local']}")
        
        # Actualizar con nueva información
        print("\n🔄 Actualizando con nueva información...")
        metadata_actualizado = {
            'titulo': 'Test Song',
            'artista': 'Test Artist',
            'ruta_local': '/music/test/song.mp3',
            'caratula_url': 'https://example.com/new_cover.jpg'
        }
        
        cancion_actualizada = upsert_cancion_json(metadata_actualizado)
        
        if cancion_actualizada:
            print(f"✅ Canción actualizada (mismo ID: {cancion_actualizada['id_cancion']})")
            print(f"   Nueva ruta local: {cancion_actualizada['ruta_local']}")
            print(f"   Nueva carátula: {cancion_actualizada['caratula_url']}")


def main():
    """Ejecuta todos los ejemplos"""
    print("\n" + "🎵"*30)
    print("EJEMPLOS DE USO DE FUNCIONES JSON DE BASE DE DATOS")
    print("🎵"*30)
    
    try:
        # Ejemplo 1: Guardar canción desde diccionario
        id_cancion = ejemplo_1_guardar_cancion_dict()
        
        # Ejemplo 2: Guardar desde JSON string
        ejemplo_2_guardar_desde_json_string()
        
        # Ejemplo 3: Obtener por ID
        if id_cancion:
            ejemplo_3_obtener_cancion_por_id(id_cancion)
        
        # Ejemplo 4: Obtener por título y artista
        ejemplo_4_obtener_cancion_por_titulo_artista()
        
        # Ejemplo 5: Listar todas las canciones
        ejemplo_5_listar_todas_canciones()
        
        # Ejemplo 6: Obtener playlist completa
        ejemplo_6_obtener_playlist()
        
        # Ejemplo 7: Listar todas las playlists
        ejemplo_7_listar_todas_playlists()
        
        # Ejemplo 8: Exportar a JSON
        ejemplo_8_exportar_a_json()
        
        # Ejemplo 9: Actualizar canción
        ejemplo_9_actualizar_cancion_existente()
        
        print("\n" + "="*60)
        print("✅ TODOS LOS EJEMPLOS COMPLETADOS")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
