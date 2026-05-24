#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test rápido del nuevo sistema de playlists completas en JSON.
Verifica que todo funciona correctamente.
"""

import os
import sys

# Asegurar que podemos importar desde src
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from model.db_adapter import (
    guardar_playlist_json_completa,
    obtener_playlist_json_completa,
    actualizar_playlist_json_completa,
    upsert_cancion_json
)


def test_playlist_json_completa():
    """Test rápido de funcionalidades de playlist completa"""
    print("\n" + "="*70)
    print("TEST PLAYLIST JSON COMPLETA")
    print("="*70)
    
    errores = []
    
    # Test 1: Crear canciones de prueba
    print("\n[1/5] Creando canciones de prueba...")
    try:
        cancion1 = upsert_cancion_json({
            'titulo': 'Test Song 1',
            'artista': 'Test Artist',
            'duracion_seg': 180
        })
        cancion2 = upsert_cancion_json({
            'titulo': 'Test Song 2',
            'artista': 'Test Artist',
            'duracion_seg': 200
        })
        
        if cancion1 and cancion2:
            print(f"   ✅ Canciones creadas: ID {cancion1['id_cancion']}, ID {cancion2['id_cancion']}")
        else:
            errores.append("No se pudieron crear las canciones de prueba")
            print("   ❌ Error creando canciones")
            return False
    except Exception as e:
        errores.append(f"Error creando canciones: {e}")
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: Crear playlist completa
    print("\n[2/5] Creando playlist completa...")
    try:
        playlist = guardar_playlist_json_completa(
            id_usuario=1,
            nombre='Test Playlist',
            descripcion='Playlist de prueba',
            canciones=[cancion1['id_cancion'], cancion2['id_cancion']],
            publica=True
        )
        
        if playlist:
            id_playlist = playlist['id_playlist']
            print(f"   ✅ Playlist creada: ID {id_playlist}")
            print(f"      - Nombre: {playlist['nombre']}")
            print(f"      - Canciones: {playlist['total_canciones']}")
            print(f"      - Duración: {playlist['duracion_total']}s")
        else:
            errores.append("No se pudo crear la playlist")
            print("   ❌ Error creando playlist")
            return False
    except Exception as e:
        errores.append(f"Error creando playlist: {e}")
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 3: Obtener playlist completa
    print("\n[3/5] Obteniendo playlist completa...")
    try:
        playlist_obtenida = obtener_playlist_json_completa(id_playlist)
        
        if playlist_obtenida:
            print(f"   ✅ Playlist obtenida correctamente")
            print(f"      - ID: {playlist_obtenida['id_playlist']}")
            print(f"      - Nombre: {playlist_obtenida['nombre']}")
            print(f"      - Canciones: {len(playlist_obtenida['canciones'])}")
            
            # Verificar que tiene las canciones
            if len(playlist_obtenida['canciones']) == 2:
                print(f"      ✅ Tiene las 2 canciones esperadas")
            else:
                errores.append(f"Playlist debería tener 2 canciones, tiene {len(playlist_obtenida['canciones'])}")
                print(f"      ❌ Número incorrecto de canciones")
        else:
            errores.append("No se pudo obtener la playlist")
            print("   ❌ Error obteniendo playlist")
            return False
    except Exception as e:
        errores.append(f"Error obteniendo playlist: {e}")
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 4: Actualizar playlist
    print("\n[4/5] Actualizando playlist...")
    try:
        cancion3 = upsert_cancion_json({
            'titulo': 'Test Song 3',
            'artista': 'Test Artist',
            'duracion_seg': 220
        })
        
        playlist_actualizada = actualizar_playlist_json_completa(
            id_playlist=id_playlist,
            nombre='Test Playlist [Updated]',
            canciones=[cancion1['id_cancion'], cancion2['id_cancion'], cancion3['id_cancion']]
        )
        
        if playlist_actualizada:
            print(f"   ✅ Playlist actualizada correctamente")
            print(f"      - Nuevo nombre: {playlist_actualizada['nombre']}")
            print(f"      - Canciones: {playlist_actualizada['total_canciones']}")
            
            if playlist_actualizada['total_canciones'] == 3:
                print(f"      ✅ Ahora tiene 3 canciones")
            else:
                errores.append(f"Debería tener 3 canciones, tiene {playlist_actualizada['total_canciones']}")
                print(f"      ❌ Número incorrecto de canciones")
        else:
            errores.append("No se pudo actualizar la playlist")
            print("   ❌ Error actualizando playlist")
            return False
    except Exception as e:
        errores.append(f"Error actualizando playlist: {e}")
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 5: Verificar estructura JSON
    print("\n[5/5] Verificando estructura JSON...")
    try:
        campos_requeridos = ['id_playlist', 'nombre', 'descripcion', 'canciones', 
                           'total_canciones', 'duracion_total', 'id_usuario', 'publica']
        
        campos_faltantes = [c for c in campos_requeridos if c not in playlist_actualizada]
        
        if not campos_faltantes:
            print(f"   ✅ Estructura JSON correcta")
            print(f"      - Todos los campos requeridos presentes")
        else:
            errores.append(f"Campos faltantes: {', '.join(campos_faltantes)}")
            print(f"   ❌ Campos faltantes: {', '.join(campos_faltantes)}")
            return False
        
        # Verificar que cada canción tiene los campos básicos
        for cancion in playlist_actualizada['canciones']:
            if 'titulo' not in cancion or 'artista' not in cancion:
                errores.append("Canciones sin campos básicos")
                print(f"   ❌ Canción sin campos básicos")
                return False
        
        print(f"      ✅ Todas las canciones tienen campos básicos")
        
    except Exception as e:
        errores.append(f"Error verificando estructura: {e}")
        print(f"   ❌ Error: {e}")
        return False
    
    # Resumen
    print("\n" + "="*70)
    if not errores:
        print("✅ TODOS LOS TESTS PASARON")
        print("="*70)
        print("\n📋 Funcionalidades verificadas:")
        print("   ✅ Crear canciones")
        print("   ✅ Crear playlist completa")
        print("   ✅ Obtener playlist completa")
        print("   ✅ Actualizar playlist completa")
        print("   ✅ Estructura JSON correcta")
        return True
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        print("="*70)
        print("\n⚠️  Errores encontrados:")
        for i, error in enumerate(errores, 1):
            print(f"   {i}. {error}")
        return False


def main():
    """Función principal"""
    print("\n" + "🎵"*35)
    print("TEST RÁPIDO - PLAYLISTS JSON COMPLETAS")
    print("🎵"*35)
    
    try:
        exito = test_playlist_json_completa()
        
        if exito:
            print("\n💡 El sistema está funcionando correctamente")
            print("\n📚 Para más ejemplos, ejecuta:")
            print("   python ejemplos_playlist_json_completa.py")
        else:
            print("\n⚠️  Revisa los errores anteriores")
        
        input("\n[Presiona ENTER para salir]")
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        input("\n[Presiona ENTER para salir]")


if __name__ == '__main__':
    main()
