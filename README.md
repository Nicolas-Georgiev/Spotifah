# EKHO

EKHO es una aplicacion de escritorio para gestionar, importar, reproducir y descubrir musica. Combina una interfaz React con un backend Python y se ejecuta como ventana nativa usando PyWebView.

## Que Incluye

- Biblioteca musical local con canciones, caratulas, metadatos y playlists.
- Importacion desde YouTube, Spotify, SoundCloud, albums, playlists y archivos locales.
- Reproductor integrado con cola, volumen, siguiente/anterior, pausa, shuffle y repeat.
- Recomendaciones externas basadas en canciones de la biblioteca usando Spotify.
- Configuracion persistente de tema, calidad, rutas y credenciales.
- Build de produccion con Vite + PyInstaller.

## Requisitos

- Python 3.12.1.
- Node.js 18 o superior.
- FFmpeg instalado o disponible para la app.
- Windows para el flujo principal de build actual.

Instalacion recomendada:

```bat
pip install -r requirements.txt
cd lovable-code
npm install
cd ..
```

Para FFmpeg en Windows:

```bat
winget install Gyan.FFmpeg
```

## Ejecutar La App

Primero genera el frontend:

```bat
cd lovable-code
npm run build
cd ..
```

Despues arranca la aplicacion:

```bat
python app.py
```

Tambien puedes usar:

```bat
run.bat
```

`app.py` comprueba que existe `web/index.html`, configura FFmpeg, levanta el servidor local en `http://127.0.0.1:57291`, crea la API Python y abre la ventana de EKHO.

## Arquitectura

EKHO tiene cuatro piezas principales:

- `app.py`: punto de entrada de escritorio. Inicializa entorno, servidor, API y ventana PyWebView.
- `server.py`: servidor HTTP local para servir el frontend, caratulas, assets y rutas de OAuth de Spotify.
- `api/`: API expuesta al frontend mediante `window.pywebview.api`.
- `lovable-code/`: frontend React/Vite con rutas, componentes y bridge TypeScript.

El flujo general es:

```text
React UI -> bridge.ts -> window.pywebview.api -> api/*.py -> src/* + SQLite + archivos
```

## Estructura Del Proyecto

