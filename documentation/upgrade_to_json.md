# Guía de Actualización a Funciones JSON

Este documento muestra cómo actualizar el código existente para usar las nuevas funciones JSON de la base de datos.

## ⚠️ IMPORTANTE: Actualización Opcional

La función `upsert_cancion()` **sigue funcionando** exactamente igual que antes. Las actualizaciones descritas aquí son **opcionales** y solo necesarias si quieres obtener el JSON completo de la canción guardada.

## 🎵 Actualización en youtube2mp3_model.py

### ❌ Código Actual (línea ~558)
```python
from model.db_adapter import upsert_cancion, registrar_descarga

# ... en el método convert() ...

metadata_bd = {
    'titulo':           video_info.get('title', ''),
    'artista':          video_info.get('author', ''),
    'duracion_seg':     video_info.get('length') or None,
    'genero':           genre_str or None,
    'plataforma_origen': 'YouTube',
    'url_origen':       url,
    'ruta_local':       mp3_abs,
    'caratula_url':     video_info.get('thumbnail_url') or None,
}
id_cancion = upsert_cancion(metadata_bd)
registrar_descarga(id_cancion, formato='mp3')
```

### ✅ Código Actualizado (con JSON)
```python
from model.db_adapter import upsert_cancion_json, registrar_descarga

# ... en el método convert() ...

metadata_bd = {
    'titulo':           video_info.get('title', ''),
    'artista':          video_info.get('author', ''),
    'duracion_seg':     video_info.get('length') or None,
    'genero':           genre_str or None,
    'plataforma_origen': 'YouTube',
    'url_origen':       url,
    'ruta_local':       mp3_abs,
    'caratula_url':     video_info.get('thumbnail_url') or None,
}

# Ahora obtenemos el JSON completo
cancion_json = upsert_cancion_json(metadata_bd)

if cancion_json:
    id_cancion = cancion_json['id_cancion']
    registrar_descarga(id_cancion, formato='mp3')
    
    # BONUS: Ahora tienes acceso a todos los datos
    print(f"💾 Canción guardada: {cancion_json['titulo']} (ID: {id_cancion})")
    print(f"   Ruta: {cancion_json['ruta_local']}")
    print(f"   Fecha: {cancion_json['fecha_importacion']}")
    
    # Podrías retornar el JSON en lugar de solo el path
    # return {'mp3_path': mp3_file, 'metadata': cancion_json}
```

### 🎁 Ventajas de la actualización
1. **Más información**: Tienes acceso inmediato a todos los campos de la BD
2. **Debugging**: Puedes verificar exactamente qué se guardó
3. **Extensibilidad**: Facilita futuras mejoras (como retornar metadata completa)
4. **Trazabilidad**: Fecha de importación, ID asignado, etc.

## 🎼 Actualización en spotify2mp3_model.py

### ❌ Código Actual (línea ~1053)
```python
from model.db_adapter import upsert_cancion, registrar_descarga

# ... en el método download_and_convert() ...

_album = track_info.get('album', '')
if isinstance(_album, dict):
    _album = _album.get('name', '')
_artistas = track_info.get('artists', [''])
_artista = _artistas[0] if _artistas else ''

metadata_bd = {
    'titulo':            track_info.get('name', ''),
    'artista':           _artista,
    'album':             _album,
    'duracion_seg':      (track_info.get('duration_ms') or 0) // 1000,
    'plataforma_origen': 'Spotify',
    'url_origen':        spotify_url,
    'ruta_local':        os.path.abspath(mp3_path),
    'caratula_url':      track_info['images'][0]['url'] if track_info.get('images') else None,
}
id_cancion = upsert_cancion(metadata_bd)
registrar_descarga(id_cancion, formato='mp3')
```

