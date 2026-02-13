# soundcloud2mp3.py
"""
Conversor completo de links de SoundCloud a MP3
Utiliza múltiples métodos de descarga y manejo de metadatos
"""

import subprocess
import os
import re
import json
import requests
import sys
import platform
import zipfile
import shutil
import urllib.request
import datetime
from pathlib import Path

# Intentar importar bibliotecas opcionales para metadatos
HAS_METADATA = False
METADATA_TYPE = None

try:
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, COMM, TRCK, TPE2, TDRC
    HAS_METADATA = True
    METADATA_TYPE = "mutagen"
    print("✅ Usando mutagen para metadatos de audio")
except ImportError:
    try:
        import eyed3
        HAS_METADATA = True
        METADATA_TYPE = "eyed3"
        print("✅ Usando eyed3 para metadatos de audio")
    except ImportError:
        print("⚠️ Sin bibliotecas de metadatos. Instala: pip install mutagen o pip install eyed3")

class SoundCloudConverter:
    """Conversor robusto de SoundCloud a MP3"""
    
    def __init__(self, download_folder="data/music"):
        self.download_folder = Path(download_folder)
        self.download_folder.mkdir(parents=True, exist_ok=True)
        
    def setup_environment(self, force_install=False):
        """Configura el entorno completo instalando todas las dependencias necesarias"""
        print("🔧 Configurando entorno para SoundCloud converter...")
        print("=" * 60)
        
        # 1. Verificar dependencias actuales
        print("🔍 Verificando dependencias existentes...")
        deps = self.check_dependencies(auto_install_ffmpeg=False)
        
        missing_deps = [name for name, available in deps.items() if not available]
        
        if not missing_deps and not force_install:
            print("✅ Todas las dependencias están instaladas")
            return True
        
        if missing_deps:
            print(f"❌ Dependencias faltantes: {', '.join(missing_deps)}")
        
        # 2. Instalar dependencias de Python
        python_deps = ['scdl', 'yt-dlp', 'mutagen', 'requests']
        missing_python = [dep for dep in python_deps if dep in missing_deps or dep in ['scdl', 'yt-dlp']]
        
        if missing_python or force_install:
            print("\n📦 Instalando dependencias de Python...")
            installed, failed = self.install_python_dependencies()
            
            if failed:
                print(f"⚠️ No se pudieron instalar: {', '.join(failed)}")
            
        # 3. Instalar ffmpeg si es necesario
        if 'ffmpeg' in missing_deps or force_install:
            print("\n🔧 Instalando ffmpeg...")
            if self.install_ffmpeg():
                print("✅ ffmpeg instalado exitosamente")
            else:
                print("❌ Error al instalar ffmpeg")
        
        # 4. Verificación final
        print("\n🔍 Verificación final de dependencias...")
        final_deps = self.check_dependencies(auto_install_ffmpeg=False)
        
        print("\n📋 Estado final de dependencias:")
        all_available = True
        for name, available in final_deps.items():
            status = "✅ Disponible" if available else "❌ No disponible"
            print(f"   {name}: {status}")
            if not available:
                all_available = False
        
        if all_available:
            print("\n🎉 ¡Entorno configurado correctamente!")
            print("💡 Puedes usar el conversor ahora")
        else:
            print("\n⚠️ Algunas dependencias aún faltan")
            print("💡 Puedes intentar instalarlas manualmente:")
            for name, available in final_deps.items():
                if not available:
                    if name == 'ffmpeg':
                        print(f"   ffmpeg: Visita https://ffmpeg.org/download.html")
                    else:
                        print(f"   {name}: pip install {name}")
        
        return all_available

    def validate_soundcloud_url(self, url):
        """Valida si la URL es de SoundCloud"""
        soundcloud_pattern = r'https?://(?:www\.)?soundcloud\.com/.+'
        return bool(re.match(soundcloud_pattern, url))
    
    def install_ffmpeg(self):
        """Instala ffmpeg automáticamente según el sistema operativo"""
        system = platform.system().lower()
        
        print("🔧 Instalando ffmpeg...")
        
        try:
            if system == "windows":
                return self._install_ffmpeg_windows()
            elif system == "darwin":  # macOS
                return self._install_ffmpeg_macos()
            elif system == "linux":
                return self._install_ffmpeg_linux()
            else:
                print(f"❌ Sistema operativo no soportado: {system}")
                return False
        except Exception as e:
            print(f"❌ Error al instalar ffmpeg: {e}")
            return False
    
    def _install_ffmpeg_windows(self):
        """Instala ffmpeg en Windows"""
        try:
            # Verificar si ya está instalado
            try:
                subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
                print("✅ ffmpeg ya está instalado")
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
            
            print("📦 Descargando ffmpeg para Windows...")
            
            # URL de descarga de ffmpeg para Windows (build estático)
            ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
            
            # Crear carpeta temporal
            temp_dir = Path.home() / "temp_ffmpeg"
            temp_dir.mkdir(exist_ok=True)
            
            zip_path = temp_dir / "ffmpeg.zip"
            
            # Descargar ffmpeg
            print("⬇️ Descargando archivo...")
            urllib.request.urlretrieve(ffmpeg_url, zip_path)
            
            # Extraer archivo
            print("📂 Extrayendo archivo...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Encontrar la carpeta extraída
            extracted_folders = [f for f in temp_dir.iterdir() if f.is_dir() and "ffmpeg" in f.name.lower()]
            if not extracted_folders:
                print("❌ No se encontró la carpeta de ffmpeg extraída")
                return False
            
            ffmpeg_folder = extracted_folders[0]
            ffmpeg_exe = ffmpeg_folder / "bin" / "ffmpeg.exe"
            
            if not ffmpeg_exe.exists():
                print("❌ No se encontró ffmpeg.exe en la carpeta extraída")
                return False
            
            # Crear carpeta de destino
            install_dir = Path.home() / "ffmpeg"
            install_dir.mkdir(exist_ok=True)
            
            # Copiar ffmpeg
            dest_exe = install_dir / "ffmpeg.exe"
            shutil.copy2(ffmpeg_exe, dest_exe)
            
            # Agregar al PATH del sistema (temporal)
            current_path = os.environ.get("PATH", "")
            if str(install_dir) not in current_path:
                os.environ["PATH"] = str(install_dir) + os.pathsep + current_path
            
            # Limpiar archivos temporales
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            # Verificar instalación
            try:
                subprocess.run([str(dest_exe), "-version"], capture_output=True, check=True)
                print(f"✅ ffmpeg instalado exitosamente en: {dest_exe}")
                print(f"💡 Agregado temporalmente al PATH. Para permanente, agrega manualmente: {install_dir}")
                return True
            except subprocess.CalledProcessError:
                print("❌ Verificación de ffmpeg falló")
                return False
                
        except Exception as e:
            print(f"❌ Error al instalar ffmpeg en Windows: {e}")
            return False
    
    def _install_ffmpeg_macos(self):
        """Instala ffmpeg en macOS usando Homebrew"""
        try:
            # Verificar si Homebrew está instalado
            try:
                subprocess.run(["brew", "--version"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("❌ Homebrew no está instalado. Instala Homebrew primero:")
                print("   /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
                return False
            
            print("📦 Instalando ffmpeg con Homebrew...")
            result = subprocess.run(["brew", "install", "ffmpeg"], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ ffmpeg instalado exitosamente con Homebrew")
                return True
            else:
                print(f"❌ Error al instalar ffmpeg: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error al instalar ffmpeg en macOS: {e}")
            return False
    
    def _install_ffmpeg_linux(self):
        """Instala ffmpeg en Linux usando el gestor de paquetes del sistema"""
        try:
            # Detectar distribución y gestor de paquetes
            if shutil.which("apt-get"):  # Debian/Ubuntu
                cmd = ["sudo", "apt-get", "update", "&&", "sudo", "apt-get", "install", "-y", "ffmpeg"]
                print("📦 Instalando ffmpeg con apt-get...")
            elif shutil.which("yum"):  # CentOS/RHEL/Fedora antiguo
                cmd = ["sudo", "yum", "install", "-y", "ffmpeg"]
                print("📦 Instalando ffmpeg con yum...")
            elif shutil.which("dnf"):  # Fedora moderno
                cmd = ["sudo", "dnf", "install", "-y", "ffmpeg"]
                print("📦 Instalando ffmpeg con dnf...")
            elif shutil.which("pacman"):  # Arch Linux
                cmd = ["sudo", "pacman", "-S", "--noconfirm", "ffmpeg"]
                print("📦 Instalando ffmpeg con pacman...")
            elif shutil.which("zypper"):  # openSUSE
                cmd = ["sudo", "zypper", "install", "-y", "ffmpeg"]
                print("📦 Instalando ffmpeg con zypper...")
            else:
                print("❌ No se pudo detectar el gestor de paquetes del sistema")
                print("💡 Instala ffmpeg manualmente usando tu gestor de paquetes")
                return False
            
            # Ejecutar comando de instalación
            result = subprocess.run(" ".join(cmd), shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ ffmpeg instalado exitosamente")
                return True
            else:
                print(f"❌ Error al instalar ffmpeg: {result.stderr}")
                print("💡 Puedes intentar instalarlo manualmente:")
                print(f"   {' '.join(cmd)}")
                return False
                
        except Exception as e:
            print(f"❌ Error al instalar ffmpeg en Linux: {e}")
            return False

    def install_python_dependencies(self):
        """Instala dependencias de Python faltantes"""
        python_deps = {
            'scdl': 'scdl',
            'yt-dlp': 'yt-dlp', 
            'mutagen': 'mutagen',
            'requests': 'requests'
        }
        
        installed = []
        failed = []
        
        for package, import_name in python_deps.items():
            try:
                # Verificar si ya está instalado
                if package in ['scdl', 'yt-dlp']:
                    # Para herramientas de línea de comandos
                    result = subprocess.run([package, '--version'], 
                                          capture_output=True, timeout=10)
                    if result.returncode == 0:
                        continue
                else:
                    # Para paquetes de Python
                    __import__(import_name)
                    continue
            except (ImportError, subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            # Intentar instalar
            try:
                print(f"📦 Instalando {package}...")
                result = subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                                      capture_output=True, text=True, timeout=120)
                
                if result.returncode == 0:
                    print(f"✅ {package} instalado exitosamente")
                    installed.append(package)
                else:
                    print(f"❌ Error al instalar {package}: {result.stderr}")
                    failed.append(package)
            except Exception as e:
                print(f"❌ Error al instalar {package}: {e}")
                failed.append(package)
        
        return installed, failed

    def diagnose_ffmpeg(self):
        """Diagnóstica problemas específicos con ffmpeg y proporciona soluciones"""
        print("🔍 Diagnosticando ffmpeg...")
        
        issues = []
        solutions = []
        
        # 1. Verificar si ffmpeg está en PATH
        ffmpeg_in_path = shutil.which("ffmpeg")
        if ffmpeg_in_path:
            print(f"✅ ffmpeg encontrado en PATH: {ffmpeg_in_path}")
            
            # Verificar si es ejecutable
            try:
                result = subprocess.run([ffmpeg_in_path, "-version"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print("✅ ffmpeg es ejecutable y funcional")
                    version_line = result.stdout.split('\n')[0]
                    print(f"📋 Versión: {version_line}")
                    return True, []
                else:
                    issues.append(f"ffmpeg no ejecutable: {result.stderr}")
                    solutions.append("Reinstalar ffmpeg o verificar permisos")
            except subprocess.TimeoutExpired:
                issues.append("ffmpeg timeout - posible instalación corrupta")
                solutions.append("Reinstalar ffmpeg")
            except Exception as e:
                issues.append(f"Error al ejecutar ffmpeg: {e}")
                solutions.append("Verificar instalación de ffmpeg")
        else:
            issues.append("ffmpeg no encontrado en PATH")
            solutions.append("Instalar ffmpeg o agregarlo al PATH")
        
        # 2. Buscar instalaciones comunes de ffmpeg
        common_paths = []
        if platform.system().lower() == "windows":
            common_paths = [
                Path.home() / "ffmpeg" / "ffmpeg.exe",
                Path("C:/ffmpeg/bin/ffmpeg.exe"),
                Path("C:/Program Files/ffmpeg/bin/ffmpeg.exe"),
                Path("C:/Program Files (x86)/ffmpeg/bin/ffmpeg.exe"),
            ]
        else:
            common_paths = [
                Path("/usr/bin/ffmpeg"),
                Path("/usr/local/bin/ffmpeg"),
                Path("/opt/homebrew/bin/ffmpeg"),
                Path.home() / "bin/ffmpeg"
            ]
        
        found_installations = []
        for path in common_paths:
            if path.exists():
                try:
                    result = subprocess.run([str(path), "-version"], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        found_installations.append(str(path))
                        print(f"✅ ffmpeg encontrado en: {path}")
                except:
                    pass
        
        if found_installations and not ffmpeg_in_path:
            issues.append("ffmpeg instalado pero no en PATH")
            solutions.append(f"Agregar al PATH: {found_installations[0]}")
        
        # 3. Verificar PATH actual
        current_path = os.environ.get("PATH", "")
        print(f"📋 PATH actual contiene {len(current_path.split(os.pathsep))} entradas")
        
        if issues:
            print("\n❌ Problemas encontrados:")
            for i, issue in enumerate(issues, 1):
                print(f"   {i}. {issue}")
            
            print("\n💡 Soluciones sugeridas:")
            for i, solution in enumerate(solutions, 1):
                print(f"   {i}. {solution}")
            
            return False, issues
        
        return True, []

    def fix_ffmpeg_path(self):
        """Intenta arreglar problemas de PATH con ffmpeg"""
        print("🔧 Intentando arreglar PATH de ffmpeg...")
        
        # Buscar instalaciones válidas
        valid_ffmpeg = None
        search_paths = []
        
        if platform.system().lower() == "windows":
            search_paths = [
                Path.home() / "ffmpeg" / "ffmpeg.exe",
                Path("C:/ffmpeg/bin/ffmpeg.exe"),
                Path("C:/Program Files/ffmpeg/bin/ffmpeg.exe"),
                Path("C:/Program Files (x86)/ffmpeg/bin/ffmpeg.exe"),
            ]
        else:
            search_paths = [
                Path("/usr/bin/ffmpeg"),
                Path("/usr/local/bin/ffmpeg"),
                Path("/opt/homebrew/bin/ffmpeg"),
                Path.home() / "bin/ffmpeg"
            ]
        
        for path in search_paths:
            if path.exists():
                try:
                    result = subprocess.run([str(path), "-version"], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        valid_ffmpeg = path
                        break
                except:
                    continue
        
        if valid_ffmpeg:
            # Agregar al PATH de la sesión actual
            ffmpeg_dir = str(valid_ffmpeg.parent)
            current_path = os.environ.get("PATH", "")
            
            if ffmpeg_dir not in current_path:
                os.environ["PATH"] = ffmpeg_dir + os.pathsep + current_path
                print(f"✅ Agregado al PATH de la sesión: {ffmpeg_dir}")
                
                # Verificar que funcione
                try:
                    result = subprocess.run(["ffmpeg", "-version"], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        print("✅ ffmpeg ahora funciona correctamente")
                        return True
                except:
                    pass
            
            print(f"💡 Para hacer permanente, agrega al PATH del sistema: {ffmpeg_dir}")
            return True
        
        return False

    def check_dependencies(self, auto_install_ffmpeg=True):
        """Verifica que las dependencias necesarias estén instaladas"""
        dependencies = {
            'scdl': 'scdl',
            'yt-dlp': 'yt-dlp',
            'ffmpeg': 'ffmpeg'
        }
        
        available = {}
        for name, command in dependencies.items():
            try:
                result = subprocess.run([command, '--version'], 
                                     capture_output=True, text=True, timeout=10)
                available[name] = result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError):
                available[name] = False
        
        # Diagnóstico especial para ffmpeg si no está disponible
        if not available['ffmpeg']:
            print("⚠️ ffmpeg no detectado, ejecutando diagnóstico...")
            
            # Intentar diagnóstico y reparación
            is_working, issues = self.diagnose_ffmpeg()
            
            if not is_working:
                print("🔧 Intentando reparar PATH de ffmpeg...")
                if self.fix_ffmpeg_path():
                    # Verificar nuevamente
                    try:
                        result = subprocess.run(['ffmpeg', '--version'], 
                                             capture_output=True, text=True, timeout=10)
                        available['ffmpeg'] = result.returncode == 0
                        if available['ffmpeg']:
                            print("✅ ffmpeg reparado correctamente")
                    except:
                        available['ffmpeg'] = False
                
                # Si aún no funciona y auto_install_ffmpeg está habilitado
                if not available['ffmpeg'] and auto_install_ffmpeg:
                    print("🔧 Intentando instalación automática de ffmpeg...")
                    if self.install_ffmpeg():
                        # Verificar nuevamente después de la instalación
                        try:
                            result = subprocess.run(['ffmpeg', '--version'], 
                                                 capture_output=True, text=True, timeout=10)
                            available['ffmpeg'] = result.returncode == 0
                            if available['ffmpeg']:
                                print("✅ ffmpeg instalado y verificado correctamente")
                        except (subprocess.TimeoutExpired, FileNotFoundError):
                            available['ffmpeg'] = False
                            print("❌ ffmpeg instalado pero no se puede verificar")
                    else:
                        print("❌ No se pudo instalar ffmpeg automáticamente")
            else:
                available['ffmpeg'] = True
                
        return available
    
    def download_with_scdl(self, url, output_path):
        """Descarga usando scdl (recomendado para SoundCloud)"""
        try:
            # Comando scdl corregido sin --format mp3 que causa error
            cmd = [
                "scdl", 
                "-l", url,
                "--path", str(output_path),
                "--onlymp3",
                "--original-art",
                "--extract-artist",
                "--no-playlist-folder"
            ]
            
            print(f"🎵 Descargando con scdl: {url}")
            print(f"🔧 Comando: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            print(f"📊 Código de salida: {result.returncode}")
            if result.stdout:
                print(f"📤 Salida: {result.stdout}")
            if result.stderr:
                print(f"⚠️ Errores: {result.stderr}")
            
            if result.returncode == 0:
                print("✅ Descarga exitosa con scdl")
                return True
            else:
                print(f"❌ Error con scdl: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Timeout en la descarga con scdl")
            return False
        except Exception as e:
            print(f"❌ Excepción con scdl: {e}")
            return False
    
    def download_with_ytdlp(self, url, output_path):
        """Descarga usando yt-dlp como respaldo"""
        try:
            cmd = [
                "yt-dlp",
                "-x", "--audio-format", "mp3",
                "--audio-quality", "0",
                "--embed-thumbnail",
                "--add-metadata",
                "-o", str(output_path / "%(title)s.%(ext)s"),
                url
            ]
            
            print(f"🎵 Descargando con yt-dlp: {url}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("✅ Descarga exitosa con yt-dlp")
                return True
            else:
                print(f"❌ Error con yt-dlp: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Timeout en la descarga con yt-dlp")
            return False
        except Exception as e:
            print(f"❌ Excepción con yt-dlp: {e}")
            return False
    
    def get_track_info(self, url):
        """Extrae información básica del track de SoundCloud"""
        try:
            # Intentar extraer info con yt-dlp
            cmd = ["yt-dlp", "--dump-json", "--no-download", url]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                info = json.loads(result.stdout)
                return {
                    'title': info.get('title', 'Unknown Title'),
                    'artist': info.get('uploader', 'Unknown Artist'),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail'),
                    'description': info.get('description', '')
                }
        except Exception as e:
            print(f"⚠️ No se pudo extraer información: {e}")
            
        # Fallback: extraer del URL
        parts = url.rstrip('/').split('/')
        if len(parts) >= 2:
            return {
                'title': parts[-1].replace('-', ' ').title(),
                'artist': parts[-2].replace('-', ' ').title(),
                'duration': 0,
                'thumbnail': None,
                'description': ''
            }
        
        return {
            'title': 'Unknown Title',
            'artist': 'Unknown Artist',
            'duration': 0,
            'thumbnail': None,
            'description': ''
        }
    
    def enhance_metadata(self, file_path, track_info):
        """Mejora los metadatos del archivo MP3"""
        if not HAS_METADATA:
            print("⚠️ Bibliotecas de metadatos no disponibles")
            return False
            
        try:
            if METADATA_TYPE == "mutagen":
                return self._enhance_metadata_mutagen(file_path, track_info)
            elif METADATA_TYPE == "eyed3":
                return self._enhance_metadata_eyed3(file_path, track_info)
        except Exception as e:
            print(f"❌ Error al mejorar metadatos: {e}")
            return False
    
    def _enhance_metadata_mutagen(self, file_path, track_info):
        """Mejora metadatos usando mutagen"""
        try:
            audio = MP3(file_path, ID3=ID3)
            audio.add_tags()
            
            # Metadatos básicos
            audio.tags.add(TIT2(encoding=3, text=track_info['title']))
            audio.tags.add(TPE1(encoding=3, text=track_info['artist']))
            audio.tags.add(TALB(encoding=3, text="SoundCloud"))
            audio.tags.add(TPE2(encoding=3, text=track_info['artist']))
            audio.tags.add(COMM(encoding=3, lang='eng', desc='Description', 
                                text=track_info.get('description', '')[:100]))
            
            # Descargar y agregar thumbnail si está disponible
            if track_info.get('thumbnail'):
                try:
                    response = requests.get(track_info['thumbnail'], timeout=10)
                    if response.status_code == 200:
                        audio.tags.add(APIC(
                            encoding=3,
                            mime='image/jpeg',
                            type=3,  # Cover (front)
                            desc='Cover',
                            data=response.content
                        ))
                        print("✅ Portada agregada")
                except Exception as e:
                    print(f"⚠️ No se pudo agregar portada: {e}")
            
            audio.save()
            print("✅ Metadatos mejorados con mutagen")
            return True
            
        except Exception as e:
            print(f"❌ Error con mutagen: {e}")
            return False
    
    def _enhance_metadata_eyed3(self, file_path, track_info):
        """Mejora metadatos usando eyed3"""
        try:
            import eyed3
            audiofile = eyed3.load(file_path)
            
            if audiofile.tag is None:
                audiofile.initTag()
            
            audiofile.tag.title = track_info['title']
            audiofile.tag.artist = track_info['artist']
            audiofile.tag.album = "SoundCloud"
            audiofile.tag.album_artist = track_info['artist']
            
            # Agregar thumbnail si está disponible
            if track_info.get('thumbnail'):
                try:
                    response = requests.get(track_info['thumbnail'], timeout=10)
                    if response.status_code == 200:
                        audiofile.tag.images.set(3, response.content, "image/jpeg")
                        print("✅ Portada agregada")
                except Exception as e:
                    print(f"⚠️ No se pudo agregar portada: {e}")
            
            audiofile.tag.save()
            print("✅ Metadatos mejorados con eyed3")
            return True
            
        except Exception as e:
            print(f"❌ Error con eyed3: {e}")
            return False
    
    def save_single_track_metadata(self, file_path, track_info):
        """Guarda metadatos JSON solo para la canción específica descargada"""
        if not HAS_METADATA:
            return None
            
        try:
            metadata = self.extract_detailed_metadata(file_path, track_info)
            if not metadata:
                return None
            
            # Crear estructura del JSON según el formato solicitado
            json_data = {
                "track_actual": metadata
            }
            
            # Nombre del archivo JSON basado en la canción
            safe_name = re.sub(r'[^\w\s-]', '', f"{track_info['artist']} - {track_info['title']}")
            safe_name = re.sub(r'[-\s]+', '-', safe_name).strip('-')
            json_filename = f"{safe_name}_metadata.json"
            json_path = self.download_folder / json_filename
            
            # Guardar archivo JSON
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Metadatos guardados: {json_path}")
            return str(json_path)
            
        except Exception as e:
            print(f"❌ Error al guardar metadatos: {e}")
            return None

    def extract_detailed_metadata(self, file_path, track_info):
        """Extrae metadatos detallados de un archivo MP3 específico"""
        try:
            if METADATA_TYPE == "mutagen":
                from mutagen.mp3 import MP3
                from mutagen.id3 import ID3
                
                audio = MP3(file_path, ID3=ID3)
                
                # Extraer información básica
                titulo = str(audio.get('TIT2', [''])[0]) if audio.get('TIT2') else track_info.get('title', 'No disponible')
                artista = str(audio.get('TPE1', [''])[0]) if audio.get('TPE1') else track_info.get('artist', 'No disponible')
                album = str(audio.get('TALB', [''])[0]) if audio.get('TALB') else track_info.get('album', 'SoundCloud')
                
                # Calcular duración
                duracion_seg = round(audio.info.length) if audio.info else 0
                
                # Buscar URL de portada
                caratula_url = track_info.get('thumbnail', '')
                if not caratula_url:
                    caratula_url = track_info.get('thumbnails', [{}])[0].get('url', '') if track_info.get('thumbnails') else ''
                
                # Estructura según el formato solicitado
                metadata = {
                    "titulo": titulo,
                    "artista": artista,
                    "album": album,
                    "duracion_seg": duracion_seg,
                    "genero": "Género Desconocido",
                    "plataforma_origen": "SoundCloud",
                    "url_origen": track_info.get('webpage_url', 'No disponible'),
                    "ruta_local": str(file_path).replace('\\', '\\\\'),
                    "caratula_url": caratula_url,
                    "letra": "Letra no disponible",
                    "track_id": track_info.get('id', 'No disponible'),
                    "isrc": "No disponible",
                    "fecha_extraccion": datetime.datetime.now().isoformat(),
                    "release_date": track_info.get('release_date', 'No disponible'),
                    "genres_list": []
                }
                
                return metadata
            
            elif METADATA_TYPE == "eyed3":
                import eyed3
                audiofile = eyed3.load(file_path)
                
                # Extraer información básica
                titulo = audiofile.tag.title if audiofile.tag and audiofile.tag.title else track_info.get('title', 'No disponible')
                artista = audiofile.tag.artist if audiofile.tag and audiofile.tag.artist else track_info.get('artist', 'No disponible')
                album = audiofile.tag.album if audiofile.tag and audiofile.tag.album else track_info.get('album', 'SoundCloud')
                
                # Calcular duración
                duracion_seg = round(audiofile.info.time_secs) if audiofile.info else 0
                
                # Buscar URL de portada
                caratula_url = track_info.get('thumbnail', '')
                if not caratula_url:
                    caratula_url = track_info.get('thumbnails', [{}])[0].get('url', '') if track_info.get('thumbnails') else ''
                
                # Estructura según el formato solicitado
                metadata = {
                    "titulo": titulo,
                    "artista": artista,
                    "album": album,
                    "duracion_seg": duracion_seg,
                    "genero": "Género Desconocido",
                    "plataforma_origen": "SoundCloud",
                    "url_origen": track_info.get('webpage_url', 'No disponible'),
                    "ruta_local": str(file_path).replace('\\', '\\\\'),
                    "caratula_url": caratula_url,
                    "letra": "Letra no disponible",
                    "track_id": track_info.get('id', 'No disponible'),
                    "isrc": "No disponible",
                    "fecha_extraccion": datetime.datetime.now().isoformat(),
                    "release_date": track_info.get('release_date', 'No disponible'),
                    "genres_list": []
                }
                
                return metadata
                
        except Exception as e:
            print(f"⚠️ Error al extraer metadatos detallados: {e}")
            return None

    def organize_downloaded_file(self, file_path):
        """Organiza el archivo descargado: mueve a data/music"""
        try:
            # Asegurar que la carpeta de música exista
            self.download_folder.mkdir(parents=True, exist_ok=True)
            
            # Nombre limpio para el archivo
            clean_name = re.sub(r'[^\w\s.-]', '', file_path.stem)
            clean_name = re.sub(r'[-\s]+', '-', clean_name).strip('-')
            final_mp3_path = self.download_folder / f"{clean_name}.mp3"
            
            # Mover archivo a data/music si no está ya ahí
            if file_path.parent != self.download_folder:
                if not final_mp3_path.exists():
                    file_path.rename(final_mp3_path)
                    print(f"📁 Archivo movido a: {final_mp3_path}")
                else:
                    print(f"📁 Archivo ya existe en destino: {final_mp3_path}")
                    final_mp3_path = file_path
            else:
                final_mp3_path = file_path
            
            return final_mp3_path
            
        except Exception as e:
            print(f"❌ Error al organizar archivo: {e}")
            return file_path

    def find_downloaded_files(self, output_path):
        """Encuentra archivos MP3 descargados en la carpeta"""
        mp3_files = list(Path(output_path).glob("*.mp3"))
        return sorted(mp3_files, key=lambda x: x.stat().st_mtime, reverse=True)
    
    def convert(self, url, custom_name=None):
        """Convierte un link de SoundCloud a MP3"""
        if not self.validate_soundcloud_url(url):
            print("❌ URL no válida de SoundCloud")
            return None
        
        print(f"🎵 Iniciando conversión: {url}")
        
        # Verificar dependencias
        deps = self.check_dependencies()
        print(f"📋 Dependencias: {deps}")
        
        if not any(deps.values()):
            print("❌ No hay herramientas de descarga disponibles")
            print("Instala: pip install scdl o pip install yt-dlp")
            return None
        
        # Obtener información del track
        track_info = self.get_track_info(url)
        print(f"📝 Info extraída: {track_info['title']} - {track_info['artist']}")
        
        # Crear carpeta específica para este download
        safe_name = re.sub(r'[^\w\s-]', '', f"{track_info['artist']} - {track_info['title']}")
        safe_name = re.sub(r'[-\s]+', '-', safe_name).strip('-')
        
        if custom_name:
            safe_name = re.sub(r'[^\w\s-]', '', custom_name)
            safe_name = re.sub(r'[-\s]+', '-', safe_name).strip('-')
        
        output_path = self.download_folder / safe_name
        output_path.mkdir(exist_ok=True)
        
        # Intentar descarga con diferentes métodos
        download_success = False
        
        if deps['scdl']:
            download_success = self.download_with_scdl(url, output_path)
        
        if not download_success and deps['yt-dlp']:
            download_success = self.download_with_ytdlp(url, output_path)
        
        if not download_success:
            print("❌ Falló la descarga con todos los métodos")
            return None
        
        # Encontrar archivo descargado
        mp3_files = self.find_downloaded_files(output_path)
        
        if not mp3_files:
            print("❌ No se encontraron archivos MP3")
            return None
        
        downloaded_file = mp3_files[0]
        print(f"📁 Archivo descargado: {downloaded_file}")
        
        # Mejorar metadatos
        if HAS_METADATA:
            self.enhance_metadata(downloaded_file, track_info)
        
        # Organizar archivo: mover a data/music y extraer portada
        final_path = self.organize_downloaded_file(downloaded_file)
        
        # Generar metadatos JSON solo para esta canción descargada
        json_path = self.save_single_track_metadata(final_path, track_info)
        
        print(f"✅ Conversión completada: {final_path}")
        if json_path:
            print(f"📋 Metadatos disponibles en: {json_path}")
        return str(final_path)

def convert_soundcloud_playlist(playlist_url, download_folder="data/music"):
    """Convierte una playlist completa de SoundCloud"""
    converter = SoundCloudConverter(download_folder)
    
    print(f"🎵 Procesando playlist: {playlist_url}")
    
    try:
        # Extraer URLs individuales de la playlist
        cmd = ["yt-dlp", "--flat-playlist", "--dump-json", playlist_url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            print("❌ Error al procesar playlist")
            return []
        
        urls = []
        for line in result.stdout.strip().split('\n'):
            if line:
                try:
                    info = json.loads(line)
                    if 'url' in info:
                        urls.append(info['url'])
                except:
                    continue
        
        print(f"📋 Encontradas {len(urls)} canciones en la playlist")
        
        downloaded_files = []
        for i, url in enumerate(urls, 1):
            print(f"\n🎵 Procesando {i}/{len(urls)}: {url}")
            try:
                file_path = converter.convert(url)
                if file_path:
                    downloaded_files.append(file_path)
                    print(f"✅ {i}/{len(urls)} completado")
                else:
                    print(f"❌ {i}/{len(urls)} falló")
            except Exception as e:
                print(f"❌ Error en {i}/{len(urls)}: {e}")
        
        print(f"\n🎉 Playlist completada: {len(downloaded_files)}/{len(urls)} exitosas")
        return downloaded_files
        
    except Exception as e:
        print(f"❌ Error al procesar playlist: {e}")
        return []

def test_ffmpeg():
    """Función de testing rápido para verificar ffmpeg"""
    print("🧪 Testing específico de ffmpeg")
    print("=" * 50)
    
    converter = SoundCloudConverter()
    
    # 1. Diagnóstico completo
    print("\n🔍 Paso 1: Diagnóstico completo")
    is_working, issues = converter.diagnose_ffmpeg()
    
    if not is_working:
        # 2. Intentar reparar
        print("\n🔧 Paso 2: Intentando reparación")
        if converter.fix_ffmpeg_path():
            print("✅ Reparación exitosa")
        else:
            print("❌ Reparación falló")
        
        # 3. Verificar nuevamente
        print("\n🔍 Paso 3: Verificación final")
        is_working, _ = converter.diagnose_ffmpeg()
    
    if is_working:
        print("\n🎉 ¡ffmpeg está funcionando correctamente!")
        
        # Test adicional: verificar codecs
        try:
            result = subprocess.run(['ffmpeg', '-codecs'], 
                                  capture_output=True, text=True, timeout=5)
            if 'mp3' in result.stdout.lower():
                print("✅ Codec MP3 disponible")
            else:
                print("⚠️ Codec MP3 podría no estar disponible")
        except:
            print("⚠️ No se pudo verificar codecs")
            
    else:
        print("\n❌ ffmpeg aún no funciona")
        print("💡 Soluciones manuales:")
        print("   1. Descarga ffmpeg desde: https://ffmpeg.org/download.html")
        print("   2. Extrae en C:\\ffmpeg\\")
        print("   3. Agrega C:\\ffmpeg\\bin\\ al PATH del sistema")
        print("   4. Reinicia la terminal")
    
    return is_working

# Función de conveniencia
def descargar_soundcloud(url, carpeta_destino="data/music", nombre_personalizado=None):
    """
    Función simple para descargar de SoundCloud
    
    Args:
        url: Link de SoundCloud
        carpeta_destino: Carpeta donde guardar
        nombre_personalizado: Nombre personalizado para el archivo
    
    Returns:
        Ruta del archivo descargado o None si falló
    """
    converter = SoundCloudConverter(carpeta_destino)
    return converter.convert(url, nombre_personalizado)

# Ejemplo de uso y testing
if __name__ == "__main__":
    print("🎵 Conversor de SoundCloud a MP3")
    print("=" * 50)
    
    # URLs de ejemplo (reemplazar con URLs reales)
    test_urls = [
        "https://soundcloud.com/fakemink/ragebait-prod-deer-park",  # Reemplazar con URL real
        # "https://soundcloud.com/user/sets/playlist-name",  # Para playlist
    ]
    
    converter = SoundCloudConverter()
    
    # Verificar si se debe hacer testing de ffmpeg
    if len(sys.argv) > 1 and sys.argv[1] == "--test-ffmpeg":
        test_ffmpeg()
        sys.exit(0)
    
    # Verificar si se debe configurar el entorno
    setup_needed = len(sys.argv) > 1 and sys.argv[1] == "--setup"
    
    if setup_needed:
        print("🔧 Configurando entorno automáticamente...")
        if converter.setup_environment():
            print("\n🎉 ¡Configuración completada!")
        else:
            print("\n⚠️ Configuración incompleta. Revisa los errores arriba.")
        sys.exit(0)
    
    # Verificar dependencias con auto-instalación de ffmpeg
    print("🔍 Verificando dependencias...")
    deps = converter.check_dependencies(auto_install_ffmpeg=True)
    print(f"📋 Estado de dependencias:")
    for tool, available in deps.items():
        status = "✅ Disponible" if available else "❌ No disponible"
        print(f"   {tool}: {status}")
    
    if not any(deps.values()):
        print("\n❌ Sin herramientas de descarga disponibles")
        print("🔧 Para instalar automáticamente todas las dependencias:")
        print(f"   python {__file__} --setup")
        print("\n📦 O instala manualmente:")
        print("   pip install scdl yt-dlp mutagen requests")
        sys.exit(1)
    
    # Mensaje de ayuda
    print(f"\n📖 Uso:")
    print(f"   python {__file__} <url_soundcloud>           # Convertir una canción")
    print(f"   python {__file__} --setup                    # Configurar entorno automáticamente")
    print(f"   python {__file__} --test-ffmpeg              # Diagnosticar problemas con ffmpeg")
    print(f"   O edita test_urls en el código para probar")
    
    # Procesar argumentos de línea de comandos
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        url = sys.argv[1]
        print(f"\n🎵 Procesando URL de argumentos: {url}")
        result = converter.convert(url)
        if result:
            print(f"\n🎉 ¡Descarga exitosa!: {result}")
        else:
            print(f"\n❌ Descarga falló")
    else:
        print(f"\n💡 Para probar, proporciona una URL como argumento:")
        print(f"   python {__file__} https://soundcloud.com/fakemink/ragebait-prod-deer-park")
        print(f"\n🔧 Para configurar dependencias automáticamente:")
        print(f"   python {__file__} --setup")
        print(f"\n🧪 Para diagnosticar problemas con ffmpeg:")
        print(f"   python {__file__} --test-ffmpeg")
