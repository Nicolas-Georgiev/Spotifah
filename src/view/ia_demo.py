"""
IA demo 

Propósito:
- Script de demostración y experimentación para el motor de recomendaciones.
- Construye un `RecommendationEngine` local, calcula embeddings (puede descargar modelos de HF)
    y muestra recomendaciones.

Notas:
- No forma parte del flujo normal de `app.py` ni de la API; es una utilidad local para desarrolladores.
- La primera ejecución puede descargar pesos desde Hugging Face (usa `HF_TOKEN` para mejores límites).
- Consume CPU/RAM durante la generación de embeddings.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from controller.recommender_engine import RecommendationEngine
from databaseManager.db import Database
from model.recommender_models import Artist, ListeningEvent, Song


class SQLiteMusicDataSource:
    """Wrapper ligero que consulta la base ekho.db usando `Database`."""

    def __init__(self, db_path: str | None = None) -> None:
        db = Database(db_path)
        self.db_path = db.db_path

    def _connect(self):
        conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        return conn

    def get_songs(self) -> list[Song]:
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT c.id_cancion, c.titulo, c.artista, c.album, c.genero,
                       c.duracion_seg, c.plataforma_origen, c.ruta_local, c.caratula_url,
                       c.fecha_importacion,
                       COUNT(h.id_historial) AS play_count
                FROM canciones c
                LEFT JOIN historial_reproduccion h ON h.id_cancion = c.id_cancion
                GROUP BY c.id_cancion
                ORDER BY c.titulo COLLATE NOCASE
                """
            )
            songs: list[Song] = []
            for row in cur.fetchall():
                songs.append(
                    Song(
                        id=int(row["id_cancion"]),
                        title=row["titulo"] or "",
                        artist=row["artista"] or "",
                        album=row["album"] or None,
                        genre=row["genero"] or None,
                        duration=int(row["duracion_seg"] or 0) or None,
                        source=row["plataforma_origen"] or "local",
                        added_at=_parse_datetime(row["fecha_importacion"]),
                        play_count=int(row["play_count"] or 0),
                        path=row["ruta_local"] or "",
                        cover_url=row["caratula_url"] or "",
                    )
                )
            return songs
        finally:
            conn.close()

    def get_song(self, song_id: int) -> Song | None:
        for song in self.get_songs():
            if song.id == song_id:
                return song
        return None

    def get_artists(self) -> list[Artist]:
        songs = self.get_songs()
        grouped: dict[str, list[Song]] = {}
        for song in songs:
            grouped.setdefault(song.artist.casefold(), []).append(song)

        artists: list[Artist] = []
        seen: set[str] = set()
        for song in songs:
            key = song.artist.casefold()
            if not song.artist or key in seen:
                continue
            artist_songs = grouped.get(key, [])
            genres = sorted({item.genre for item in artist_songs if item.genre})
            popularity = float(sum(item.play_count for item in artist_songs))
            artists.append(Artist(id=len(artists) + 1, name=song.artist, genres=genres, popularity=popularity))
            seen.add(key)

        return artists

    def get_listening_history(self) -> list[ListeningEvent]:
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id_historial, id_cancion, fecha_reproduccion
                FROM historial_reproduccion
                ORDER BY fecha_reproduccion ASC, id_historial ASC
                """
            )
            history: list[ListeningEvent] = []
            for row in cur.fetchall():
                history.append(
                    ListeningEvent(
                        id=int(row["id_historial"]),
                        song_id=int(row["id_cancion"]),
                        listened_at=_parse_datetime(row["fecha_reproduccion"]),
                    )
                )
            return history
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


def _parse_datetime(value: object, default: datetime | None = None) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str) and value.strip():
        normalized = value.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(normalized)
        except ValueError:
            pass
    return default or datetime.now(timezone.utc)


def build_demo_data_source():
    now = datetime.now(timezone.utc)

    artists = [
        Artist(id=1, name="Arctic Monkeys", genres=["indie rock", "alternative rock"], popularity=88.0),
        Artist(id=2, name="M83", genres=["synthpop", "dream pop"], popularity=76.0),
        Artist(id=3, name="Adele", genres=["pop", "soul"], popularity=95.0),
    ]

    songs = [
        Song(1, "Do I Wanna Know?", "Arctic Monkeys", "AM", "indie rock", 272, "local", now - timedelta(days=120), 45),
        Song(2, "Midnight City", "M83", "Hurry Up, We're Dreaming", "synthpop", 246, "local", now - timedelta(days=80), 18),
        Song(3, "Rolling in the Deep", "Adele", "21", "pop", 228, "spotify", now - timedelta(days=140), 63),
    ]

    history = [
        ListeningEvent(1, 1, now - timedelta(hours=3)),
        ListeningEvent(2, 2, now - timedelta(days=1, hours=4)),
    ]

    class DemoDataSource:
        def get_songs(self):
            return list(songs)

        def get_song(self, song_id: int):
            for song in songs:
                if song.id == song_id:
                    return song
            return None

        def get_artists(self):
            return list(artists)

        def get_listening_history(self):
            return list(history)

        def get_embeddings(self, song_ids: list[int]) -> dict:
            return {}

        def set_embedding(self, song_id: int, vector) -> None:
            pass

    return DemoDataSource()


def _print_items(title: str, items) -> None:
    print(f"\n{title}")
    print("-" * len(title))
    for index, item in enumerate(items, start=1):
        print(f"{index}. {item.title} - {item.artist} | score={item.score:.3f} | {item.reason}")


def main() -> None:
    db = Database()
    source = SQLiteMusicDataSource(db.db_path)
    if not source.get_songs():
        source = build_demo_data_source()
    engine = RecommendationEngine(source)

    print("Backend de embeddings:", engine.embedding_service.backend)
    print("Canciones cargadas:", len(engine.songs))
    print("Artistas cargados:", len(engine.artists))
    print("Historial cargado:", len(engine.history))

    first_song = engine.songs[0]
    similar_songs = engine.get_similar_songs(first_song.id, top_k=5)
    similar_artists = engine.get_similar_artists(first_song.artist, top_k=5)

    _print_items(f"Canciones similares a {first_song.title}", similar_songs)
    _print_items(f"Artistas similares a {first_song.artist}", similar_artists)

    home_recommendations = engine.generate_home_recommendations(top_k=10)
    _print_items("Recomendaciones home", home_recommendations)

    seed_recommendations = engine.recommend_from_seed_songs(engine.songs[:3], top_k=10)
    _print_items("Recomendaciones basadas en semillas", seed_recommendations)

    print("\nEjemplo de embedding:")
    print(first_song.embedding[:8])


if __name__ == "__main__":
    main()
