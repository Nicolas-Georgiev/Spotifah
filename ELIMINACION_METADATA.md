# ACTUALIZACIÓN: Eliminación de carpeta metadata

## 📋 Resumen de Cambios

Se han eliminado las referencias a la carpeta `data/metadata/` y sus archivos:
- ❌ `spotify_metadata.json` - Ya no se usa
- ❌ `youtube_metadata.json` - Ya no se usa

## 🎯 Razón del Cambio

Toda la información de canciones y playlists ahora se almacena **directamente en la base de datos** como JSON, eliminando la necesidad de archivos intermedios.

## ✅ Nuevo Flujo de Datos

### Antes (con metadata):
```
Spotify/YouTube → Descargar → Guardar metadata JSON → Leer metadata → Guardar en BD
```

### Ahora (sin metadata):
```
Spotify/YouTube → Descargar → Guardar DIRECTO en BD como JSON
```

## 🔧 Métodos Afectados

### spotify2mp3_model.py
- ❌ `_save_metadata_to_temp_file()` - Método obsoleto, comentado
- ❌ `get_metadata_file_path()` - Método obsoleto, comentado
- ❌ `get_current_metadata()` - Método obsoleto, comentado
- ❌ `get_all_tracks_metadata()` - Método obsoleto, comentado
- ❌ `get_download_session_info()` - Método obsoleto, comentado

### youtube2mp3_model.py
- ❌ `_save_metadata_to_json()` - Método obsoleto, comentado

## 📊 Nueva Estructura de Base de Datos

### Canciones
```python
# Guardar canción con toda la información
cancion_json = upsert_cancion_json({
    'titulo': 'Nombre de la canción',
    'artista': 'Artista',
    'album': 'Álbum',
    'duracion_seg': 300,
    'genero': 'Rock',
    'caratula_url': 'https://...',  # Se descarga y convierte a BLOB automáticamente
    'plataforma_origen': 'Spotify',
    'url_origen': 'spotify:track:...',
    'ruta_local': '/path/to/song.mp3'
})

# El JSON devuelto incluye:
# - caratula_base64: Imagen lista para usar en HTML
# - id_cancion: ID asignado en la BD
# - Todos los campos proporcionados
```

### Playlists Completas
```python
# Guardar playlist con todas sus canciones en un solo JSON
playlist_json = guardar_playlist_json_completa(
    id_usuario=1,
    nombre='Mi Playlist',
    descripcion='Descripción',
    canciones=[id1, id2, id3],  # Lista de IDs de canciones
    publica=True,
    caratula_url='https://...'  # Se descarga y convierte a BLOB automáticamente
)

# El JSON devuelto incluye:
# - Toda la información de la playlist
# - Lista completa de canciones con todos sus datos
# - caratula_base64: Imagen de la playlist lista para usar
# - total_canciones: Número de canciones
# - duracion_total: Duración total en segundos
```

## 🖼️ Manejo de Imágenes

Las imágenes ahora se almacenan como **BLOB** en la base de datos y se devuelven como **base64** para visualización:

```python
# Imagen desde URL (se descarga automáticamente)
cancion = upsert_cancion_json({
    'titulo': 'Mi canción',
    'caratula_url': 'https://ejemplo.com/imagen.jpg'
})

# Imagen desde archivo local
cancion = upsert_cancion_json({
    'titulo': 'Mi canción',
    'caratula_archivo': '/path/to/imagen.jpg'
})

# Imagen ya en base64
cancion = upsert_cancion_json({
    'titulo': 'Mi canción',
    'caratula_base64': 'iVBORw0KGgo...'
})

# Usar imagen en HTML
html = f'<img src="data:image/jpeg;base64,{cancion["caratula_base64"]}" />'
```

## 📦 Ventajas del Nuevo Sistema

1. **Simplicidad**: Un solo lugar para todos los datos (la BD)
2. **Consistencia**: No hay archivos JSON que puedan desincronizarse
3. **Atomicidad**: Todo se guarda en una sola operación
4. **Portabilidad**: Un solo archivo .db contiene todo
5. **Eficiencia**: No hay lecturas/escrituras de archivos adicionales
6. **Imágenes embebidas**: Las imágenes viajan con los datos en el JSON

## 🔄 Compatibilidad

El sistema sigue siendo compatible con el formato antiguo:
- Si una playlist no tiene `playlist_json`, se construye desde `playlist_canciones`
- Los métodos antiguos siguen funcionando (aunque usan el nuevo sistema por debajo)

## 📝 Archivos Modificados

- `src/model/db_adapter.py` - Nuevas funciones agregadas
- `src/model/spotify2mp3_model.py` - Métodos metadata comentados
- `src/model/youtube2mp3_model.py` - Método metadata comentado
- `src/databaseManager/db.py` - Schema actualizado con nuevos campos

## 🗑️ Limpieza Opcional

Si quieres eliminar completamente la carpeta metadata:

```python
import os
import shutil

metadata_path = 'data/metadata'
if os.path.exists(metadata_path):
    shutil.rmtree(metadata_path)
    print(f"🗑️ Carpeta {metadata_path} eliminada")
```

O desde PowerShell:
```powershell
Remove-Item -Path "data\metadata" -Recurse -Force
Write-Host "🗑️ Carpeta metadata eliminada"
```

## 📚 Documentación Adicional

- `ejemplos_playlist_json_completa.py` - Ejemplos de uso del nuevo sistema
- `documentation/json_database_usage.md` - Guía completa de operaciones JSON
- `documentation/upgrade_to_json.md` - Guía de migración

## ✨ Nuevas Funciones Disponibles

### Para Canciones
- `upsert_cancion_json(metadata)` - Guarda y devuelve JSON completo
- `get_cancion_json(id/titulo/artista)` - Obtiene canción como JSON
- `get_todas_canciones_json()` - Lista todas las canciones
- `guardar_cancion_desde_json(json_str/dict)` - Importa desde JSON

### Para Playlists
- `guardar_playlist_json_completa()` - Guarda playlist completa
- `obtener_playlist_json_completa(id)` - Obtiene playlist completa
- `actualizar_playlist_json_completa(id, ...)` - Actualiza playlist

### Para Imágenes
- `imagen_url_a_blob(url)` - Descarga imagen a BLOB
- `imagen_archivo_a_blob(ruta)` - Lee imagen local a BLOB
- `blob_a_base64(blob)` - Convierte BLOB a base64
- `base64_a_blob(base64)` - Convierte base64 a BLOB
- `blob_a_data_uri(blob, mime)` - Crea Data URI completo

---

**Última actualización:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
