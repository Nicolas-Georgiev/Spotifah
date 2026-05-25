import os
import sys

_src_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

import sqlite3
from datetime import datetime
from databaseManager.db import Database


class SQLiteMusicDataSource:
    def __init__(self, db_path: str | None = None) -> None:
        db = Database(db_path) if db_path is None else Database(db_path)
        self.db_path = db.db_path

    def _connect(self):
        conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        return conn

    def get_song(self, song_id: int):
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id_cancion, titulo, artista, album, genero, duracion_seg, plataforma_origen, ruta_local, caratula_url, fecha_importacion FROM canciones WHERE id_cancion = ?",
                (int(song_id),),
            )
            row = cur.fetchone()
            if not row:
                return None
            from model.recommender_models import Song
            fecha = row["fecha_importacion"]
            added_at = None
            if fecha:
                try:
                    added_at = datetime.fromisoformat(fecha)
                except Exception:
                    try:
                        added_at = datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        added_at = None

            return Song(
                id=int(row["id_cancion"]),
                title=row["titulo"] or "",
                artist=row["artista"] or "",
                album=row["album"] or None,
                genre=row["genero"] or None,
                duration=int(row["duracion_seg"] or 0) or None,
                source=row["plataforma_origen"] or "local",
                added_at=added_at,
                play_count=0,
                path=row["ruta_local"] or "",
                cover_url=row["caratula_url"] or "",
            )
        finally:
            conn.close()

    def get_songs(self):
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT c.id_cancion, c.titulo, c.artista, c.album, c.genero, c.duracion_seg, c.plataforma_origen, c.ruta_local, c.caratula_url, c.fecha_importacion, COUNT(h.id_historial) AS play_count FROM canciones c LEFT JOIN historial_reproduccion h ON h.id_cancion = c.id_cancion GROUP BY c.id_cancion ORDER BY c.titulo COLLATE NOCASE"
            )
            rows = cur.fetchall()
            from model.recommender_models import Song
            songs = []
            for row in rows:
                fecha = row["fecha_importacion"]
                added_at = None
                if fecha:
                    try:
                        added_at = datetime.fromisoformat(fecha)
                    except Exception:
                        try:
                            added_at = datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")
                        except Exception:
                            added_at = None

                songs.append(
                    Song(
                        id=int(row["id_cancion"]),
                        title=row["titulo"] or "",
                        artist=row["artista"] or "",
                        album=row["album"] or None,
                        genre=row["genero"] or None,
                        duration=int(row["duracion_seg"] or 0) or None,
                        source=row["plataforma_origen"] or "local",
                        added_at=added_at,
                        play_count=int(row["play_count"] or 0),
                        path=row["ruta_local"] or "",
                        cover_url=row["caratula_url"] or "",
                    )
                )
            return songs
        finally:
            conn.close()

    def get_listening_history(self):
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id_historial, id_cancion, fecha_reproduccion FROM historial_reproduccion ORDER BY fecha_reproduccion ASC, id_historial ASC")
            rows = cur.fetchall()
            from model.recommender_models import ListeningEvent
            history = []
            for row in rows:
                history.append(ListeningEvent(id=int(row["id_historial"]), song_id=int(row["id_cancion"]), listened_at=None))
            return history
        finally:
            conn.close()

    def get_artists(self):
        """Devuelve una lista simple de artistas a partir de las canciones."""
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT artista FROM canciones ORDER BY artista COLLATE NOCASE")
            rows = cur.fetchall()
            from model.recommender_models import Artist
            artists = []
            idx = 1
            for row in rows:
                name = row["artista"] or ""
                artists.append(Artist(id=idx, name=name, genres=[], popularity=0.0, embedding=[]))
                idx += 1
            return artists
        finally:
            conn.close()

    def get_embeddings(self, song_ids: list[int]) -> dict:
        try:
            db = Database(self.db_path)
            return db.get_embeddings(song_ids)
        except Exception:
            return {}

    def set_embedding(self, song_id: int, vector) -> None:
        try:
            db = Database(self.db_path)
            db.set_embedding(song_id, vector)
        except Exception:
            pass
from controller.recommender_engine import RecommendationEngine


class RecommendationsMixin:
    def _get_recommendation_engine(self) -> RecommendationEngine:
        db_path = getattr(self.db, "db_path", "")
        try:
            signature = (os.path.getmtime(db_path), os.path.getsize(db_path)) if db_path and os.path.exists(db_path) else (0.0, 0)
        except Exception:
            signature = (0.0, 0)

        if (
            getattr(self, "_recommendation_engine", None) is None
            or getattr(self, "_recommendation_signature", None) != signature
        ):
            source = SQLiteMusicDataSource(db_path)
            self._recommendation_engine = RecommendationEngine(source)
            self._recommendation_signature = signature
        return self._recommendation_engine

    def _playlist_seed_songs(self, playlist_id: str):
        if playlist_id == "all":
            return []
        try:
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT c.id_cancion, c.titulo, c.artista, c.album, c.genero,
                           c.duracion_seg, c.plataforma_origen, c.ruta_local, c.caratula_url,
                           c.fecha_importacion
                    FROM playlist_canciones pc
                    JOIN canciones c ON pc.id_cancion = c.id_cancion
                    WHERE pc.id_playlist = ?
                    ORDER BY pc.orden ASC, c.id_cancion ASC
                    """,
                    (int(playlist_id),),
                )
                rows = cur.fetchall()
                if not rows:
                    return []
                source = self._get_recommendation_engine().source
                from model.recommender_models import Song
                return [song for row in rows if (song := source.get_song(int(row["id_cancion"]))) is not None]
            finally:
                conn.close()
        except Exception:
            return []

    def _serialize_recommendation(self, item):
        metadata = item.metadata or {}
        return {
            "id": str(item.song_id),
            "title": item.title,
            "artist": item.artist,
            "album": metadata.get("album") or "",
            "duration": int(metadata.get("duration") or 0),
            "genre": metadata.get("genre") or "",
            "source": metadata.get("source") or item.source or "local",
            "path": metadata.get("path") or "",
            "cover_url": metadata.get("cover_url") or "",
            "score": round(float(item.score), 3),
            "reason": item.reason,
            "play_count": int(metadata.get("play_count") or 0),
            "added_at": str(metadata.get("added_at") or ""),
        }

    def get_recommendations(self, playlist_id: str = "all", limit: int = 8) -> list:
        try:
            engine = self._get_recommendation_engine()
            if playlist_id == "all":
                recommendations = engine.generate_home_recommendations(top_k=limit)
            else:
                seed_songs = self._playlist_seed_songs(playlist_id)
                recommendations = engine.recommend_from_seed_songs(seed_songs, top_k=limit)
            return [self._serialize_recommendation(item) for item in recommendations]
        except Exception:
            return []