```text
.
|-- app.py                         # Lanzador PyWebView
|-- server.py                      # Servidor local SPA, assets, caratulas y Spotify OAuth
|-- build.bat                      # Build frontend + PyInstaller
|-- run.bat                        # Ejecucion simple de app.py
|-- requirements.txt               # Dependencias Python
|-- EKHO.spec                      # Spec generado/usado por PyInstaller
|-- installer.iss                  # Instalador Inno Setup
|-- api/                           # API bridge para la UI
|   |-- __init__.py                # Clase Api y preparacion de datos
|   |-- converters.py              # Conversion e importacion online
|   |-- playlists.py               # Biblioteca, playlists, favoritos y busqueda
|   |-- player.py                  # Reproductor
|   |-- recommendations.py         # Recomendaciones y Spotify
|   |-- settings.py                # Configuracion
|   |-- system.py                  # Estado del sistema y borrado de datos
|   |-- covers.py                  # Caratulas
|   `-- local_import.py            # Importacion de archivos locales
|-- src/                           # Logica Python de dominio
|   |-- controller/                # Controladores de conversion, musica y recomendaciones
|   |-- model/                     # Modelos, conversores, biblioteca y embeddings
|   |-- databaseManager/           # SQLite y esquema de datos
|   |-- frozen_utils.py            # Utilidades para ejecutable congelado
|   `-- no_console_subprocess.py   # Oculta ventanas de subprocess en Windows
|-- lovable-code/                  # Frontend React
|   |-- src/routes/                # Paginas de la app
|   |-- src/components/            # Componentes visuales
|   |-- src/lib/bridge.ts          # Cliente TypeScript hacia Python
|   |-- src/lib/app-data.tsx       # Estado compartido de biblioteca/player
|   `-- package.json
|-- web/                           # Build generado por Vite, usado por app.py/PyInstaller
|-- assets/                        # Iconos y portadas base
|-- data/                          # Datos en desarrollo
|   |-- BDD/ekho.db                # Base de datos SQLite
|   |-- music/                     # Canciones descargadas/importadas
|   |-- covers/                    # Caratulas temporales o localizadas
|   `-- settings.json              # Configuracion local
|-- scripts/                       # Utilidades de pruebas, migracion y diagnostico
`-- documentation/                 # Documentacion adicional
```

## Frontend

El frontend vive en `lovable-code/` y usa:

- React.
- Vite.
- TanStack Router.
- Tailwind CSS.
- Componentes Radix/shadcn.
- Lucide React para iconos.

Rutas principales:

- `src/routes/index.tsx`: inicio.
- `src/routes/library*.tsx`: biblioteca y playlists.
- `src/routes/convert.tsx`: importacion/conversion.
- `src/routes/recommendations.tsx`: recomendaciones.
- `src/routes/settings.tsx`: configuracion.
- `src/routes/status.tsx`: estado del sistema.

Componentes importantes:

- `components/player/PlayerBar.tsx`: barra de reproduccion.
- `components/library/*`: tabla, filas, playlists, edicion de canciones.
- `components/convert/*`: importacion de canciones, albums, playlists y archivos locales.
- `components/recommendations/RecommendationsPage.tsx`: pantalla de recomendaciones.
- `components/settings/*`: controles de configuracion.
- `components/shared/*`: caratulas, logo, tarjetas y estados comunes.

## Backend Y API Bridge

La clase `Api` se crea en `api/__init__.py` y mezcla varios mixins. PyWebView expone sus metodos al frontend como:

```ts
window.pywebview.api.nombre_del_metodo(...)
```

El frontend no llama directamente a esa API en todas partes: normalmente pasa por `lovable-code/src/lib/bridge.ts`, que normaliza respuestas y tipos.

### Metodos Principales

Conversion e importacion:

- `convert_youtube(url)`
- `convert_spotify(url)`
- `convert_soundcloud(url)`
- `detect_url_type(url)`
- `get_album_preview(url)`
- `import_album(url)`
- `import_playlist(url)`
- `get_import_progress(task_id)`
- `select_files_dialog()`
- `import_local_files(file_paths)`

Biblioteca y playlists:

- `get_playlists()`
- `get_playlist_songs(playlist_id)`
- `get_songs()`
- `search_songs(query)`
- `create_playlist(name, description)`
- `rename_playlist(playlist_id, name, description, cover_base64)`
- `delete_playlist(playlist_id)`
- `add_song_to_playlist(playlist_id, song_id)`
- `remove_song_from_playlist(playlist_id, song_id)`
- `delete_song(song_id)`
- `update_song(song_id, data)`
- `toggle_favorite(song_id)`
- `is_favorite(song_id)`

Reproductor:

- `play_song(song_id, song_ids)`
- `pause_song()`
- `resume_song()`
- `stop_song()`
- `seek_song(position)`
- `next_song()`
- `prev_song()`
- `toggle_shuffle()`
- `cycle_repeat()`
- `get_now_playing()`
- `get_playback_position()`
- `set_volume(volume)`
- `get_volume()`
- `get_recently_played(limit)`

Recomendaciones:

- `get_recommendations(playlist_id, limit, refresh_key)`
- `recompute_all_embeddings(force)`

Configuracion y sistema:

- `get_settings()`
- `update_settings(data)`
- `select_folder_dialog()`
- `get_system_status()`
- `open_spotify_login()`
- `delete_all_data()`

## Datos Y Persistencia

En desarrollo, los datos se guardan en `data/`.

En el ejecutable congelado, `Api._resolve_data_dir()` mueve los datos de usuario a una carpeta persistente del sistema. En Windows usa:

```text
%APPDATA%\EKHO\data
```

Partes importantes:

- `data/BDD/ekho.db`: SQLite con canciones, playlists, historial, favoritos, caratulas y embeddings.
- `data/music/`: MP3 importados o descargados.
- `data/covers/`: caratulas descargadas o previews.
- `data/settings.json`: tema, volumen, calidad, rutas y tokens de Spotify.

Al arrancar, `Api` crea carpetas necesarias, siembra `ekho.db` si falta, sincroniza MP3 locales y asegura playlists de sistema como Favoritos.

## Conversion E Importacion

La conversion se coordina desde `api/converters.py` y usa modelos/controladores en `src/`.

Soportes principales:

- YouTube: `src/model/youtube2mp3_model.py`.
- Spotify: `src/model/spotify2mp3_model.py`.
- SoundCloud: `src/model/soundcloud2mp3.py`.
- Albums y playlists: importacion asyncrona con progreso consultable por `get_import_progress`.
- Archivos locales: `api/local_import.py`, con lectura de metadatos mediante `mutagen`.

Las canciones importadas se copian o descargan a la carpeta de musica y se registran en SQLite.

## Reproductor

El reproductor esta en:

- `api/player.py`: API de reproduccion para la UI.
- `src/controller/music_controller.py`: control de cola y estado.
- `src/model/music_library.py`: acceso a archivos de musica.

El frontend consulta y actualiza el estado desde `PlayerBar.tsx` y `app-data.tsx`.

## Recomendaciones

La pantalla de recomendaciones usa `api/recommendations.py`.

Comportamiento actual:

- Usa la biblioteca local como semilla para buscar similitudes.
- Busca canciones externas en Spotify.
- Filtra canciones que ya existen en tu biblioteca.
- Devuelve sugerencias no importables directamente, con titulo, artista, album y caratula.
- No rellena huecos con canciones locales.
- Si no hay canciones en la biblioteca, la UI indica que hacen falta canciones para buscar similitudes.
- Si hay biblioteca pero no aparecen recomendaciones, la UI indica que hacen falta tokens de Spotify.

Variables/configuracion relacionadas:

- `RECS_SPOTIFY=0` desactiva recomendaciones por Spotify.
- `RECS_DEBUG=1` muestra logs de diagnostico.
- `SPOTIFY_CLIENT_ID` / `SPOTIFY_CLIENT_SECRET` o `SPOTDL_CLIENT_ID` / `SPOTDL_CLIENT_SECRET` configuran OAuth/API.

Tambien pueden guardarse credenciales y tokens en `settings.json` desde la app.

## Spotify OAuth

`server.py` expone rutas locales para login:

- `/spotify/login`
- `/spotify/callback`
- `/spotify/logout`

El login guarda:

- `spotify_access_token`
- `spotify_refresh_token`
- `spotify_token_expires_at`

en `settings.json`.

Para que OAuth funcione, la app de Spotify debe aceptar como redirect URI el puerto local usado por EKHO:

```text
http://127.0.0.1:57291/spotify/callback
```

## Servidor Local

`server.py` sirve:

- `web/index.html` y assets del frontend.
- Rutas SPA, devolviendo `index.html` cuando no hay archivo fisico.
- Caratulas desde SQLite: `/api/covers/...` y `/api/playlist-covers/...`.
- Portadas base desde `assets/portadas`.
- Tema inicial sustituyendo `__INITIAL_THEME__` en el HTML.
- OAuth de Spotify.

## Configuracion

La configuracion se gestiona en `api/settings.py` y se guarda como JSON.

Campos habituales:

- `theme`
- `volume`
- `download_quality`
- `download_path`
- `spotify_client_id`
- `spotify_client_secret`
- `spotify_access_token`
- `spotify_refresh_token`
- `spotify_token_expires_at`

## Build De Produccion

Build normal:

```bat
build.bat
```

Build con instalador:

```bat
build.bat --installer
```

El proceso hace:

1. Compila el frontend con Vite hacia `web/`.
2. Localiza `site-packages` y dependencias especiales como `tls-client-64.dll`.
3. Ejecuta PyInstaller en modo `onedir`.
4. Genera `dist/EKHO/EKHO.exe`.
5. Opcionalmente genera instalador con Inno Setup.

`build.bat` incluye assets, frontend compilado, base de datos inicial, hooks de PyWebView, dependencias de conversores y DLLs necesarias para `tls_client`.

## Scripts Utiles

- `scripts/check_recs.py`: diagnostico de recomendaciones.
- `scripts/ver_bd.py`: inspeccion de base de datos.
- `scripts/migrar_base_datos.py`: migraciones de SQLite.
- `scripts/install_dependencies.py`: instalacion auxiliar.
- `scripts/test_*.py`: pruebas/manual checks de datos y playlists.

## Problemas Comunes

### Falta `web/index.html`

Ejecuta:

```bat
cd lovable-code
npm run build
cd ..
```

### FFmpeg No Disponible

Instala FFmpeg y comprueba que esta en PATH, o revisa la configuracion que usa `src/frozen_utils.py`.

### Recomendaciones Vacias

- Si la biblioteca esta vacia, importa canciones primero.
- Si ya hay canciones, revisa credenciales y tokens de Spotify.
- Activa `RECS_DEBUG=1` para ver logs.

### Error Con `tls-client-64.dll` En El EXE

Reinstala `tls-client` en el entorno usado para compilar:

```bat
pip install --force-reinstall tls-client
```

Despues vuelve a ejecutar `build.bat`.

### Ventanas Fugaces Durante Conversion

`src/no_console_subprocess.py` parchea `subprocess.Popen` en Windows para ocultar ventanas de procesos auxiliares como FFmpeg o descargadores.

## Notas De Desarrollo

- Edita el frontend en `lovable-code/src/`.
- Ejecuta `npm run build` para actualizar `web/`, que es lo que carga la app.
- Edita la API Python en `api/`.
- Edita logica de dominio en `src/`.
- No edites manualmente assets generados en `web/assets` salvo que sepas que no vas a regenerar el frontend.
