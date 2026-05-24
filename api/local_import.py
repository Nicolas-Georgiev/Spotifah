import os
import shutil
import base64
import sys

_src_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)


class LocalImportMixin:
    def select_files_dialog(self) -> dict:
        try:
            import tkinter.filedialog
            import tkinter
            root = tkinter.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            files = tkinter.filedialog.askopenfilenames(
                title="Seleccionar archivos de audio",
                filetypes=[
                    ("Archivos de audio", "*.mp3 *.wav *.flac *.m4a *.ogg *.wma"),
                    ("MP3", "*.mp3"),
                    ("WAV", "*.wav"),
                    ("FLAC", "*.flac"),
                    ("M4A", "*.m4a"),
                    ("OGG", "*.ogg"),
                    ("WMA", "*.wma"),
                    ("Todos los archivos", "*.*"),
                ],
            )
            root.destroy()
            if files:
                return {"ok": True, "data": {"files": list(files)}}
            return {"ok": False, "error": "No se seleccionaron archivos"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def import_local_files(self, file_paths: list) -> dict:
        if not file_paths:
            return {"ok": False, "error": "No se proporcionaron archivos"}

        imported = []
        errors = []

        for file_path in file_paths:
            try:
                song_data = self._import_single_local_file(file_path)
                if song_data:
                    imported.append(song_data)
                else:
                    errors.append({"file": file_path, "error": "No se pudo importar el archivo"})
            except Exception as e:
                errors.append({"file": file_path, "error": str(e)})

        return {
            "ok": True,
            "data": {
                "imported": imported,
                "errors": errors,
                "total": len(imported),
            },
        }

    def _import_single_local_file(self, file_path: str) -> dict | None:
        if not os.path.exists(file_path):
            return None

        metadata = self._extract_metadata(file_path)

        dest_filename = self._get_unique_filename(file_path, metadata)
        dest_path = os.path.join(self._music_dir, dest_filename)
        shutil.copy2(file_path, dest_path)

        if "caratula_blob" in metadata and metadata["caratula_blob"]:
            metadata["caratula_base64"] = base64.b64encode(metadata.pop("caratula_blob")).decode("utf-8")

        metadata.update({
            "ruta_local": dest_path,
            "plataforma_origen": "local",
        })

        from model.db_adapter import upsert_cancion_json
        db_path = self.db.db_path if hasattr(self.db, "db_path") else None
        saved = upsert_cancion_json(metadata, db_path=db_path)

        if saved:
            song_id = saved.get("id_cancion")
            if song_id:
                from model.db_adapter import registrar_descarga
                registrar_descarga(song_id, db_path=db_path)
            return {
                "id": str(song_id) if song_id else None,
                "title": saved.get("titulo", ""),
                "artist": saved.get("artista", ""),
                "album": saved.get("album", ""),
                "duration": saved.get("duracion_seg", 0) or 0,
                "genre": saved.get("genero", ""),
                "path": dest_path,
                "source": "local",
            }
        return None

    def _extract_metadata(self, file_path: str) -> dict:
        import mutagen
        from mutagen.mp3 import MP3
        from mutagen.flac import FLAC
        from mutagen.oggvorbis import OggVorbis
        from mutagen.wave import WAVE
        from mutagen.mp4 import MP4

        ext = os.path.splitext(file_path)[1].lower()
        filename = os.path.splitext(os.path.basename(file_path))[0]
        metadata = {"titulo": filename, "artista": "", "album": "", "duracion_seg": None, "genero": ""}

        try:
            if ext == ".mp3":
                audio = MP3(file_path)
            elif ext == ".flac":
                audio = FLAC(file_path)
            elif ext == ".ogg":
                audio = OggVorbis(file_path)
            elif ext == ".wav":
                audio = WAVE(file_path)
            elif ext == ".m4a":
                audio = MP4(file_path)
            else:
                audio = mutagen.File(file_path)
                if audio is None:
                    return metadata
        except Exception:
            return metadata

        try:
            if audio.info and audio.info.length:
                metadata["duracion_seg"] = int(audio.info.length)
        except Exception:
            pass

        try:
            if ext == ".mp3":
                tag = audio.tags
                if tag:
                    if tag.get("TIT2"):
                        metadata["titulo"] = str(tag["TIT2"])
                    if tag.get("TPE1"):
                        metadata["artista"] = str(tag["TPE1"])
                    if tag.get("TALB"):
                        metadata["album"] = str(tag["TALB"])
                    if tag.get("TCON"):
                        metadata["genero"] = str(tag["TCON"])
                    if tag.get("APIC"):
                        metadata["caratula_blob"] = tag["APIC"].data
            elif ext == ".flac":
                if audio.get("title"):
                    metadata["titulo"] = audio["title"][0]
                if audio.get("artist"):
                    metadata["artista"] = audio["artist"][0]
                if audio.get("album"):
                    metadata["album"] = audio["album"][0]
                if audio.get("genre"):
                    metadata["genero"] = audio["genre"][0]
                if audio.pictures:
                    metadata["caratula_blob"] = audio.pictures[0].data
            elif ext == ".ogg":
                if audio.get("title"):
                    metadata["titulo"] = audio["title"][0]
                if audio.get("artist"):
                    metadata["artista"] = audio["artist"][0]
                if audio.get("album"):
                    metadata["album"] = audio["album"][0]
                if audio.get("genre"):
                    metadata["genero"] = audio["genre"][0]
            elif ext == ".m4a":
                if audio.get("\xa9nam"):
                    metadata["titulo"] = audio["\xa9nam"][0]
                if audio.get("\xa9ART"):
                    metadata["artista"] = audio["\xa9ART"][0]
                if audio.get("\xa9alb"):
                    metadata["album"] = audio["\xa9alb"][0]
                if audio.get("\xa9gen"):
                    metadata["genero"] = audio["\xa9gen"][0]
                if "covr" in audio:
                    cover_data = audio["covr"][0]
                    if hasattr(cover_data, "data"):
                        metadata["caratula_blob"] = cover_data.data
                    else:
                        metadata["caratula_blob"] = bytes(cover_data)
        except Exception:
            pass

        titulo = metadata.get("titulo", "").strip()
        if not titulo:
            metadata["titulo"] = filename

        return metadata

    def _get_unique_filename(self, file_path: str, metadata: dict) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        if not ext:
            ext = ".mp3"

        artist = (metadata.get("artista") or "").strip()
        title = (metadata.get("titulo") or "").strip()

        if artist and title:
            base = f"{artist} - {title}"
        else:
            base = os.path.splitext(os.path.basename(file_path))[0]

        safe_base = "".join(c for c in base if c not in r'<>:"/\|?*').strip()
        if not safe_base:
            safe_base = "track"

        dest = os.path.join(self._music_dir, f"{safe_base}{ext}")
        if not os.path.exists(dest):
            return f"{safe_base}{ext}"

        counter = 1
        while True:
            dest = os.path.join(self._music_dir, f"{safe_base}_{counter}{ext}")
            if not os.path.exists(dest):
                return f"{safe_base}_{counter}{ext}"
            counter += 1
