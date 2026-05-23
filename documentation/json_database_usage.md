# Uso de la Base de Datos con JSON

Este documento explica cómo usar las nuevas funciones JSON para interactuar con la base de datos de Spotifah.

## 📝 Visión General

Todas las operaciones de base de datos ahora soportan JSON como formato de entrada/salida:
- Al **guardar** una canción, la BD devuelve un JSON completo con todos los campos
- Al **leer** una canción, la BD devuelve un JSON con toda la información
- Las funciones pueden **aceptar** JSON (string o dict) para guardar datos

## 🎵 Funciones para Canciones

### 1. Guardar canción y obtener JSON completo

```python
from model.db_adapter import upsert_cancion_json

# Metadatos de la canción (pueden venir de Spotify, YouTube, etc.)
metadata = {
    'titulo': 'Bohemian Rhapsody',
    'artista': 'Queen',
    'album': 'A Night at the Opera',
    'duracion_seg': 354,
    'genero': 'Rock',
    'plataforma_origen': 'Spotify',
    'url_origen': 'https://open.spotify.com/track/...',
    'ruta_local': '/path/to/song.mp3',
    'caratula_url': 'https://i.scdn.co/image/...',
    'letra': 'Is this the real life?...'
}

# Guardar y obtener JSON completo
cancion_json = upsert_cancion_json(metadata)

if cancion_json:
    print(f"Canción guardada con ID: {cancion_json['id_cancion']}")
    print(f"Título: {cancion_json['titulo']}")
    print(f"Artista: {cancion_json['artista']}")
    # El JSON incluye TODOS los campos de la BD
```

**JSON retornado:**
```json
{
    "id_cancion": 5,
    "titulo": "Bohemian Rhapsody",
    "artista": "Queen",
    "album": "A Night at the Opera",
    "duracion_seg": 354,
    "genero": "Rock",
    "plataforma_origen": "Spotify",
    "url_origen": "https://open.spotify.com/track/...",
    "ruta_local": "/path/to/song.mp3",
    "caratula_url": "https://i.scdn.co/image/...",
    "letra": "Is this the real life?...",
    "fecha_importacion": "2026-05-20 10:30:00"
}
```

### 2. Guardar desde JSON (string o dict)

```python
from model.db_adapter import guardar_cancion_desde_json
import json

# Opción 1: Desde un diccionario
cancion_dict = {
    'titulo': 'Stairway to Heaven',
    'artista': 'Led Zeppelin',
    'duracion_seg': 482
}
cancion_json = guardar_cancion_desde_json(cancion_dict)

# Opción 2: Desde un string JSON
cancion_str = '{"titulo": "Hotel California", "artista": "Eagles", "duracion_seg": 391}'
cancion_json = guardar_cancion_desde_json(cancion_str)

if cancion_json:
    print(f"Guardada: {cancion_json['titulo']} - {cancion_json['artista']}")
```

### 3. Obtener canción por ID

```python
from model.db_adapter import get_cancion_json

# Buscar por ID
cancion = get_cancion_json(id_cancion=5)

if cancion:
    print(f"Encontrada: {cancion['titulo']}")
    print(f"Duración: {cancion['duracion_seg']} segundos")
    print(f"Ruta local: {cancion['ruta_local']}")
```

### 4. Obtener canción por título y artista

```python
from model.db_adapter import get_cancion_json

# Buscar por título y artista
cancion = get_cancion_json(titulo='Bohemian Rhapsody', artista='Queen')

if cancion:
    print(f"ID: {cancion['id_cancion']}")
    print(f"Álbum: {cancion['album']}")
```

### 5. Obtener todas las canciones

```python
from model.db_adapter import get_todas_canciones_json

# Obtener todas las canciones como lista de JSONs
canciones = get_todas_canciones_json()

print(f"Total de canciones: {len(canciones)}")
for cancion in canciones:
    print(f"  - {cancion['titulo']} por {cancion['artista']}")
```

## 📚 Funciones para Playlists

### 6. Obtener playlist con todas sus canciones

```python
from model.db_adapter import get_playlist_json

# Obtener playlist completa con todas sus canciones
playlist = get_playlist_json(id_playlist=1)

if playlist:
    print(f"Playlist: {playlist['nombre']}")
    print(f"Descripción: {playlist['descripcion']}")
    print(f"Creada por: {playlist['nombre_usuario']}")
    print(f"Canciones ({len(playlist['canciones'])}):")
    
    for cancion in playlist['canciones']:
        print(f"  {cancion['orden']}. {cancion['titulo']} - {cancion['artista']}")
```

