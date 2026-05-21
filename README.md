# 🎵 Ekho - Plataforma Musical Integral

## 📝 Descripción
Ekho es una aplicación avanzada que centraliza toda tu música en una sola plataforma. Permite reproducir archivos locales, convertir contenido desde múltiples plataformas (YouTube, Spotify, SoundCloud) y gestionar tu biblioteca musical con inteligencia artificial que analiza tus hábitos de escucha para recomendaciones personalizadas.

## ✨ Características Principales

### 🎵 **Reproductor Musical**
- ✅ Reproducción de archivos locales (MP3, FLAC, WAV, etc.)
- ✅ Gestión intuitiva de playlists
- ✅ Integración con cuentas de Spotify
- ✅ Interfaz moderna y personalizable

### 🔄 **Conversor Universal (ARQUITECTURA SIMPLIFICADA)** 
- ✅ **Descarga de audio desde YouTube**
- ✅ **Conversión desde Spotify a MP3**
- ✅ **Sistema optimizado**: Solo bibliotecas esenciales
  - 🎯 `spotdl` - Metadatos de Spotify y descarga
  - 🎯 `yt-dlp` - Búsqueda y descarga desde YouTube
  - 🎯 `moviepy` - Conversión de audio (única)
  - 🎯 `mutagen` - Metadatos MP3 (única)
- ✅ Conversión real a formato MP3 de alta calidad
- ✅ Extracción e incrustación automática de portadas
- ✅ Metadatos automáticos con identificación de origen
- ✅ **Guardado automático**: Archivo fijo para integración con BD
- 🚧 Próximamente: SoundCloud

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

### Conversor Universal (Punto de Entrada Único)
```bash
# Ejecutar aplicación principal con menú interactivo
python src/conversores.py

# La aplicación presenta un menú para seleccionar:
# 1. Spotify a MP3 - Metadatos completos con SpotDL
# 2. YouTube a MP3 - Descarga directa optimizada
```

### Configuración Automática
El sistema está completamente simplificado y no requiere configuración manual:

**✅ SpotDL configuración automática:**
- Usa credenciales por defecto integradas
- No necesita API keys ni configuración
- Funciona inmediatamente tras la instalación

**✅ FFmpeg incluido:**
- Instalación automática con las dependencias
- No requiere configuración adicional

**✅ Arquitectura MVC robusta:**
- Punto de entrada único: `src/conversores.py`
- Separación clara de responsabilidades
- Bibliotecas esenciales sin redundancias

### 🎵 Reproductor Musical
```bash
# Próximamente - Integración con biblioteca de música convertida
python player.py
```

### 🤖 Asistente IA  
```bash
# En desarrollo - Recomendaciones basadas en música convertida
python ai_assistant.py
```

## 📁 Estructura del Proyecto Simplificada
```
Ekho/
├── src/
│   ├── conversores.py                   # 🚀 PUNTO DE ENTRADA ÚNICO
│   ├── controller/                      # 🎛️ Controladores MVC
│   │   ├── base_controller.py           #   Controlador base abstracto
│   │   ├── main_controller.py           #   Controlador principal con menú
│   │   ├── spotify2mp3_controller.py    #   Controlador Spotify
│   │   └── youtube2mp3_controller.py    #   Controlador YouTube
│   ├── model/                           # 📊 Modelos (Lógica de negocio)
│   │   ├── spotify2mp3_model.py         #   Modelo Spotify (SpotDL + yt-dlp)
│   │   ├── youtube2mp3_model.py         #   Modelo YouTube (PyTubefix)
│   │   └── base_converter.py            #   Conversor base
│   ├── view/                            # 👁️ Vistas (Interfaz usuario)
│   │   ├── base_view.py                 #   Vista base abstracta
│   │   ├── spotify2mp3_view.py          #   Vista Spotify
│   │   └── youtube2mp3_view.py          #   Vista YouTube
├── data/
│   ├── music/                           # 🎵 Música convertida (MP3)
│   ├── BDD/                             # 💾 Base de datos SQLite
│   │   └── ekho.db                      #   BD con canciones/playlists en JSON
│   └── temp/                            # 🗂️ Archivos temporales
├── install_dependencies.py              # 📦 Instalador dependencias
├── requirements.txt                     # 📝 Lista dependencias simplificadas
└── README.md                            # 📖 Documentación
```

## 🎯 Arquitectura MVC Robusta

### 🎛️ **Controladores** (Comunicadores Model-View)
- **`MainController`**: Menú principal y gestión de aplicación
- **`Spotify2MP3Controller`**: Coordinador conversión Spotify
- **`YouTube2MP3Controller`**: Coordinador conversión YouTube
- **`BaseController`**: Interfaz común y manejo de errores

### 📊 **Modelos** (Lógica de Negocio)  
- **`Spotify2MP3Converter`**: SpotDL + yt-dlp + moviepy + mutagen
- **`YouTube2MP3Converter`**: PyTubefix + moviepy + mutagen
- **Sin bibliotecas redundantes**: Solo esenciales

### 👁️ **Vistas** (Interfaz de Usuario)
- **`SpotifyView`**: Interfaz conversión Spotify  
- **`YouTubeView`**: Interfaz conversión YouTube
- **`BaseView`**: Interfaz común y mensajes consistentes
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

### Conversor Spotify (SIMPLIFICADO)
```bash
# Sistema simplificado - instalar bibliotecas esenciales
pip install spotdl yt-dlp moviepy mutagen requests

# ⚠️ FFmpeg requerido por spotdl y moviepy
# Windows: Descargar desde https://ffmpeg.org/
# Linux: sudo apt install ffmpeg
# macOS: brew install ffmpeg

# Arquitectura simplificada:
# ✅ spotdl: Metadatos de Spotify + descarga integrada
# ✅ yt-dlp: Búsqueda y descarga desde YouTube  
# ✅ moviepy: Conversión de audio (única biblioteca)
# ✅ mutagen: Metadatos MP3 (única biblioteca)
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
