# EKHO 
Ekho es una plataforma de reproducción musical avanzada diseñada para 
centralizar y optimizar la experiencia de escucha del usuario. La aplicación permite 
reproducir música de forma local, importar contenidos desde diversas plataformas 
de streaming —incluyendo YouTube, Spotify y SoundCloud—, y ofrecer 
recomendaciones personalizadas mediante un asistente con inteligencia artificial.
 
Este asistente analiza las canciones descargadas, hábitos de escucha, géneros 
favoritos y artistas más reproducidos, generando sugerencias adaptadas al perfil 
musical de cada usuario. Además, Ekho proporciona información detallada sobre 
cada canción, su autor, origen y letra, junto con otros datos relevantes. 

## Funcionalidades principales 
- Reproducción de música local: Compatibilidad con formatos de audio 
comunes (mp3, wav, etc.). Permite organizar la biblioteca, crear listas de 
reproducción y explorar colecciones musicales de forma intuitiva. 
- Conversor de enlaces: Herramienta para convertir contenidos de YouTube, 
SoundCloud y Spotify en archivos mp3 con gestión automática de metadatos, 
como título, artista y carátula. 
- Recomendador inteligente: Algoritmo basado en aprendizaje automático que 
ofrece sugerencias musicales acordes a gustos y tendencias de escucha. 
- Sistema de playlists: Creación, edición y gestión avanzada de listas 
personalizadas. 
- Sincronización con Spotify: Integración directa para mostrar y descargar 
canciones y playlists del usuario, incorporándose a la biblioteca local. 
En definitiva, Ekho proporciona una solución completa y flexible para amantes de 
la música que buscan personalización, accesibilidad y versatilidad, reuniendo en una 
sola plataforma todos los recursos necesarios para disfrutar, descubrir y gestionar 
su colección musical de manera inteligente y eficiente.

## Ventajas ante la competencia
Te preguntarás: ¿Por qué elegir EKHO y no cualquier otra aplicacion main stream? Muy sencillo:

| Ventaja | EKHO | Spotify | SoundCloud | Youtube |
|---------|------|---------|------------|---------|
| Descarga directa de audio	| ✓ Permite descargar audio desde múltiples orígenes | ✕ Solo offline con Premium | ✕ No descarga nativa | ✕ No descarga nativa|
| Reproducción sin conexión sin suscripción| ✓ Offline gratuito | ✕ Offline solo con Premium| ✕ No disponible | ✕ No disponible |
| Eliminación total de publicidad |✓ Libre de anuncios| ✕ Gratis con anuncios; Premium sin anuncios| ✕ Gratis con anuncios; Pro sin anuncios| ✕ Gratis con anuncios; Premium sin anuncios |
| Integración multi-fuente | ✓ Soporta YouTube, Spotify, SoundCloud y más | ✕ Solo catálogo Spotify | ✕ Solo catálogo SoundCloud | ✕ Solo videos YouTube |
|Gestión completa de la biblioteca | ✓ Crear, editar y organizar carpetas locales sin restricciones | ✕ Listas y favoritos limitados | ✕ Favoritos y sets, menos control | ✕ Listas de reproducción básicas|

## Breakdown 
| Semana | Fase principal | Subtareas detalladas |
|--------|----------------|----------------------|
| 1      | Análisis y diseño | - Definir funcionalidades (reproduce local, conversor, recomendaciones, playlists, sincronización) <br> - Estudio de requisitos técnicos  y dependencias (APIs externas, ML, bases de datos)  Investigación de APIs de streaming (endpoints, limitaciones) <br> - Diseño inicial UI/UX (bocetos, wireframes principales) <br> - Planificación y asignación de tareas |
| 2      | Desarrollo base app | - Configuración inicial del proyecto (repositorio, estructura directorios, frameworks) <br> - Implementar reproductor local básico (carga y reproducción de archivos mp3, wav) <br> - Añadir gestión de biblioteca (importar/eliminar canciones, carpetas) <br> - Crear interfaz principal y navegación (pantalla home, menús) <br>| - Pruebas de funcionamiento básico (reproduce, añade, elimina) |
| 3      | Integraciones externas y conversor  | - Integrar autenticación y acceso a Spotify <br> - Conectar y consultar APIs de YouTube y SoundCloud <br> - Crear el conversor de enlaces (descargar audio de YouTube/SoundCloud/Spotify en mp3) <br> - Procesar y añadir metadatos automáticos (título, artista, carátula) <br> - Sincronizar y descargar playlists desde Spotify <br> - Pruebas de conversión y sincronización |
| 4      | Motor recomendador y asistente IA   | - Recopilar historial y hábitos de escucha (guardar historial en base de datos) <br> - Analizar géneros y artistas favoritos (estadísticas básicas) <br> - Diseñar y probar el algoritmo ML (sugerencias de canciones) <br> - Integrar el asistente IA para recomendaciones personalizadas <br> - Pruebas de uso del recomendador |
| 5      | Gestión avanzada e información      | - Implementar visualización de metadatos (autor, álbum, letra) <br> - Mejorar interfaz para playlists (crear, editar, ordenar, borrar) <br> - Añadir buscador y filtros avanzados en la biblioteca <br> - Integrar vistas de información de canción (popup, detalles) <br> - Validar y corregir UI/UX según feedback de usuarios |
| 6      | QA, testing y despliegue            | - Testear todas las funcionalidades (unitarias y de integración) <br> - Corregir bugs y refinar detalles <br> - Crear documentación para usuario y técnica <br> - Preparar despliegue en entorno final <br> - Presentación y entrega del proyecto |