**JSON retornado:**
```json
{
    "id_playlist": 1,
    "id_usuario": 1,
    "nombre": "Mis Favoritas",
    "descripcion": "Canciones que me gustan",
    "fecha_creacion": "2026-05-20 10:00:00",
    "publica": 1,
    "nombre_usuario": "Juan",
    "canciones": [
        {
            "id_cancion": 1,
            "titulo": "Canción 1",
            "artista": "Artista A",
            "album": "Album X",
            "duracion_seg": 210,
            "genero": "Pop",
            "plataforma_origen": "Spotify",
            "url_origen": "https://...",
            "ruta_local": "/path/to/song1.mp3",
            "caratula_url": "https://...",
            "letra": null,
            "fecha_importacion": "2026-05-19 15:00:00",
            "orden": 1
        },
        {
            "id_cancion": 2,
            "titulo": "Canción 2",
            "artista": "Artista B",
            ...
            "orden": 2
        }
    ]
}
```

### 7. Obtener todas las playlists

```python
from model.db_adapter import get_todas_playlists_json

# Todas las playlists
playlists = get_todas_playlists_json()

# O solo las de un usuario específico
playlists_usuario = get_todas_playlists_json(id_usuario=1)

for playlist in playlists:
    print(f"{playlist['nombre']} - {playlist['num_canciones']} canciones")
```

## 🔄 Migración desde funciones antiguas

### Antes (solo devolvía ID):
```python
from model.db_adapter import upsert_cancion

metadata = {'titulo': 'Song', 'artista': 'Artist'}
id_cancion = upsert_cancion(metadata)  # Devuelve solo el ID
```

### Ahora (devuelve JSON completo):
```python
from model.db_adapter import upsert_cancion_json

metadata = {'titulo': 'Song', 'artista': 'Artist'}
cancion_json = upsert_cancion_json(metadata)  # Devuelve JSON completo

if cancion_json:
    id_cancion = cancion_json['id_cancion']
    titulo = cancion_json['titulo']
    artista = cancion_json['artista']
    # ... todos los campos disponibles
```

## 💡 Ventajas del sistema JSON

1. **Consistencia**: Todas las funciones hablan el mismo "idioma" (JSON)
2. **Flexibilidad**: Fácil de serializar/deserializar para APIs
3. **Completitud**: Siempre obtienes todos los datos, no solo IDs
4. **Compatibilidad**: Funciona con diccionarios Python o strings JSON
5. **Trazabilidad**: Puedes ver exactamente qué se guardó y con qué valores

## 📋 Campos disponibles en el JSON de canción

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id_cancion` | int | ID único de la canción |
| `titulo` | str | Título de la canción |
| `artista` | str | Nombre del artista |
| `album` | str | Nombre del álbum |
| `duracion_seg` | int | Duración en segundos |
| `genero` | str | Género musical |
| `plataforma_origen` | str | Origen (Spotify, YouTube, local, etc.) |
| `url_origen` | str | URL original |
| `ruta_local` | str | Ruta del archivo MP3 local |
| `caratula_url` | str | URL de la carátula |
| `letra` | str | Letra de la canción |
| `fecha_importacion` | str | Fecha y hora de importación |

## 🎯 Casos de uso comunes

### Convertir de Spotify a MP3 y guardar
```python
from model.db_adapter import upsert_cancion_json

# Después de descargar de Spotify
metadata = {
    'titulo': track_info['name'],
    'artista': track_info['artists'][0]['name'],
    'album': track_info['album']['name'],
    'duracion_seg': track_info['duration_ms'] // 1000,
    'plataforma_origen': 'Spotify',
    'url_origen': track_info['external_urls']['spotify'],
    'ruta_local': downloaded_mp3_path,
    'caratula_url': track_info['album']['images'][0]['url']
}

cancion_json = upsert_cancion_json(metadata)
print(f"✅ Guardada: {cancion_json['titulo']} (ID: {cancion_json['id_cancion']})")
```

### Mostrar playlist en UI
```python
from model.db_adapter import get_playlist_json

playlist = get_playlist_json(id_playlist=playlist_id)

# Mostrar en la interfaz
ui.mostrar_titulo(playlist['nombre'])
ui.mostrar_descripcion(playlist['descripcion'])

for cancion in playlist['canciones']:
    ui.agregar_cancion_a_lista(
        titulo=cancion['titulo'],
        artista=cancion['artista'],
        duracion=cancion['duracion_seg'],
        caratula=cancion['caratula_url']
    )
```

### Sincronizar con archivo JSON
```python
import json
from model.db_adapter import get_todas_canciones_json

# Exportar toda la biblioteca a un archivo JSON
canciones = get_todas_canciones_json()

with open('biblioteca_backup.json', 'w', encoding='utf-8') as f:
    json.dump(canciones, f, indent=2, ensure_ascii=False)

print(f"✅ {len(canciones)} canciones exportadas")
```

## ⚠️ Notas importantes

- La función `upsert_cancion()` **aún existe** y sigue funcionando (devuelve solo ID)
- Usa `upsert_cancion_json()` cuando necesites el JSON completo
- Todas las funciones JSON manejan automáticamente la conexión a la BD
- Los valores `None` en el JSON indican campos vacíos en la BD
- Las funciones son **seguras**: validan los datos antes de guardar
