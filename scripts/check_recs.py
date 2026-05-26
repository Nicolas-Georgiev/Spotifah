#!/usr/bin/env python
"""
Check Recs

Diagnostico de recomendaciones:
- Intenta levantar `Api()` y probar la base real.
"""
from __future__ import annotations

import importlib.util
import os
import sys
from dataclasses import asdict
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if SRC not in sys.path:
    sys.path.insert(0, SRC)


def _load_recommendations_module():
    path = os.path.join(ROOT, "api", "recommendations.py")
    spec = importlib.util.spec_from_file_location("check_recommendations_module", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("No se pudo cargar api/recommendations.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def print_items(label: str, items, limit: int = 8):
    print(f"\n--- {label} ({len(items)}) ---")
    for item in list(items)[:limit]:
        if hasattr(item, "title"):
            print(f"- {item.title} | {item.artist} | score={getattr(item, 'score', 0):.3f} | {getattr(item, 'reason', '')}")
        elif isinstance(item, dict):
            print(f"- {item.get('name') or item.get('title')} | {item.get('artist') or item.get('artists')} | id={item.get('id')}")
        else:
            print("-", item)


def run_api_check() -> bool:
    try:
        from api import Api
    except Exception as exc:
        print("Api check omitido:", repr(exc))
        return False

    api = Api()
    conn = api.db.get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row["name"] for row in cur.fetchall()]
        print("tables:", tables)

        for table in ("canciones", "embeddings", "historial_reproduccion"):
            try:
                cur.execute(f"SELECT COUNT(*) as c FROM {table}")
                print(f"{table}:", cur.fetchone()["c"])
            except Exception:
                print(f"{table}: (no existe)")

        print("\nSample canciones:")
        try:
            cur.execute("SELECT id_cancion, titulo, artista, ruta_local FROM canciones LIMIT 10")
            for row in cur.fetchall():
                print(dict(row))
        except Exception:
            print("(no se pudo leer canciones)")
    finally:
        conn.close()

    print("\n--- Engine real ---")
    engine = api._get_recommendation_engine()
    print("engine songs count:", len(getattr(engine, "songs", [])))
    print("engine history count:", len(getattr(engine, "history", [])))
    print_items("generate_home_recommendations", engine.generate_home_recommendations(top_k=8))
    print_items("_rank_by_popularity", engine._rank_by_popularity(8, "test"))
    print_items("api.get_recommendations", api.get_recommendations("all", 8))
    return True


class ManualSource:
    def __init__(self):
        from model.recommender_models import ListeningEvent, Song

        now = datetime.utcnow()
        self.songs = [
            Song(1, "Daft Punk - One More Time (Official Video)", "DaftPunkVEVO", "Discovery", "electronic", 320, "YouTube", now - timedelta(days=12), 6),
            Song(2, "Harder Better Faster Stronger", "Daft Punk", "Discovery", "electronic", 224, "Spotify", now - timedelta(days=20), 4),
            Song(3, "The Less I Know The Better", "Tame Impala", "Currents", "indie", 216, "YouTube", now - timedelta(days=4), 8),
            Song(4, "Let It Happen", "Tame Impala", "Currents", "indie", 467, "local", now - timedelta(days=2), 3),
            Song(5, "Billie Jean", "Michael Jackson", "Thriller", "pop", 294, "YouTube", now - timedelta(days=30), 5),
            Song(6, "Blinding Lights", "The Weeknd", "After Hours", "pop", 200, "Spotify", now - timedelta(days=1), 9),
            Song(7, "Instant Crush", "Daft Punk ft. Julian Casablancas", "Random Access Memories", "electronic", 337, "local", now - timedelta(days=9), 2),
            Song(8, "Sofia", "Clairo", "Immunity", "indie pop", 188, "local", now - timedelta(days=7), 7),
            Song(9, "Bad Habit", "Steve Lacy", "Gemini Rights", "r&b", 232, "YouTube", now - timedelta(days=5), 3),
            Song(10, "Redbone", "Childish Gambino", "Awaken, My Love!", "funk", 326, "local", now - timedelta(days=15), 2),
        ]
        self.history = [
            ListeningEvent(1, 1, now - timedelta(days=6)),
            ListeningEvent(2, 3, now - timedelta(days=4)),
            ListeningEvent(3, 6, now - timedelta(days=2)),
            ListeningEvent(4, 8, now - timedelta(hours=6)),
        ]
        self.embeddings = {}

    def get_songs(self):
        return self.songs

    def get_song(self, song_id: int):
        return next((song for song in self.songs if song.id == int(song_id)), None)

    def get_artists(self):
        from model.recommender_models import Artist

        names = []
        for song in self.songs:
            if song.artist not in names:
                names.append(song.artist)
        return [Artist(index + 1, name) for index, name in enumerate(names)]

    def get_listening_history(self):
        return self.history

    def get_embeddings(self, song_ids: list[int]) -> dict:
        return {song_id: self.embeddings[song_id] for song_id in song_ids if song_id in self.embeddings}

    def set_embedding(self, song_id: int, vector) -> None:
        self.embeddings[int(song_id)] = list(vector)


class ManualRecommendations:
    def __init__(self, mixin_cls):
        self.mixin = mixin_cls()

    def __getattr__(self, name):
        return getattr(self.mixin, name)


def run_manual_check():
    recs_module = _load_recommendations_module()
    from controller.recommender_engine import RecommendationEngine

    source = ManualSource()
    engine = RecommendationEngine(source)
    helper = ManualRecommendations(recs_module.RecommendationsMixin)

    print("\n--- Engine manual ---")
    print("manual songs count:", len(engine.songs))
    print("manual history count:", len(engine.history))
    print_items("manual generate_home_recommendations", engine.generate_home_recommendations(top_k=8))

    seeds = helper._mixed_seed_songs(engine, "all", limit=8)
    print_items("manual mixed seeds", [asdict(song) for song in seeds])

    fake_spotify_tracks = [
        {"id": "sp1", "name": "One More Time", "artists": [{"name": "Daft Punk"}]},
        {"id": "sp2", "name": "One More Time - Radio Edit", "artists": [{"name": "Daft Punk"}]},
        {"id": "sp3", "name": "Let It Happen", "artists": [{"name": "Tame Impala"}]},
        {"id": "sp4", "name": "Borderline", "artists": [{"name": "Tame Impala"}]},
        {"id": "sp5", "name": "Borderline", "artists": [{"name": "Tame Impala"}]},
        {"id": "sp6", "name": "Digital Love", "artists": [{"name": "Daft Punk"}]},
        {"id": "sp7", "name": "Nangs", "artists": [{"name": "Tame Impala"}]},
        {"id": "sp8", "name": "After Dark", "artists": [{"name": "Mr.Kitty"}]},
        {"id": "sp9", "name": "After Dark", "artists": [{"name": "Mr Kitty"}]},
        {"id": "sp10", "name": "Sweet Disposition", "artists": [{"name": "The Temper Trap"}]},
    ]
    existing_titles = {
        title_key
        for song in engine.songs
        for title_key in helper._title_identity_keys(song.title)
    }
    existing_pairs = {helper._song_identity(song) for song in engine.songs if helper._song_identity(song)[0]}
    filtered = helper._dedupe_spotify_tracks(
        fake_spotify_tracks,
        existing_titles=existing_titles,
        existing_pairs=existing_pairs,
        limit=8,
        max_per_artist=1,
    )
    print_items("manual spotify dedupe", filtered)

    print("\nEsperado:")
    print("- No debe aparecer One More Time ni Let It Happen porque ya estan en la biblioteca.")
    print("- No debe repetir Borderline/After Dark.")
    print("- No debe meter mas de una cancion por artista en la tanda filtrada.")


def main():
    if not run_api_check():
        run_manual_check()


if __name__ == "__main__":
    main()