### ✅ Código Actualizado (con JSON)
```python
from model.db_adapter import upsert_cancion_json, registrar_descarga

# ... en el método download_and_convert() ...

_album = track_info.get('album', '')
if isinstance(_album, dict):
    _album = _album.get('name', '')
_artistas = track_info.get('artists', [''])
_artista = _artistas[0] if _artistas else ''

metadata_bd = {
    'titulo':            track_info.get('name', ''),
    'artista':           _artista,
    'album':             _album,
    'duracion_seg':      (track_info.get('duration_ms') or 0) // 1000,
    'plataforma_origen': 'Spotify',
    'url_origen':        spotify_url,
    'ruta_local':        os.path.abspath(mp3_path),
    'caratula_url':      track_info['images'][0]['url'] if track_info.get('images') else None,
}

# Obtener JSON completo
cancion_json = upsert_cancion_json(metadata_bd)

if cancion_json:
    id_cancion = cancion_json['id_cancion']
    registrar_descarga(id_cancion, formato='mp3')
    
    # BONUS: Información completa disponible
    print(f"💾 Spotify → MP3: {cancion_json['titulo']} - {cancion_json['artista']}")
    print(f"   Álbum: {cancion_json['album']}")
    print(f"   Duración: {cancion_json['duracion_seg']}s")
    print(f"   Guardada: {cancion_json['fecha_importacion']}")
    
    # Podrías retornar metadata completa
    # return {'mp3_path': mp3_path, 'metadata': cancion_json}
```

## 📊 Comparación Rápida

| Aspecto | `upsert_cancion()` | `upsert_cancion_json()` |
|---------|-------------------|------------------------|
| **Retorna** | Solo `id_cancion` (int) | JSON completo (dict) |
| **Uso actual** | ✅ Ya implementado | 🆕 Nueva función |
| **Compatibilidad** | 100% compatible | Requiere cambio de import |
| **Información** | Mínima | Completa |
| **Recomendado para** | Casos simples | Cuando necesitas más datos |

## 🔧 Pasos para actualizar un archivo

1. **Cambiar el import:**
   ```python
   # Antes
   from model.db_adapter import upsert_cancion, registrar_descarga
   
   # Después  
   from model.db_adapter import upsert_cancion_json, registrar_descarga
   ```

2. **Actualizar la llamada:**
   ```python
   # Antes
   id_cancion = upsert_cancion(metadata_bd)
   
   # Después
   cancion_json = upsert_cancion_json(metadata_bd)
   if cancion_json:
       id_cancion = cancion_json['id_cancion']
   ```

3. **Usar los datos adicionales (opcional):**
   ```python
   # Ahora tienes acceso a:
   # - cancion_json['titulo']
   # - cancion_json['artista']
   # - cancion_json['album']
   # - cancion_json['duracion_seg']
   # - cancion_json['ruta_local']
   # - cancion_json['caratula_url']
   # - cancion_json['fecha_importacion']
   # ... y más
   ```

## 💡 Casos de uso donde la actualización es especialmente útil

### 1. Logging mejorado
```python
cancion_json = upsert_cancion_json(metadata_bd)
if cancion_json:
    logger.info(f"Canción guardada: {cancion_json['titulo']} - {cancion_json['artista']}")
    logger.debug(f"Ruta local: {cancion_json['ruta_local']}")
    logger.debug(f"Fecha: {cancion_json['fecha_importacion']}")
```

### 2. Retornar metadata completa
```python
def download_and_convert(self, spotify_url):
    # ... proceso de conversión ...
    
    cancion_json = upsert_cancion_json(metadata_bd)
    
    # Retornar un objeto completo en lugar de solo el path
    return {
        'success': True,
        'mp3_path': mp3_path,
        'metadata': cancion_json,
        'id_cancion': cancion_json['id_cancion']
    }
```

### 3. Notificaciones en UI
```python
cancion_json = upsert_cancion_json(metadata_bd)
if cancion_json:
    ui.mostrar_notificacion(
        f"✅ Descargada: {cancion_json['titulo']}\n"
        f"Artista: {cancion_json['artista']}\n"
        f"Guardada en: {cancion_json['ruta_local']}"
    )
```

### 4. Exportar a JSON para sincronización
```python
import json

cancion_json = upsert_cancion_json(metadata_bd)
if cancion_json:
    # Guardar en un archivo para sincronización posterior
    with open('ultimas_descargas.json', 'a', encoding='utf-8') as f:
        json.dump(cancion_json, f, ensure_ascii=False)
        f.write('\n')
```

## 🎯 Recomendación

- **Si el código actual funciona bien**: No es necesario actualizar
- **Si necesitas más información**: Actualiza a `upsert_cancion_json()`
- **Para nuevas funciones**: Usa directamente `upsert_cancion_json()`

## 📝 Notas adicionales

- Ambas funciones usan internamente el mismo código de base de datos
- No hay diferencia de rendimiento significativa
- La función `upsert_cancion()` seguirá existiendo para compatibilidad retroactiva
- Puedes mezclar ambos enfoques en diferentes partes del código sin problemas
