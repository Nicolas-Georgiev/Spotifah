import os
import json
import hashlib
import urllib.request


class CoversMixin:
    def _localize_cover(self, song_id: int, external_url: str) -> str:
        if not external_url or external_url.startswith("/api/covers/"):
            return external_url
        try:
            url_lower = external_url.lower()
            ext = "jpg"
            for c in ["png", "webp", "jpeg", "gif"]:
                if f".{c}" in url_lower or f"image={c}" in url_lower:
                    ext = "jpeg" if c == "jpeg" else c
                    break
            local_url = f"/api/covers/{song_id}.{ext}"

            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute("SELECT caratula_blob FROM canciones WHERE id_cancion = ?", (song_id,))
                row = cur.fetchone()
                if row and row["caratula_blob"]:
                    return local_url
            finally:
                conn.close()

            with urllib.request.urlopen(external_url) as response:
                image_data = response.read()

            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    "UPDATE canciones SET caratula_blob = ?, caratula_url = ? WHERE id_cancion = ?",
                    (image_data, local_url, song_id),
                )
                conn.commit()
            finally:
                conn.close()

            return local_url
        except Exception:
            return external_url

    def _ensure_cover(self, song_id: int, title: str, artist: str, album: str, mp3_path: str, plataforma: str) -> str:
        for meta_file in ["spotify_metadata.json", "youtube_metadata.json"]:
            meta_path = os.path.join(self._metadata_dir, meta_file)
            if not os.path.exists(meta_path):
                continue
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for track in data.get("tracks", []):
                    cover = track.get("caratula_url", "") or ""
                    if not cover:
                        continue
                    ruta_local = track.get("ruta_local", "") or ""
                    track_title = track.get("titulo", "") or ""
                    track_artist = track.get("artista", "") or ""
                    match = False
                    if ruta_local and mp3_path and os.path.normpath(ruta_local) == os.path.normpath(mp3_path):
                        match = True
                    elif track_title.lower() == title.lower() and track_artist.lower() == artist.lower():
                        match = True
                    elif track_title.lower() == title.lower() and album and track.get("album", "") and track["album"].lower() == album.lower():
                        match = True
                    if match:
                        return self._localize_cover(song_id, cover)
            except Exception:
                continue

        if mp3_path and os.path.exists(mp3_path):
            try:
                from mutagen.mp3 import MP3
                from mutagen.id3 import ID3, APIC
                audio = MP3(mp3_path)
                if audio.tags:
                    for tag in audio.tags.values():
                        if isinstance(tag, APIC):
                            ext = "jpg"
                            if tag.mime == "image/png":
                                ext = "png"
                            elif tag.mime == "image/webp":
                                ext = "webp"
                            local_url = f"/api/covers/{song_id}.{ext}"
                            conn = self.db.get_connection()
                            try:
                                cur = conn.cursor()
                                cur.execute(
                                    "UPDATE canciones SET caratula_blob = ?, caratula_url = ? WHERE id_cancion = ?",
                                    (tag.data, local_url, song_id),
                                )
                                conn.commit()
                            finally:
                                conn.close()
                            return local_url
            except Exception:
                pass

        return ""

    def _cleanup_preview_covers(self):
        for f in os.listdir(self._covers_dir):
            if f.startswith("preview_"):
                try:
                    os.remove(os.path.join(self._covers_dir, f))
                except Exception:
                    pass

    def _localize_preview_cover(self, cover_url: str) -> str:
        if not cover_url or cover_url.startswith("/api/"):
            return cover_url
        self._cleanup_preview_covers()
        h = hashlib.md5(cover_url.encode()).hexdigest()[:16]
        ext = "jpg"
        local = f"/api/covers/preview_{h}.{ext}"
        local_path = os.path.join(self._covers_dir, f"preview_{h}.{ext}")
        if os.path.exists(local_path):
            return local
        try:
            with urllib.request.urlopen(cover_url, timeout=10) as r:
                data = r.read()
            with open(local_path, "wb") as f:
                f.write(data)
            return local
        except Exception:
            return ''

    def delete_preview_cover(self, cover_url: str):
        if not cover_url:
            return
        h = hashlib.md5(cover_url.encode()).hexdigest()[:16]
        local_path = os.path.join(self._covers_dir, f"preview_{h}.jpg")
        try:
            if os.path.exists(local_path):
                os.remove(local_path)
        except Exception:
            pass

    def _playlist_cover_url(self, playlist_id: int) -> str:
        conn = self.db.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT caratula_blob FROM playlists WHERE id_playlist = ?", (playlist_id,))
            row = cur.fetchone()
            if row and row["caratula_blob"]:
                return f"/api/playlist-covers/{playlist_id}.jpg"
        except Exception:
            pass
        finally:
            conn.close()
        return ""
