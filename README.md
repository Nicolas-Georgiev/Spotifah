# 🎵 Ekho - Plataforma Musical Integral

## 📝 Descripción
Ekho es una aplicación avanzada que centraliza toda tu música en una sola plataforma. Permite reproducir archivos locales, convertir contenido desde múltiples plataformas (YouTube, Spotify, SoundCloud) y gestionar tu biblioteca musical con inteligencia artificial que analiza tus hábitos de escucha para recomendaciones personalizadas.

## ✨ Características Principales

### 🎵 **Reproductor Musical**
- ✅ Reproducción de archivos locales (MP3, FLAC, WAV, etc.)
- ✅ Gestión intuitiva de playlists
- ✅ Integración con cuentas de Spotify
- ✅ Interfaz moderna y personalizable

### 🔄 **Conversor Universal** 
- ✅ **Descarga de audio desde YouTube** (Disponible)
- ✅ **Conversión desde Spotify a MP3** (Nuevo!)
- ✅ Conversión real a formato MP3 de alta calidad
- ✅ Extracción e incrustación automática de portadas
- ✅ Metadatos automáticos con identificación de origen
- 🚧 Próximamente: SoundCloud, Bandcamp

### 🤖 **Asistente IA**
- 🚧 Análisis de hábitos de escucha
- 🚧 Recomendaciones personalizadas
- 🚧 Descubrimiento automático de nueva música

### 📚 **Gestión de Biblioteca**
- 🚧 Organización automática por metadatos
- 🚧 Búsqueda avanzada y filtros
- 🚧 Sincronización multiplataforma

## 🛠️ Instalación

```bash
# Instalación automática de dependencias
python install_dependencies.py

# O instalación manual
pip install -r requierments.txt
```

## 🚀 Uso

### Conversor de YouTube a MP3
```bash
# Ejecutar conversor de YouTube
python run_converter.py

# Ejecutar conversor de Spotify
python run_spotify_converter.py

# Conversor universal (detecta automáticamente la plataforma)
python main_converter.py
```

### Configuración para Spotify
Para usar el conversor de Spotify, necesitas configurar credenciales de la API:

**🚀 Configuración rápida:**
```bash
python setup_spotify.py
```

**🔧 Configuración manual:**

