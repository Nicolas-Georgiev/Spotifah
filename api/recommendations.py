import os
import sys
import time
import json

_src_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

import sqlite3
from datetime import datetime
import re
from random import Random
from types import SimpleNamespace
import requests
from databaseManager.db import Database


class SQLiteMusicDataSource:
    def __init__(self, db_path: str | None = None) -> None:
        db = Database(db_path) if db_path is None else Database(db_path)
        self.db_path = db.db_path

    def _connect(self):
        conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        return conn

    def _parse_datetime(self, value: object) -> datetime | None:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str) and value.strip():
            normalized = value.replace("Z", "+00:00")
            try:
                return datetime.fromisoformat(normalized)
            except Exception:
                pass
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
                try:
                    return datetime.strptime(value, fmt)
                except Exception:
                    continue
        return None

    def _song_from_row(self, row, *, play_count: int = 0):
        from model.recommender_models import Song

        return Song(
            id=int(row["id_cancion"]),
            title=row["titulo"] or "",
            artist=row["artista"] or "",
            album=row["album"] or None,
            genre=row["genero"] or None,
            duration=int(row["duracion_seg"] or 0) or None,
            source=row["plataforma_origen"] or "local",
            added_at=self._parse_datetime(row["fecha_importacion"]),
            play_count=int(play_count or 0),
            path=row["ruta_local"] or "",
            cover_url=row["caratula_url"] or "",
        )

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
            return self._song_from_row(row)
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
            return [self._song_from_row(row, play_count=row["play_count"]) for row in rows]
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
                history.append(
                    ListeningEvent(
                        id=int(row["id_historial"]),
                        song_id=int(row["id_cancion"]),
                        listened_at=self._parse_datetime(row["fecha_reproduccion"]),
                    )
                )
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
    def _recs_debug_enabled(self) -> bool:
        value = os.getenv("RECS_DEBUG", "").strip()
        if not value:
            try:
                dotenv_path = os.path.join(self._project_root, ".env")
                if os.path.exists(dotenv_path):
                    with open(dotenv_path, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if not line or line.startswith("#") or "=" not in line:
                                continue
                            key, raw = line.split("=", 1)
                            key = key.strip()
                            if key == "RECS_DEBUG":
                                value = raw.strip().strip('"').strip("'")
                                break
            except Exception:
                pass
        return value.strip().lower() in {"1", "true", "yes", "on"}

    def _recs_spotify_enabled(self) -> bool:
        value = os.getenv("RECS_SPOTIFY", "1").strip()
        try:
            settings = self._load_settings() if hasattr(self, "_load_settings") else {}
            if isinstance(settings, dict):
                value = str(settings.get("recs_spotify", value) or "").strip()
        except Exception:
            pass
        if not value:
            try:
                dotenv_path = os.path.join(self._project_root, ".env")
                if os.path.exists(dotenv_path):
                    with open(dotenv_path, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if not line or line.startswith("#") or "=" not in line:
                                continue
                            key, raw = line.split("=", 1)
                            if key.strip() == "RECS_SPOTIFY":
                                value = raw.strip().strip('"').strip("'")
                                break
            except Exception:
                pass
        return value.strip().lower() not in {"0", "false", "no", "off"}

    def _recommendation_rng(self, refresh_key=None) -> Random:
        if refresh_key is None:
            refresh_key = time.time_ns()
        return Random(str(refresh_key))

    def _local_recommendations(
        self,
        engine: RecommendationEngine,
        playlist_id: str,
        limit: int,
        refresh_key=None,
    ) -> list:
        if playlist_id == "all":
            recommendations = engine.generate_home_recommendations(top_k=limit)
        else:
            seed_songs = self._playlist_seed_songs(playlist_id)
            recommendations = engine.recommend_from_seed_songs(seed_songs, top_k=limit)

        serialized = [self._serialize_recommendation(item) for item in recommendations]
        rng = self._recommendation_rng(refresh_key)
        rng.shuffle(serialized)
        return self._fill_local_recommendations(
            engine,
            serialized,
            limit,
            refresh_key=refresh_key,
        )

    def _song_recommendation_item(self, song, *, score: float, reason: str):
        return SimpleNamespace(
            song_id=song.id,
            title=song.title,
            artist=song.artist,
            score=score,
            reason=reason,
            source=song.source,
            metadata={
                "album": song.album or "",
                "duration": song.duration or 0,
                "genre": song.genre or "",
                "source": song.source,
                "path": song.path,
                "cover_url": song.cover_url,
                "play_count": song.play_count,
                "added_at": song.added_at or "",
            },
        )

    def _fill_local_recommendations(
        self,
        engine: RecommendationEngine,
        items: list[dict],
        limit: int,
        refresh_key=None,
    ) -> list[dict]:
        if len(items) >= limit:
            return items[:limit]

        seen_ids = {str(item.get("id", "")) for item in items}
        seen_pairs = {
            (
                self._normalize_recommendation_text(item.get("title", "")),
                self._normalize_recommendation_text(item.get("artist", "")),
            )
            for item in items
        }

        rng = self._recommendation_rng(refresh_key)
        songs = list(engine.songs)
        rng.shuffle(songs)
        songs.sort(key=lambda song: (song.play_count, str(song.added_at or "")), reverse=True)
        for song in songs:
            pair = self._song_identity(song)
            if str(song.id) in seen_ids or pair in seen_pairs:
                continue

            item = self._serialize_recommendation(
                self._song_recommendation_item(
                    song,
                    score=0.35,
                    reason="tambien puede encajar",
                )
            )
            items.append(item)
            seen_ids.add(str(song.id))
            seen_pairs.add(pair)
            if len(items) >= limit:
                break

        return items[:limit]

    def _spotify_cached_get(self, url: str, params: dict, *, log_errors: bool = False) -> dict:
        cache = getattr(self, "_spotify_recs_cache", None)
        if cache is None:
            cache = {}
            self._spotify_recs_cache = cache

        key = (url, tuple(sorted((str(k), str(v)) for k, v in params.items())))
        cached = cache.get(key)
        if cached and time.time() - cached[0] < 900:
            return cached[1]

        data = self._spotify_api_get(url, params, log_errors=log_errors)
        cache[key] = (time.time(), data)
        return data

    def _sanitize_title(self, title: str) -> str:
        if not title:
            return ""
        cleaned = re.sub(r"\s+", " ", title).strip()
        cleaned = re.sub(r"\s*[\(\[].*?[\)\]]\s*", " ", cleaned).strip()
        for sep in (" | ", " - ", " \u2013 ", " \u2014 "):
            if sep in cleaned:
                cleaned = cleaned.split(sep, 1)[0].strip()
        return cleaned

    def _get_spotify_client_credentials(self) -> tuple[str | None, str | None]:
        # First check settings.json (saved from UI)
        try:
            settings = self._load_settings() if hasattr(self, "_load_settings") else None
            if isinstance(settings, dict):
                client_id = settings.get("spotify_client_id") or settings.get("SPOTIFY_CLIENT_ID")
                client_secret = settings.get("spotify_client_secret") or settings.get("SPOTIFY_CLIENT_SECRET")
                if client_id and client_secret:
                    return client_id, client_secret
        except Exception:
            pass

        # Then environment variables
        client_id = os.getenv("SPOTIFY_CLIENT_ID") or os.getenv("SPOTDL_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET") or os.getenv("SPOTDL_CLIENT_SECRET")
        if client_id and client_secret:
            return client_id, client_secret

        # Finally fallback to reading .env
        try:
            dotenv_path = os.path.join(self._project_root, ".env")
            if os.path.exists(dotenv_path):
                with open(dotenv_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key in ("SPOTIFY_CLIENT_ID", "SPOTDL_CLIENT_ID") and not client_id:
                            client_id = value
                        if key in ("SPOTIFY_CLIENT_SECRET", "SPOTDL_CLIENT_SECRET") and not client_secret:
                            client_secret = value
        except Exception:
            pass

        return client_id, client_secret

    def _get_spotify_token(self) -> str | None:
        cached = getattr(self, "_spotify_token", None)
        expires_at = getattr(self, "_spotify_token_expires_at", 0)
        if cached and time.time() < float(expires_at) - 60:
            return cached

        # Prefer stored user token (from Authorization Code Flow)
        try:
            settings = self._load_settings() if hasattr(self, "_load_settings") else {}
            user_token = settings.get("spotify_access_token") if isinstance(settings, dict) else None
            user_expires = float(settings.get("spotify_token_expires_at") or 0) if isinstance(settings, dict) else 0
            refresh = settings.get("spotify_refresh_token") if isinstance(settings, dict) else None
            if user_token and time.time() < user_expires - 60:
                self._spotify_token = user_token
                self._spotify_token_expires_at = user_expires
                return user_token

            # Try refresh if we have a refresh token
            if refresh:
                new = self._spotify_refresh_user_token(refresh)
                if new and new.get("access_token"):
                    expires_in = int(new.get("expires_in", 3600))
                    access = new.get("access_token")
                    refresh_token = new.get("refresh_token") or refresh
                    expires_at_val = time.time() + expires_in
                    try:
                        # persist
                        data = {
                            "spotify_access_token": access,
                            "spotify_refresh_token": refresh_token,
                            "spotify_token_expires_at": expires_at_val,
                        }
                        if hasattr(self, "update_settings"):
                            self.update_settings(data)
                        else:
                            # fallback write
                            path = getattr(self, "_settings_file", None)
                            if path:
                                try:
                                    with open(path, "r", encoding="utf-8") as f:
                                        s = json.load(f)
                                except Exception:
                                    s = {}
                                s.update(data)
                                try:
                                    with open(path, "w", encoding="utf-8") as f:
                                        json.dump(s, f, indent=2, ensure_ascii=False)
                                except Exception:
                                    pass
                    except Exception:
                        pass

                    self._spotify_token = access
                    self._spotify_token_expires_at = expires_at_val
                    return access
        except Exception:
            pass

        # fallback to client credentials
        client_id, client_secret = self._get_spotify_client_credentials()
        if not client_id or not client_secret:
            return None

        try:
            response = requests.post(
                "https://accounts.spotify.com/api/token",
                data={"grant_type": "client_credentials"},
                auth=(client_id, client_secret),
                timeout=10,
            )
            response.raise_for_status()
            payload = response.json()
            token = payload.get("access_token")
            expires_in = int(payload.get("expires_in", 3600))
            if token:
                self._spotify_token = token
                self._spotify_token_expires_at = time.time() + expires_in
                return token
        except Exception:
            return None

        return None

    def _spotify_refresh_user_token(self, refresh_token: str) -> dict | None:
        if not refresh_token:
            return None
        client_id, client_secret = self._get_spotify_client_credentials()
        if not client_id or not client_secret:
            return None
        try:
            response = requests.post(
                "https://accounts.spotify.com/api/token",
                data={"grant_type": "refresh_token", "refresh_token": refresh_token},
                auth=(client_id, client_secret),
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

    def _spotify_has_valid_user_token(self) -> bool:
        try:
            settings = self._load_settings() if hasattr(self, "_load_settings") else {}
            return bool(
                isinstance(settings, dict)
                and settings.get("spotify_access_token")
                and settings.get("spotify_token_expires_at")
                and time.time() < float(settings.get("spotify_token_expires_at") or 0) - 60
            )
        except Exception:
            return False

    def _spotify_api_get(self, url: str, params: dict, *, log_errors: bool = True) -> dict:
        """
        Perform a Spotify GET request. On 401 try to refresh the user token once.
        On 403 try client-credentials token as a fallback. Always return a dict
        (empty on failure) so callers don't receive None.
        """
        token = self._get_spotify_token()
        token_type = "user" if self._spotify_has_valid_user_token() else "client-credentials"
        if not token:
            return {}

        def _do_request(tok: str):
            return requests.get(url, params=params, headers={"Authorization": f"Bearer {tok}"}, timeout=4)

        try:
            if self._recs_debug_enabled():
                print(f"[recs] spotify request using token_type: {token_type}", url, params)
            response = _do_request(token)
            response.raise_for_status()
            return response.json() or {}
        except Exception as exc:
            resp = getattr(exc, "response", None)
            status = getattr(resp, "status_code", None) if resp is not None else getattr(exc, 'status_code', None)
            text = (resp.text if resp is not None else getattr(exc, 'text', '')) or ""
            if log_errors and self._recs_debug_enabled():
                print("[recs] spotify api error:", status, url, params)
                if text:
                    print("[recs] spotify api error body:", text[:1000])

            # If 401, try refresh user token once and retry
            try:
                if status == 401:
                    try:
                        settings = self._load_settings() if hasattr(self, "_load_settings") else {}
                        refresh = settings.get("spotify_refresh_token") if isinstance(settings, dict) else None
                        if refresh:
                            new = self._spotify_refresh_user_token(refresh)
                            if new and new.get("access_token"):
                                access = new.get("access_token")
                                expires_in = int(new.get("expires_in", 3600))
                                self._spotify_token = access
                                self._spotify_token_expires_at = time.time() + expires_in
                                if self._recs_debug_enabled():
                                    print("[recs] spotify retrying after refresh with user token", url, params)
                                r2 = _do_request(access)
                                r2.raise_for_status()
                                return r2.json() or {}
                    except Exception:
                        pass

                # If 403, try client credentials token for public endpoints
                if status == 403:
                    try:
                        client_id, client_secret = self._get_spotify_client_credentials()
                        if client_id and client_secret:
                            resp = requests.post(
                                "https://accounts.spotify.com/api/token",
                                data={"grant_type": "client_credentials"},
                                auth=(client_id, client_secret),
                                timeout=10,
                            )
                            resp.raise_for_status()
                            client_token = resp.json().get("access_token")
                            if client_token:
                                if self._recs_debug_enabled():
                                    print("[recs] spotify retrying with client-credentials token", url, params)
                                r2 = requests.get(url, params=params, headers={"Authorization": f"Bearer {client_token}"}, timeout=4)
                                if r2.status_code == 200:
                                    return r2.json() or {}
                    except Exception:
                        pass
            except Exception:
                pass

            return {}

    def _spotify_market(self) -> str:
        return os.getenv("SPOTIFY_MARKET", "US")

    def _clean_search_text(self, value: str) -> str:
        if not value:
            return ""
        cleaned = re.sub(r"https?://\S+", " ", value)
        cleaned = re.sub(
            r"\b(official|video|audio|lyrics?|lyric|visualizer|remaster(?:ed)?|"
            r"explicit|clean|radio edit|extended|mix|hd|hq|mv)\b",
            " ",
            cleaned,
            flags=re.I,
        )
        cleaned = re.sub(r"\b(ft|feat|featuring|with)\.?\s+.*$", " ", cleaned, flags=re.I)
        cleaned = re.sub(r"\s*[\(\[].*?[\)\]]\s*", " ", cleaned)
        return re.sub(r"\s+", " ", cleaned).strip(" -_|")

    def _clean_youtube_artist(self, artist: str) -> str:
        cleaned = self._clean_search_text(artist)
        cleaned = re.sub(r"(?i)vevo$", "", cleaned)
        cleaned = re.sub(r"\b(vevo|topic|official|music|records?|channel)\b", " ", cleaned, flags=re.I)
        return re.sub(r"\s+", " ", cleaned).strip(" -_|")

    def _looks_like_youtube_channel(self, value: str) -> bool:
        value = value or ""
        normalized = value.casefold()
        return any(
            marker in normalized
            for marker in (
                "vevo",
                "official",
                "topic",
                "label",
                "radio",
                "records",
                "tv",
                "fox",
                "bbc",
                "grammy",
                "iheartradio",
            )
        )

    def _humanize_artist_name(self, value: str) -> str:
        value = self._clean_youtube_artist(value)
        value = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", value)
        value = re.sub(r"\s+", " ", value).strip(" -_|")
        return value

    def _artist_candidates_from_song(self, song) -> list[str]:
        title = getattr(song, "title", "") or ""
        artist = getattr(song, "artist", "") or ""
        candidates: list[str] = []

        raw_title = re.sub(r"\s+", " ", title).strip()
        performs_match = re.match(r"^(.+?)\s+performs\b", raw_title, flags=re.I)
        if performs_match:
            possible = self._clean_search_text(performs_match.group(1))
            if possible:
                candidates.append(possible)

        found_separator = False
        for sep in (" - ", " – ", " — ", " | "):
            if sep in raw_title:
                left, _ = raw_title.split(sep, 1)
                left = self._clean_search_text(left)
                if left:
                    candidates.append(left)
                found_separator = True
                break

        match = None if found_separator else re.match(r"^(.+?)\s*[\(\[]", raw_title)
        if match:
            possible = self._clean_search_text(match.group(1))
            if possible:
                candidates.append(possible)

        cleaned_artist = self._humanize_artist_name(artist)
        if cleaned_artist and not self._looks_like_youtube_channel(artist):
            candidates.append(cleaned_artist)

        return list(dict.fromkeys(candidate for candidate in candidates if candidate))

    def _normalize_recommendation_text(self, value: str) -> str:
        cleaned = self._clean_search_text(value)
        cleaned = re.sub(r"[^a-z0-9]+", " ", cleaned.casefold())
        return re.sub(r"\s+", " ", cleaned).strip()

    def _title_identity_keys(self, title: str) -> set[str]:
        keys = set()
        normalized = self._normalize_recommendation_text(title)
        if normalized:
            keys.add(normalized)
        raw_title = re.sub(r"\s+", " ", title or "").strip()
        for sep in (" - ", " \u2013 ", " \u2014 ", " | "):
            if sep not in raw_title:
                continue
            left, right = [part.strip() for part in raw_title.split(sep, 1)]
            for part in (left, right):
                part_key = self._normalize_recommendation_text(part)
                if part_key:
                    keys.add(part_key)
        return keys

    def _spotify_track_identity(self, track: dict) -> tuple[str, str, str]:
        title = track.get("name") or track.get("title") or ""
        artists = track.get("artists", []) or []
        artist = ", ".join(a.get("name", "") for a in artists if a.get("name"))
        return (
            self._normalize_recommendation_text(title),
            self._normalize_recommendation_text(artist),
            track.get("id") or "",
        )

    def _song_identity(self, song) -> tuple[str, str]:
        return (
            self._normalize_recommendation_text(getattr(song, "title", "") or ""),
            self._normalize_recommendation_text(getattr(song, "artist", "") or ""),
        )

    def _spotify_track_exists_locally(self, track: dict, existing_titles: set[str], existing_pairs: set[tuple[str, str]]) -> bool:
        title_key, artist_key, _ = self._spotify_track_identity(track)
        if not title_key:
            return True
        if title_key in existing_titles:
            return True
        if (title_key, artist_key) in existing_pairs:
            return True
        return False

    def _dedupe_spotify_tracks(
        self,
        tracks: list[dict],
        existing_titles: set[str] | None = None,
        existing_pairs: set[tuple[str, str]] | None = None,
        limit: int | None = None,
        max_per_artist: int = 1,
    ) -> list[dict]:
        existing_titles = existing_titles or set()
        existing_pairs = existing_pairs or set()
        seen_ids: set[str] = set()
        seen_titles: set[str] = set()
        seen_pairs: set[tuple[str, str]] = set()
        artist_counts: dict[str, int] = {}
        result: list[dict] = []

        for track in tracks:
            title_key, artist_key, spotify_id = self._spotify_track_identity(track)
            if not title_key:
                continue
            if spotify_id and spotify_id in seen_ids:
                continue
            if title_key in seen_titles or (title_key, artist_key) in seen_pairs:
                continue
            if self._spotify_track_exists_locally(track, existing_titles, existing_pairs):
                continue
            if artist_key and artist_counts.get(artist_key, 0) >= max_per_artist:
                continue

            if spotify_id:
                seen_ids.add(spotify_id)
            seen_titles.add(title_key)
            seen_pairs.add((title_key, artist_key))
            if artist_key:
                artist_counts[artist_key] = artist_counts.get(artist_key, 0) + 1
            result.append(track)
            if limit is not None and len(result) >= limit:
                break

        return result

    def _mixed_seed_songs(self, engine: RecommendationEngine, playlist_id: str, limit: int = 30) -> list:
        if playlist_id == "all":
            candidates = []
            if engine.history:
                candidates.extend(
                    engine._song_by_id.get(event.song_id)
                    for event in reversed(engine.history[-50:])
                )
            candidates.extend(sorted(engine.songs, key=lambda song: song.play_count, reverse=True))
            candidates.extend(sorted(engine.songs, key=lambda song: str(song.added_at or ""), reverse=True))
            candidates.extend(sorted(engine.songs, key=lambda song: Random(song.id).random()))
        else:
            candidates = self._playlist_seed_songs(playlist_id)

        seeds = []
        seen_pairs: set[tuple[str, str]] = set()
        seen_artists: set[str] = set()
        for song in candidates:
            if song is None:
                continue
            title_key, artist_key = self._song_identity(song)
            if not title_key or (title_key, artist_key) in seen_pairs:
                continue
            if artist_key in seen_artists and len(seeds) < max(5, limit // 2):
                continue
            seeds.append(song)
            seen_pairs.add((title_key, artist_key))
            if artist_key:
                seen_artists.add(artist_key)
            if len(seeds) >= limit:
                break

        if len(seeds) < min(limit, 10):
            for song in candidates:
                if song is None:
                    continue
                title_key, artist_key = self._song_identity(song)
                if title_key and (title_key, artist_key) not in seen_pairs:
                    seeds.append(song)
                    seen_pairs.add((title_key, artist_key))
                if len(seeds) >= limit:
                    break
        return seeds

    def _existing_song_identities(self, songs: list) -> tuple[set[str], set[tuple[str, str]]]:
        titles = {
            title_key
            for song in songs
            for title_key in self._title_identity_keys(song.title)
        }
        pairs = {self._song_identity(song) for song in songs if self._song_identity(song)[0]}
        return titles, pairs

    def _spotify_seed_data(self, seed_songs: list, max_ids: int = 12) -> tuple[list[str], list[str], list[str]]:
        track_ids: list[str] = []
        artist_ids: list[str] = []
        artist_names: list[str] = []

        for song in seed_songs:
            title = self._sanitize_title(song.title)
            artist = (song.artist or "").strip()
            artist_name = self._clean_youtube_artist(artist)
            if artist_name and artist_name not in artist_names:
                artist_names.append(artist_name)

            track_id = self._spotify_search_track_id(title, artist)
            if track_id and track_id not in track_ids:
                track_ids.append(track_id)

            if artist:
                artist_id = self._spotify_search_artist_id(artist)
                if artist_id and artist_id not in artist_ids:
                    artist_ids.append(artist_id)

            if len(track_ids) >= max_ids and len(artist_ids) >= max_ids:
                break

        return track_ids, artist_ids, artist_names

    def _spotify_track_search_queries(self, title: str, artist: str) -> list[str]:
        raw_title = re.sub(r"\s+", " ", title or "").strip()
        raw_artist = re.sub(r"\s+", " ", artist or "").strip()
        clean_title = self._clean_search_text(raw_title)
        clean_artist = self._clean_youtube_artist(raw_artist)
        candidates: list[tuple[str, str]] = []

        if clean_title:
            candidates.append((clean_title, clean_artist))

        for sep in (" - ", " \u2013 ", " \u2014 ", " | "):
            if sep in raw_title:
                left, right = [part.strip() for part in raw_title.split(sep, 1)]
                left = self._clean_search_text(left)
                right = self._clean_search_text(right)
                if left and right:
                    candidates.append((right, left))
                    candidates.append((left, right))

        sanitized_title = self._sanitize_title(raw_title)
        if sanitized_title and sanitized_title != clean_title:
            candidates.append((self._clean_search_text(sanitized_title), clean_artist))

        queries: list[str] = []
        for candidate_title, candidate_artist in candidates:
            if not candidate_title:
                continue
            if candidate_artist:
                queries.append(f"track:{candidate_title} artist:{candidate_artist}")
                queries.append(f"{candidate_title} {candidate_artist}")
            queries.append(f"track:{candidate_title}")
            queries.append(candidate_title)

        return list(dict.fromkeys(query for query in queries if query.strip()))

    def _spotify_search_track(self, title: str, artist: str) -> dict | None:
        queries = self._spotify_track_search_queries(title, artist)
        for query in queries:
            params = {"q": query, "type": "track", "limit": 1, "market": self._spotify_market()}
            data = self._spotify_api_get("https://api.spotify.com/v1/search", params)
            tracks = data.get("tracks", {}).get("items", []) if data else []
            if tracks:
                return tracks[0]

        for query in queries:
            data = self._spotify_api_get(
                "https://api.spotify.com/v1/search",
                {"q": query, "type": "track", "limit": 1},
                log_errors=False,
            )
            tracks = data.get("tracks", {}).get("items", []) if data else []
            if tracks:
                return tracks[0]
        return None

    def _spotify_search_track_id(self, title: str, artist: str) -> str | None:
        track = self._spotify_search_track(title, artist)
        if track:
            return track.get("id")
        return None

    def _spotify_search_tracks_by_name(self, title: str, artist: str, limit: int = 10) -> list[dict]:
        queries = self._spotify_track_search_queries(title, artist)
        seen: set[str] = set()
        results: list[dict] = []
        for query in queries:
            data = self._spotify_api_get(
                "https://api.spotify.com/v1/search",
                {"q": query, "type": "track", "limit": max(1, min(int(limit), 20)), "market": self._spotify_market()},
                log_errors=False,
            )
            tracks = data.get("tracks", {}).get("items", []) if data else []
            for track in tracks:
                key = track.get("id") or "|".join([
                    (track.get("name") or "").casefold(),
                    ", ".join(a.get("name", "") for a in track.get("artists", []) if a.get("name")).casefold(),
                ])
                if key and key not in seen:
                    seen.add(key)
                    results.append(track)
                if len(results) >= limit:
                    return results
        return results

    def _spotify_enrich_track_by_name(self, track: dict) -> dict:
        if not track:
            return track
        external_url = track.get("external_urls", {}).get("spotify", "")
        if track.get("id") and external_url:
            return track
        title = track.get("name") or track.get("title") or ""
        artists = track.get("artists", []) or []
        artist = ", ".join(a.get("name", "") for a in artists if a.get("name"))
        found = self._spotify_search_track(title, artist)
        return found or track

    def _spotify_search_artist_id(self, artist: str) -> str | None:
        if not artist:
            return None
        clean_artist = self._clean_youtube_artist(artist)
        queries = [f"artist:{clean_artist}", clean_artist] if clean_artist else []
        queries.extend([f"artist:{artist}", artist])
        for query in list(dict.fromkeys(q for q in queries if q.strip())):
            data = self._spotify_api_get(
                "https://api.spotify.com/v1/search",
                {"q": query, "type": "artist", "limit": 1, "market": self._spotify_market()},
                log_errors=False,
            )
            items = data.get("artists", {}).get("items", []) if data else []
            if items:
                return items[0].get("id")
        return None

    def _spotify_artist_tracks_by_name(self, artist: str, limit: int) -> list[dict]:
        artist_id = self._spotify_search_artist_id(artist)
        if artist_id:
            return self._spotify_related_artist_tracks([artist_id], limit)
        tracks: list[dict] = []
        seen: set[str] = set()
        clean_artist = self._clean_youtube_artist(artist) or artist
        for query in list(dict.fromkeys([f"artist:{clean_artist}", clean_artist, artist])):
            if not query.strip():
                continue
            data = self._spotify_api_get(
                "https://api.spotify.com/v1/search",
                {"q": query, "type": "track", "limit": max(1, min(int(limit), 20)), "market": self._spotify_market()},
                log_errors=False,
            )
            items = data.get("tracks", {}).get("items", []) if data else []
            for item in items:
                key = item.get("id") or (item.get("name") or "").casefold()
                if key and key not in seen:
                    seen.add(key)
                    tracks.append(item)
                if len(tracks) >= limit:
                    return tracks
        return tracks

    def _spotify_tracks_from_seed_names(self, seed_songs: list, limit: int) -> list[dict]:
        tracks: list[dict] = []
        seen: set[str] = set()
        per_seed = 2 if len(seed_songs) > 1 else limit
        for song in seed_songs:
            title = self._sanitize_title(song.title) or song.title
            added_for_seed = 0
            for item in self._spotify_search_tracks_by_name(title, song.artist, limit=max(per_seed, 3)):
                title_key, artist_key, spotify_id = self._spotify_track_identity(item)
                key = spotify_id or "|".join([title_key, artist_key])
                if key and key not in seen:
                    seen.add(key)
                    tracks.append(item)
                    added_for_seed += 1
                if len(tracks) >= limit:
                    return tracks
                if added_for_seed >= per_seed:
                    break
        return tracks

    def _append_spotify_track(
        self,
        tracks: list[dict],
        track: dict,
        seen_track_ids: set[str],
        existing_titles: set[str],
        existing_pairs: set[tuple[str, str]],
    ) -> None:
        track_id = track.get("id")
        title_key, artist_key, _ = self._spotify_track_identity(track)
        if not track_id or track_id in seen_track_ids:
            return
        if title_key in existing_titles or (title_key, artist_key) in existing_pairs:
            return

        seen_track_ids.add(track_id)
        tracks.append(track)

    def _spotify_track_to_recommendation(self, track: dict, index: int, limit: int) -> dict:
        artists = track.get("artists", []) or []
        album = track.get("album", {}) or {}
        images = album.get("images", []) or []
        score = 1.0 - min((index - 1) / max(limit, 1), 0.75)

        return {
            "id": track.get("id") or f"spotify:{index}",
            "title": track.get("name") or "",
            "artist": ", ".join(a.get("name", "") for a in artists if a.get("name")),
            "album": album.get("name", ""),
            "duration": int((track.get("duration_ms") or 0) / 1000),
            "genre": "",
            "source": "spotify",
            "path": "",
            "cover_url": images[0].get("url") if images else "",
            "score": round(float(score), 3),
            "reason": "descubrimiento similar",
            "play_count": 0,
            "added_at": "",
            "external_url": "",
            "external_id": track.get("id") or "",
            "catalog_source": "spotify",
            "can_import": False,
        }

    def _spotify_fetch_recommendations(
        self,
        seed_track_ids: list[str],
        seed_artist_ids: list[str],
        limit: int,
    ) -> list[dict]:
        tracks = []
        track_ids = list(dict.fromkeys(seed_track_ids))
        artist_ids = list(dict.fromkeys(seed_artist_ids))
        if not track_ids and not artist_ids:
            return []

        def build_params(use_market: bool) -> dict:
            params = {"limit": max(1, min(int(limit), 30))}
            if use_market:
                params["market"] = self._spotify_market()
            if track_ids:
                params["seed_tracks"] = ",".join(track_ids[:5])
            if artist_ids:
                remaining = max(0, 5 - len(track_ids[:5]))
                if remaining > 0:
                    params["seed_artists"] = ",".join(artist_ids[:remaining])
            return params

        for use_market in (True, False):
            params = build_params(use_market)
            data = self._spotify_api_get("https://api.spotify.com/v1/recommendations", params)
            tracks = data.get("tracks", []) if data else []
            if tracks:
                break

        if self._recs_debug_enabled():
            print("[recs] spotify response tracks:", len(tracks))
        return tracks

    def _spotify_recommendations(
        self,
        engine: RecommendationEngine,
        playlist_id: str,
        limit: int,
        refresh_key=None,
    ) -> list[dict] | None:
        # If there is no spotify token available, return an empty list so the
        # caller can fall back to the local recommendation engine instead of
        # propagating None which may cause callers to return None.
        if not self._get_spotify_token():
            return []

        rng = self._recommendation_rng(refresh_key)
        seed_songs = self._mixed_seed_songs(engine, playlist_id, limit=max(8, min(limit * 3, 14)))
        seed_songs = [song for song in seed_songs if song is not None]
        rng.shuffle(seed_songs)
        if not seed_songs:
            return []

        existing_titles, existing_pairs = self._existing_song_identities(engine.songs)
        seed_artist_names = []
        for song in seed_songs:
            for artist in self._artist_candidates_from_song(song):
                if artist and artist not in seed_artist_names:
                    seed_artist_names.append(artist)
                if len(seed_artist_names) >= 6:
                    break
            if len(seed_artist_names) >= 6:
                break

        spotify_tracks: list[dict] = []
        seen_track_ids: set[str] = set()
        market = self._spotify_market()
        rng.shuffle(seed_artist_names)
        for artist_name in seed_artist_names:
            data = self._spotify_cached_get(
                "https://api.spotify.com/v1/search",
                {
                    "q": f"artist:{artist_name}",
                    "type": "track",
                    "limit": max(8, min(limit * 4, 20)),
                    "market": market,
                },
                log_errors=False,
            )
            items = list(data.get("tracks", {}).get("items", []) if data else [])
            rng.shuffle(items)
            for item in items:
                self._append_spotify_track(
                    spotify_tracks,
                    item,
                    seen_track_ids,
                    existing_titles,
                    existing_pairs,
                )
                if len(spotify_tracks) >= limit * 2:
                    break
            if len(spotify_tracks) >= limit * 2:
                break

        if len(spotify_tracks) < limit:
            artist_ids = []
            for artist_name in seed_artist_names[:3]:
                artist_data = self._spotify_cached_get(
                    "https://api.spotify.com/v1/search",
                    {"q": f"artist:{artist_name}", "type": "artist", "limit": 1, "market": market},
                    log_errors=False,
                )
                items = artist_data.get("artists", {}).get("items", []) if artist_data else []
                if items and items[0].get("id"):
                    artist_ids.append(items[0]["id"])
            rng.shuffle(artist_ids)

            related_ids: list[str] = []
            for artist_id in artist_ids:
                data = self._spotify_cached_get(
                    f"https://api.spotify.com/v1/artists/{artist_id}/related-artists",
                    {},
                    log_errors=False,
                )
                items = list(data.get("artists", []) if data else [])
                rng.shuffle(items)
                for item in items:
                    related_id = item.get("id")
                    if related_id and related_id not in related_ids:
                        related_ids.append(related_id)
                    if len(related_ids) >= limit:
                        break
                if len(related_ids) >= limit:
                    break

            for artist_id in related_ids:
                data = self._spotify_cached_get(
                    f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks",
                    {"market": market},
                    log_errors=False,
                )
                items = list(data.get("tracks", []) if data else [])
                rng.shuffle(items)
                for item in items:
                    self._append_spotify_track(
                        spotify_tracks,
                        item,
                        seen_track_ids,
                        existing_titles,
                        existing_pairs,
                    )
                    break
                if len(spotify_tracks) >= limit * 2:
                    break

        spotify_tracks = self._dedupe_spotify_tracks(
            spotify_tracks,
            existing_titles=existing_titles,
            existing_pairs=existing_pairs,
            limit=max(limit * 4, 12),
            max_per_artist=1,
        )
        rng.shuffle(spotify_tracks)

        results: list[dict] = []
        result_titles: set[str] = set()
        result_pairs: set[tuple[str, str]] = set()
        result_artists: set[str] = set()
        for index, raw_track in enumerate(spotify_tracks, start=1):
            track = raw_track
            if self._spotify_track_exists_locally(track, existing_titles, existing_pairs):
                continue

            title_key, artist_key, _ = self._spotify_track_identity(track)
            if title_key in result_titles or (title_key, artist_key) in result_pairs:
                continue
            if artist_key in result_artists:
                continue

            result_titles.add(title_key)
            result_pairs.add((title_key, artist_key))
            if artist_key:
                result_artists.add(artist_key)

            results.append(self._spotify_track_to_recommendation(track, index, limit))
            if len(results) >= limit:
                break
        return results

    def _spotify_related_artist_tracks(self, seed_artist_ids: list[str], limit: int) -> list[dict]:
        market = self._spotify_market()
        artist_ids = list(dict.fromkeys(seed_artist_ids))[:8]
        related_ids: list[str] = []
        for artist_id in artist_ids:
            data = self._spotify_api_get(
                f"https://api.spotify.com/v1/artists/{artist_id}/related-artists",
                {},
                log_errors=False,
            )
            items = data.get("artists", []) if data else []
            for item in items:
                rid = item.get("id")
                if rid and rid not in related_ids:
                    related_ids.append(rid)
                if len(related_ids) >= max(10, limit * 2):
                    break
            if len(related_ids) >= max(10, limit * 2):
                break

        tracks: list[dict] = []
        for artist_id in related_ids:
            data = self._spotify_api_get(
                f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks",
                {"market": market},
                log_errors=False,
            )
            items = data.get("tracks", []) if data else []
            added_for_artist = 0
            for item in items:
                tracks.append(item)
                added_for_artist += 1
                if len(tracks) >= limit:
                    return tracks
                if added_for_artist >= 2:
                    break
        return tracks

    def _spotify_get_audio_features(self, track_ids: list[str]) -> dict[str, dict]:
        if not track_ids:
            return {}
        features: dict[str, dict] = {}
        ids = list(dict.fromkeys(track_ids))
        for i in range(0, len(ids), 100):
            chunk = ids[i:i + 100]
            data = self._spotify_api_get(
                "https://api.spotify.com/v1/audio-features",
                {"ids": ",".join(chunk)},
            )
            items = data.get("audio_features", []) if data else []
            for item in items:
                if item and item.get("id"):
                    features[item["id"]] = item
        return features

    def _spotify_audio_vector(self, feat: dict) -> list[float]:
        return [
            float(feat.get("danceability") or 0.0),
            float(feat.get("energy") or 0.0),
            float(feat.get("valence") or 0.0),
            float(feat.get("acousticness") or 0.0),
            float(feat.get("instrumentalness") or 0.0),
            float(feat.get("liveness") or 0.0),
            float(feat.get("speechiness") or 0.0),
            float(feat.get("tempo") or 0.0) / 200.0,
        ]

    def _spotify_similarity_tracks(self, seed_songs: list, limit: int) -> list[dict]:
        if not self._spotify_has_valid_user_token():
            return []

        seed_keys: set[tuple[str, str]] = set()
        for song in seed_songs:
            title = self._sanitize_title(song.title)
            artist = (song.artist or "").strip()
            if title:
                seed_keys.add((title.casefold(), artist.casefold()))

        seed_track_ids, seed_artist_ids, seed_artist_names = self._spotify_seed_data(seed_songs)

        seed_features = self._spotify_get_audio_features(seed_track_ids)
        if self._recs_debug_enabled():
            print("[recs] seed audio features:", len(seed_features))

        # If audio-features are unavailable, try Spotify recommendations directly
        # with the seed ids gathered from title/artist searches.
        seed_vectors = [self._spotify_audio_vector(feat) for feat in seed_features.values() if feat]

        if not seed_vectors:
            try:
                recs = self._spotify_fetch_recommendations(seed_track_ids, seed_artist_ids, limit)
                if recs:
                    if self._recs_debug_enabled():
                        print("[recs] spotify recommendations fallback count:", len(recs))
                    return recs[:limit]
            except Exception:
                pass

        candidate_tracks = self._spotify_related_artist_tracks(seed_artist_ids, limit=limit * 2)
        if not candidate_tracks:
            for artist_name in seed_artist_names:
                candidate_tracks.extend(self._spotify_artist_tracks_by_name(artist_name, limit * 2 - len(candidate_tracks)))
                if len(candidate_tracks) >= limit * 2:
                    break
        if not candidate_tracks:
            candidate_tracks = self._spotify_tracks_from_seed_names(seed_songs, limit)

        if not candidate_tracks:
            return []

        candidate_ids = [track.get("id") for track in candidate_tracks if track.get("id")]
        candidate_features = self._spotify_get_audio_features(candidate_ids)

        seed_vectors = [self._spotify_audio_vector(feat) for feat in seed_features.values() if feat]
        if not seed_vectors:
            return candidate_tracks[:limit]

        seed_avg = [sum(vals) / len(vals) for vals in zip(*seed_vectors, strict=False)]

        scored: list[tuple[float, dict]] = []
        for track in candidate_tracks:
            track_id = track.get("id")
            if not track_id or track_id not in candidate_features:
                continue
            title = (track.get("name") or "").strip()
            artist = ", ".join(a.get("name", "") for a in track.get("artists", []) if a.get("name"))
            key = (title.casefold(), artist.casefold())
            if key in seed_keys:
                continue
            feat_vec = self._spotify_audio_vector(candidate_features[track_id])
            distance = sum((a - b) ** 2 for a, b in zip(seed_avg, feat_vec, strict=False)) ** 0.5
            score = 1.0 / (1.0 + distance)
            scored.append((score, track))

        scored.sort(key=lambda item: item[0], reverse=True)
        if self._recs_debug_enabled():
            print("[recs] similarity candidates:", len(scored))
        return [track for _, track in scored[:limit]]

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

    def get_recommendations(self, playlist_id: str = "all", limit: int = 8, refresh_key=None) -> list:
        try:
            engine = self._get_recommendation_engine()
            if not self._recs_spotify_enabled():
                return self._local_recommendations(engine, playlist_id, limit, refresh_key=refresh_key)

            spotify_items = self._spotify_recommendations(engine, playlist_id, limit, refresh_key=refresh_key)
            # If Spotify returned a non-empty list, prefer those. If it returned
            # None (meaning Spotify not available) or an empty list, fall back
            # to the local recommendation engine.
            if spotify_items:
                if len(spotify_items) < limit:
                    spotify_items = self._fill_local_recommendations(engine, spotify_items, limit, refresh_key=refresh_key)
                return spotify_items
            return self._local_recommendations(engine, playlist_id, limit, refresh_key=refresh_key)
        except Exception:
            return []

    def recompute_all_embeddings(self, force: bool = False) -> dict:
        """
        Recompute and persist embeddings for all songs in the local database.
        If `force` is False, only missing embeddings are computed. Returns a
        dict with counts: {updated: int, skipped: int, total: int}.
        """
        try:
            engine = self._get_recommendation_engine()
            source = engine.source
            songs = engine.songs
            total = len(songs)
            if total == 0:
                return {"ok": True, "updated": 0, "skipped": 0, "total": 0}

            # existing embeddings map
            existing = {}
            try:
                if hasattr(source, "get_embeddings"):
                    existing = source.get_embeddings([song.id for song in songs]) or {}
            except Exception:
                existing = {}

            texts = [song.as_text() for song in songs]
            engine.embedding_service.fit(texts)
            embeddings = engine.embedding_service.encode(texts)

            updated = 0
            skipped = 0
            for song, vec in zip(songs, embeddings, strict=False):
                has = existing.get(song.id)
                if has and not force:
                    skipped += 1
                    continue
                try:
                    if hasattr(source, "set_embedding"):
                        source.set_embedding(song.id, vec.astype(float).tolist())
                        updated += 1
                except Exception:
                    continue

            # Refresh the in-memory engine so subsequent calls use new vectors
            try:
                self._recommendation_engine = None
                _ = self._get_recommendation_engine()
            except Exception:
                pass

            return {"ok": True, "updated": updated, "skipped": skipped, "total": total}
        except Exception as e:
            return {"ok": False, "error": str(e)}
