# EKHO - Desktop App

Aplicacion de escritorio EKHO (Plataforma Musical) que combina:
- **Backend Python**: Conversores Spotify/YouTube a MP3, reproductor local, gestion de BD
- **Frontend React**: UI con TanStack Start + Tailwind v4 + shadcn/ui
- **Puente**: PyWebView para ventana nativa + API bridge via `window.pywebview.api`

## Requisitos

- **Python 3.10+**
- **Node.js 18+** (para el frontend)
- **FFmpeg** en PATH
  - Windows: `winget install Gyan.FFmpeg`

## Instalacion

```bash
pip install -r requirements.txt
cd lovable-code
npm install
cd ..
```

## Desarrollo

Ejecuta con un solo comando:

```bash
python app.py
```

O:

```bash
run.bat
```

`app.py` arranca automaticamente el servidor Vite (frontend) y la ventana
PyWebView, y lo cierra todo al salir.

## Como se conecta el Frontend con Python

La UI React llama a Python a traves de `window.pywebview.api`:

```js
// Obtener playlists
const playlists = await window.pywebview.api.get_playlists();

// Obtener canciones
const songs = await window.pywebview.api.get_playlist_songs("all");

// Convertir YouTube
const result = await window.pywebview.api.convert_youtube(url);

// Convertir Spotify
const result = await window.pywebview.api.convert_spotify(url);

// Reproducir
await window.pywebview.api.play_song(songId);
await window.pywebview.api.pause_song();
await window.pywebview.api.next_song();

// Estado del sistema
const status = await window.pywebview.api.get_system_status();

// Configuracion
const settings = await window.pywebview.api.get_settings();
await window.pywebview.api.update_settings({ volume: 50 });
```

### Metodos disponibles

| Metodo | Retorno |
|--------|---------|
| `convert_youtube(url)` | `{ok, data: {path, filename, log}}` |
| `convert_spotify(url)` | `{ok, data: {path, filename, log}}` |
| `get_playlists()` | `[{id, name, description, is_public}]` |
| `get_playlist_songs(id)` | `[{id, title, artist, album, duration, genre, source, path, cover_url}]` |
| `get_songs()` | igual que `get_playlist_songs("all")` |
| `add_song_to_playlist(pid, sid)` | `{ok, data}` |
| `remove_song_from_playlist(pid, sid)` | `{ok, data}` |
| `play_song(id)` | `{ok, data: {message}}` |
| `pause_song()` | `{ok, data}` |
| `resume_song()` | `{ok, data}` |
| `stop_song()` | `{ok, data}` |
| `next_song()` | `{ok, data}` |
| `prev_song()` | `{ok, data}` |
| `get_settings()` | `{volume, theme, download_quality}` |
| `update_settings({...})` | `{ok, data: settings}` |
| `get_system_status()` | `{dependencies, ffmpeg, music_count}` |

## Empaquetar (Windows)

Proximamente: empaquetado con PyInstaller incluyendo Node.js + el frontend.

## Estructura del proyecto

```
├── app.py                  # PyWebView launcher
├── api.py                  # API bridge (clase Api)
├── run.bat                 # Lanzador dev server + app
├── requirements.txt        # Dependencias Python
├── README.md               # Esta documentacion
├── lovable-code/           # Codigo fuente React (TanStack Start)
│   ├── src/
│   │   ├── lib/bridge.ts   # Bridge window.pywebview.api
│   │   ├── routes/         # Paginas de la app
│   │   └── ...
│   └── package.json
├── web/                    # Build de produccion (generado)
├── src/                    # Modulos Python existentes
│   ├── model/
│   ├── controller/
│   └── databaseManager/
└── data/
    ├── music/              # MP3 descargados
    ├── metadata/
    └── BDD/ekho.db         # Base de datos SQLite
```
