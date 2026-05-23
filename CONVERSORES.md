# 🔄 Conversores — Documentación de cambios

Este documento describe los cambios aplicados a los tres conversores de audio del proyecto.

---

## Archivos modificados

| Archivo | Clase principal |
|---|---|
| `src/model/soundcloud2mp3.py` | `SoundCloudConverter` |
| `src/model/spotify2mp3_model.py` | `Spotify2MP3Converter` |
| `src/model/youtube2mp3_model.py` | `YouTube2MP3Converter` |
| `src/model/conversor_model.py` | `BaseModel`, `ConverterFactory` |

---

## 1. SoundCloud adaptado al mismo patrón que Spotify y YouTube

`SoundCloudConverter` ahora hereda de `BaseModel` (igual que `Spotify2MP3Converter`) y su método `convert()` sigue exactamente el mismo flujo que los otros dos conversores.

### Formato de metadatos unificado

Los tres conversores retornan y guardan los metadatos con las mismas claves:

```python
{
    'titulo':            str,   # nombre de la canción
    'artista':           str,   # artista o uploader
    'album':             str,   # álbum o nombre de canal/plataforma
    'duracion_seg':      int,   # duración en segundos
    'genero':            str,   # género(s) separados por coma
    'plataforma_origen': str,   # 'Spotify' | 'YouTube' | 'SoundCloud'
    'url_origen':        str,   # URL original proporcionada
    'ruta_local':        str,   # ruta absoluta del MP3 descargado
    'caratula_url':      str,   # URL de la imagen de portada
    'letra':             str,   # letra de la canción (si está disponible)
}
```

### Guardado automático en base de datos

Los tres conversores guardan en BD al finalizar cada conversión usando `upsert_cancion` y `registrar_descarga` del adaptador de BD:

```
convert(url)
    ├── descarga el audio
    ├── convierte a MP3
    ├── incrusta metadatos y portada en el archivo
    └── upsert_cancion(metadata_bd)   ← guarda/actualiza en BD
        registrar_descarga(id, 'mp3') ← registra el evento
```

Si la BD no está disponible, la descarga continúa igual y se muestra una advertencia.

---

## 2. Funciones de conveniencia (una línea por conversor)

Cada módulo expone ahora una función a nivel de módulo que acepta directamente una URL y devuelve la ruta del MP3. No hace falta instanciar la clase manualmente.

```python
from model.spotify2mp3_model  import convert_spotify
from model.youtube2mp3_model  import convert_youtube
from model.soundcloud2mp3     import convert_soundcloud

mp3 = convert_spotify("https://open.spotify.com/track/...")
mp3 = convert_youtube("https://www.youtube.com/watch?v=...")
mp3 = convert_soundcloud("https://soundcloud.com/artist/track")
```

Estas funciones **sí guardan en BD** porque internamente llaman a `ConverterClass().convert(url)`.

`convert_soundcloud` también acepta una carpeta personalizada:

```python
mp3 = convert_soundcloud(url, download_folder="D:/Mi Musica")
```

---

## 3. Carpeta de descarga configurable

Cada conversor ahora expone la variable `download_folder` y el método `set_download_folder(path)` para cambiar el destino de las canciones en cualquier momento.

### Variable de instancia

```python
conversor.download_folder  # ruta actual (str o Path según el conversor)
```

### Método para cambiar la ruta

```python
conversor.set_download_folder("D:/Mi Musica")
# → Crea la carpeta si no existe
# → Imprime: 📁 Carpeta de descarga actualizada: D:\Mi Musica
```

### Valores por defecto

| Conversor | Ruta por defecto |
|---|---|
| `SoundCloudConverter` | `<raíz_proyecto>/data/music` |
| `Spotify2MP3Converter` | `<raíz_proyecto>/data/music` |
| `YouTube2MP3Converter` | `<raíz_proyecto>/data/music` |

El valor por defecto se calcula automáticamente a partir de la ubicación del archivo, independientemente del directorio de trabajo actual.

### Ejemplo completo

```python
from model.youtube2mp3_model import YouTube2MP3Converter

conv = YouTube2MP3Converter()
conv.set_download_folder("C:/Usuarios/Niko/Musica")

mp3 = conv.convert("https://www.youtube.com/watch?v=...")
# El MP3 se guarda en C:\Usuarios\Niko\Musica\
# Y queda registrado en la BD con esa ruta
```

---

## 4. ConverterFactory ahora soporta SoundCloud

`ConverterFactory.create_converter(url)` en `conversor_model.py` detecta automáticamente la plataforma y retorna el conversor correcto:

```python
from model.conversor_model import ConverterFactory

conv = ConverterFactory.create_converter("https://soundcloud.com/artist/track")
# → retorna SoundCloudConverter()

conv = ConverterFactory.create_converter("https://open.spotify.com/track/...")
# → retorna Spotify2MP3Converter()

conv = ConverterFactory.create_converter("https://www.youtube.com/watch?v=...")
# → retorna YouTube2MP3Converter()

mp3 = conv.convert(url)
```

`get_supported_platforms()` ya incluye `'SoundCloud'`.

---

## 5. Resumen de métodos por conversor

| Método / Función | SoundCloud | Spotify | YouTube |
|---|:---:|:---:|:---:|
| `convert(url)` | ✅ | ✅ | ✅ |
| `set_download_folder(path)` | ✅ | ✅ | ✅ |
| `get_track_info(url)` → formato canónico | ✅ | ✅ | — |
| Guarda en BD automáticamente | ✅ | ✅ | ✅ |
| `convert_XXX(url)` función global | ✅ | ✅ | ✅ |