1. **Obtén credenciales de Spotify:**
   - Ve a [Spotify for Developers](https://developer.spotify.com/dashboard)
   - Crea una nueva aplicación
   - Obtén tu Client ID y Client Secret

2. **Configura variables de entorno:**
   ```powershell
   # Windows (PowerShell)
   $env:SPOTIFY_CLIENT_ID="tu_client_id"
   $env:SPOTIFY_CLIENT_SECRET="tu_client_secret"
   
   # Windows (CMD)
   set SPOTIFY_CLIENT_ID=tu_client_id
   set SPOTIFY_CLIENT_SECRET=tu_client_secret
   
   # Linux/macOS
   export SPOTIFY_CLIENT_ID="tu_client_id"
   export SPOTIFY_CLIENT_SECRET="tu_client_secret"
   ```

3. **URLs soportadas:**
   - `https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh`
   - `spotify:track:4iV5W9uYEdYUVa79Axb7Rh`
   - ✅ URLs con parámetros (`?si=...`) se limpian automáticamente

**Proceso:** URL de YouTube → Descarga audio + portada → Conversión a MP3 → Metadatos + portada incrustada

### 🎵 Reproductor Musical
```bash
# Próximamente
python player.py
```

### 🤖 Asistente IA
```bash
# En desarrollo
python ai_assistant.py
```

## 📁 Estructura del Proyecto
```
Ekho/
├── src/
│   ├── controller/
│   │   ├── youtube2mp3_controller.py    # Conversor YouTube
│   │   ├── metadata_controller.py       # Control de metadatos
│   │   └── music_controller.py          # Reproductor
│   ├── model/
│   │   ├── youtube2mp3_model.py         # Conversión YouTube con portadas
│   │   ├── metadata_reader.py           # Lectura de metadatos de audio
│   │   ├── music_library.py             # Biblioteca musical
│   │   └── base_converter.py            # Base para convertidores futuros
│   ├── view/
│   │   ├── youtube2mp3_view.py          # UI Conversor
│   │   ├── metadata_view.py             # UI Metadatos
│   │   ├── player_ui.py                 # UI Reproductor
│   │   └── main_ui.py                   # UI Principal (futuro)
│   ├── run_converter.py                 # Script principal del conversor
│   ├── run_metadata.py                  # Script principal de metadatos
│   └── main.py                          # Aplicación principal (futuro)
├── data/
│   └── music/                           # Biblioteca musical (MP3 con metadatos)
├── assets/
│   └── icons/                           # Recursos gráficos
├── converter.py                         # Acceso directo al conversor
├── metadata.py                          # Analizador de metadatos
├── install_dependencies.py              # Instalador automático de dependencias
├── requierments.txt                     # Lista de dependencias
└── README.md                            # Documentación del proyecto
```

## 🎯 Funcionalidades por Módulo

### 🔄 Conversor (Disponible)
| Característica | Estado | Descripción |
|----------------|--------|-------------|
| YouTube → MP3 | ✅ Activo | Descarga y conversión con portadas |
| Spotify → MP3 | ✅ Activo | Busca en YouTube usando metadatos de Spotify |
| SoundCloud → MP3 | 🚧 Planificado | En roadmap |

### 🎵 Reproductor (En desarrollo)
| Característica | Estado | Descripción |
|----------------|--------|-------------|
| Reproducción local | 🚧 Desarrollo | Archivos MP3, FLAC, WAV |
| Control de playlists | 🚧 Desarrollo | Crear, editar, gestionar |
| Integración Spotify | 🚧 Planificado | Sincronización de cuentas |

### 🤖 IA & Recomendaciones
| Característica | Estado | Descripción |
|----------------|--------|-------------|
| Análisis de hábitos | 🚧 Investigación | Machine Learning |
| Recomendaciones | 🚧 Planificado | Algoritmos personalizados |
| Auto-discovery | 🚧 Concepto | Descubrimiento automático |

## 🔧 Detalles Técnicos del Conversor

### Metadatos incluidos:
- 📝 **Título:** Nombre de la pista (YouTube) o información de Spotify
- 👤 **Artista:** Canal/creador (YouTube) o artista real (Spotify)
- 🖼️ **Portada:** Thumbnail (YouTube) o artwork oficial (Spotify)
- 💬 **Origen:** Identificación de plataforma fuente
- 🎵 **Album:** Información del álbum (Spotify)

### Calidad y formato:
- **Audio:** 192kbps MP3 estándar
- **Portadas:** Máxima resolución disponible
- **Compatibilidad:** Universal con reproductores

## 📈 Roadmap de Desarrollo

### 🚧 v2.0 - Reproductor Completo
- [ ] Interfaz gráfica principal
- [ ] Reproductor de archivos locales
- [ ] Gestión de playlists
- [ ] Controles multimedia

### 🚧 v3.0 - Múltiples Convertidores
- [x] Conversor de Spotify (✅ Completado)
- [ ] Conversor de SoundCloud
- [ ] Conversor de Bandcamp
- [ ] Descarga de playlists

### 🚧 v4.0 - Inteligencia Artificial
- [ ] Motor de recomendaciones
- [ ] Análisis de preferencias musicales
- [ ] Auto-generación de playlists
- [ ] Descubrimiento musical inteligente

## 🐛 Solución de Problemas

### Conversor YouTube
```bash
# Verificar dependencias
python install_dependencies.py

# Problemas de conversión
pip install moviepy mutagen
```

### Conversor Spotify
```bash
# Instalar dependencias específicas
pip install spotipy yt-dlp

# Configurar credenciales (ver sección de configuración arriba)
# Problemas de búsqueda: verificar conexión a YouTube
```

### Reproductor (Próximamente)
```bash
# Verificar dependencias de audio
pip install pygame
```

## 📄 Licencia
Proyecto educativo. 

---
*Ekho v1.0 - Una nueva forma de gestionar tu música* 🎵
