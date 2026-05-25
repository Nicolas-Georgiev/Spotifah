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
    def _sanitize_title(self, title: str) -> str:
        if not title:
            return ""
        cleaned = re.sub(r"\s+", " ", title).strip()
        cleaned = re.sub(r"\s*[\(\[].*?[\)\]]\s*", " ", cleaned).strip()
        for sep in (" | ", " - ", " — "):
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

    def _spotify_api_get(self, url: str, params: dict, *, log_errors: bool = True) -> dict:
        """
        Perform a Spotify GET request. On 401 try to refresh the user token once.
        On 403 try client-credentials token as a fallback. Always return a dict
        (empty on failure) so callers don't receive None.
        """
        token = self._get_spotify_token()
        # Determine whether we have a valid user token in settings (for logging)
        has_user_token = False
        try:
            settings = self._load_settings() if hasattr(self, "_load_settings") else {}
            has_user_token = bool(
                isinstance(settings, dict)
                and settings.get("spotify_access_token")
                and settings.get("spotify_token_expires_at")
                and time.time() < float(settings.get("spotify_token_expires_at") or 0) - 60
            )
        except Exception:
            has_user_token = False

        token_type = "user" if has_user_token else "client-credentials"
        if not token:
            return {}

        def _do_request(tok: str):
            return requests.get(url, params=params, headers={"Authorization": f"Bearer {tok}"}, timeout=10)

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
                                r2 = requests.get(url, params=params, headers={"Authorization": f"Bearer {client_token}"}, timeout=10)
                                if r2.status_code == 200:
                                    return r2.json() or {}
                    except Exception:
                        pass
            except Exception:
                pass

            return {}

    def _spotify_market(self) -> str:
        return os.getenv("SPOTIFY_MARKET", "US")

    def _spotify_available_genres(self) -> list[str]:
        # Spotify's genre-seeds endpoint has been flaky/restricted in this app's flow.
        # Keep this as a no-op so recommendations do not depend on it.
        return []

    def _spotify_search_track_id(self, title: str, artist: str) -> str | None:
        if not title:
            return None
        query = f"track:{title} artist:{artist}" if artist else f"track:{title}"
        data = self._spotify_api_get(
            "https://api.spotify.com/v1/search",
            {"q": query, "type": "track", "limit": 1, "market": self._spotify_market()},
        )
        tracks = data.get("tracks", {}).get("items", []) if data else []
        if tracks:
            return tracks[0].get("id")
        if artist:
            data = self._spotify_api_get(
                "https://api.spotify.com/v1/search",
                {"q": f"track:{title}", "type": "track", "limit": 1, "market": self._spotify_market()},
            )
            tracks = data.get("tracks", {}).get("items", []) if data else []
            if tracks:
                return tracks[0].get("id")
        return None

    def _spotify_search_artist_id(self, artist: str) -> str | None:
        if not artist:
            return None
        data = self._spotify_api_get(
            "https://api.spotify.com/v1/search",
            {"q": f"artist:{artist}", "type": "artist", "limit": 1, "market": self._spotify_market()},
        )
        items = data.get("artists", {}).get("items", []) if data else []
        if items:
            return items[0].get("id")
        return None

    def _extract_seed_genres(self, songs: list) -> list[str]:
        available = set(self._spotify_available_genres())
        if not available:
            return []
        seeds: list[str] = []
        mapping = {
            "pop": "pop",
            "k pop": "k-pop",
            "k-pop": "k-pop",
            "korean": "k-pop",
            "hip hop": "hip-hop",
            "hip-hop": "hip-hop",
            "rap": "hip-hop",
            "r&b": "r-n-b",
            "rnb": "r-n-b",
            "rock": "rock",
            "indie": "indie",
            "latin": "latin",
            "reggaeton": "reggaeton",
            "electronic": "electronic",
            "edm": "edm",
            "dance": "dance",
        }
        for song in songs:
            raw = (song.genre or "").strip()
            if not raw:
                continue
            for token in re.split(r"[,/;|]", raw):
                candidate = token.strip().casefold()
                if not candidate:
                    continue
                mapped = mapping.get(candidate)
                if mapped and mapped in available and mapped not in seeds:
                    seeds.append(mapped)
                    if len(seeds) >= 5:
                        return seeds
                normalized = candidate.replace(" ", "-")
                if normalized in available and normalized not in seeds:
                    seeds.append(normalized)
                if len(seeds) >= 5:
                    return seeds
        return seeds

    def _extract_seed_artists_from_genres(self, songs: list) -> list[str]:
        seeds: list[str] = []
        for song in songs:
            raw = (song.genre or "").strip()
            if not raw:
                continue
            for token in re.split(r"[,/;|]", raw):
                candidate = token.strip()
                if not candidate or len(candidate) < 3:
                    continue
                lowered = candidate.casefold()
                if any(word in lowered for word in ("records", "tv", "awards", "music awards")):
                    continue
                if lowered in ("pop", "k-pop", "k pop", "hip hop", "hip-hop", "rap", "r&b", "rnb"):
                    continue
                artist_id = self._spotify_search_artist_id(candidate)
                if artist_id and artist_id not in seeds:
                    seeds.append(artist_id)
                if len(seeds) >= 5:
                    return seeds
        return seeds

    def _spotify_fetch_recommendations(
        self,
        seed_track_ids: list[str],
        seed_artist_ids: list[str],
        seed_genres: list[str],
        limit: int,
    ) -> list[dict]:
        tracks = []
        track_ids = list(dict.fromkeys(seed_track_ids))
        artist_ids = list(dict.fromkeys(seed_artist_ids))
        genres = list(dict.fromkeys(seed_genres))
        if not track_ids and not artist_ids and not genres:
            return []

        def build_params(use_market: bool, use_genres: list[str]) -> dict:
            params = {"limit": max(1, min(int(limit), 30))}
            if use_market:
                params["market"] = self._spotify_market()
            if track_ids:
                params["seed_tracks"] = ",".join(track_ids[:5])
            if artist_ids:
                remaining = max(0, 5 - len(track_ids[:5]))
                if remaining > 0:
                    params["seed_artists"] = ",".join(artist_ids[:remaining])
            if use_genres:
                remaining = 5 - len(track_ids[:5]) - len(artist_ids[:5])
                if remaining > 0:
                    params["seed_genres"] = ",".join(use_genres[:remaining])
            return params

        for use_market in (True, False):
            params = build_params(use_market, genres)
            data = self._spotify_api_get("https://api.spotify.com/v1/recommendations", params)
            tracks = data.get("tracks", []) if data else []
            if tracks:
                break

        if self._recs_debug_enabled():
            print("[recs] spotify response tracks:", len(tracks))
        return tracks

    def _spotify_recommendations(self, engine: RecommendationEngine, playlist_id: str, limit: int) -> list[dict] | None:
        # If there is no spotify token available, return an empty list so the
        # caller can fall back to the local recommendation engine instead of
        # propagating None which may cause callers to return None.
        if not self._get_spotify_token():
            return []

        if playlist_id == "all":
            if engine.history:
                seed_songs = [engine._song_by_id.get(event.song_id) for event in engine.history[-10:]]
            else:
                seed_songs = sorted(engine.songs, key=lambda song: song.play_count, reverse=True)[:10]
        else:
            seed_songs = self._playlist_seed_songs(playlist_id)

        seed_songs = [song for song in seed_songs if song is not None]
        if not seed_songs:
            return []

        existing = {
            (song.title.casefold().strip(), song.artist.casefold().strip())
            for song in engine.songs
        }

        seed_track_ids: list[str] = []
        seed_artist_ids: list[str] = []
        for song in seed_songs:
            title = self._sanitize_title(song.title)
            track_id = self._spotify_search_track_id(title, song.artist)
            if track_id:
                seed_track_ids.append(track_id)
            artist_id = self._spotify_search_artist_id(song.artist)
            if artist_id:
                seed_artist_ids.append(artist_id)
            if len(seed_track_ids) + len(seed_artist_ids) >= 5:
                break

        if len(seed_track_ids) + len(seed_artist_ids) < 5:
            seed_artist_ids.extend(
                [artist for artist in self._extract_seed_artists_from_genres(seed_songs) if artist not in seed_artist_ids]
            )

        if self._recs_debug_enabled():
            print("[recs] market:", self._spotify_market())
            print("[recs] seed tracks:", seed_track_ids)
            print("[recs] seed artists:", seed_artist_ids)

        has_user_token = False
        try:
            settings = self._load_settings() if hasattr(self, "_load_settings") else {}
            has_user_token = bool(
                isinstance(settings, dict)
                and settings.get("spotify_access_token")
                and settings.get("spotify_token_expires_at")
                and time.time() < float(settings.get("spotify_token_expires_at") or 0) - 60
            )
        except Exception:
            has_user_token = False

        if has_user_token:
            spotify_tracks = self._spotify_similarity_tracks(seed_songs, limit=limit * 2)
        else:
            spotify_tracks = self._spotify_related_artist_tracks(seed_artist_ids, limit * 2)
            if not spotify_tracks:
                spotify_tracks = []

        results: list[dict] = []
        for index, track in enumerate(spotify_tracks, start=1):
            title = track.get("name") or ""
            artists = track.get("artists", []) or []
            artist = ", ".join(a.get("name", "") for a in artists if a.get("name"))
            key = (title.casefold().strip(), artist.casefold().strip())
            if key in existing:
                continue
            album = track.get("album", {}) or {}
            images = album.get("images", []) or []
            cover_url = images[0].get("url") if images else ""
            duration = int((track.get("duration_ms") or 0) / 1000)
            external_url = track.get("external_urls", {}).get("spotify", "")
            score = 1.0 - min((index - 1) / max(limit, 1), 0.75)
            results.append({
                "id": track.get("id") or external_url or f"spotify:{index}",
                "title": title,
                "artist": artist,
                "album": album.get("name", ""),
                "duration": duration,
                "genre": "",
                "source": "spotify",
                "path": "",
                "cover_url": cover_url,
                "score": round(float(score), 3),
                "reason": "spotify similar",
                "play_count": 0,
                "added_at": "",
                "external_url": external_url,
                "external_id": track.get("id") or "",
            })
            if len(results) >= limit:
                break
        return results

    def _spotify_related_artist_tracks(self, seed_artist_ids: list[str], limit: int) -> list[dict]:
        market = self._spotify_market()
        artist_ids = list(dict.fromkeys(seed_artist_ids))[:3]
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
                if len(related_ids) >= 10:
                    break
            if len(related_ids) >= 10:
                break

        tracks: list[dict] = []
        for artist_id in related_ids:
            data = self._spotify_api_get(
                f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks",
                {"market": market},
                log_errors=False,
            )
            items = data.get("tracks", []) if data else []
            for item in items:
                tracks.append(item)
                if len(tracks) >= limit:
                    return tracks
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
            # If the request failed (e.g. 403) when using a user token, retry
            # using the client credentials token as a fallback.
            if data is None:
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
                            resp2 = requests.get(
                                "https://api.spotify.com/v1/audio-features",
                                params={"ids": ",".join(chunk)},
                                headers={"Authorization": f"Bearer {client_token}"},
                                timeout=10,
                            )
                            if resp2.status_code == 200:
                                data = resp2.json()
                except Exception:
                    data = None
            items = data.get("audio_features", []) if data else []
            for item in items:
                if item and item.get("id"):
                    features[item["id"]] = item
        return features

    def _spotify_similarity_tracks(self, seed_songs: list, limit: int) -> list[dict]:
        try:
            settings = self._load_settings() if hasattr(self, "_load_settings") else {}
            has_user_token = bool(
                isinstance(settings, dict)
                and settings.get("spotify_access_token")
                and settings.get("spotify_token_expires_at")
                and time.time() < float(settings.get("spotify_token_expires_at") or 0) - 60
            )
            if not has_user_token:
                return []
        except Exception:
            return []

        seed_track_ids: list[str] = []
        seed_keys: set[tuple[str, str]] = set()
        seed_artist_ids: list[str] = []
        for song in seed_songs:
            title = self._sanitize_title(song.title)
            artist = (song.artist or "").strip()
            if title:
                seed_keys.add((title.casefold(), artist.casefold()))
            track_id = self._spotify_search_track_id(title, artist)
            if track_id:
                seed_track_ids.append(track_id)
            elif artist:
                artist_id = self._spotify_search_artist_id(artist)
                if artist_id:
                    seed_artist_ids.append(artist_id)
            if len(seed_track_ids) >= 5:
                break

        seed_features = self._spotify_get_audio_features(seed_track_ids)
        if self._recs_debug_enabled():
            print("[recs] seed audio features:", len(seed_features))

        # If we failed to get audio-features for the seed tracks, try the
        # recommendations endpoint directly using seed ids / artists / genres
        # (search-by-name produces the seed ids earlier). This avoids relying
        # solely on audio-features availability.
        seed_genres = self._extract_seed_genres(seed_songs)
        if self._recs_debug_enabled():
            print("[recs] seed genres:", seed_genres)

        seed_vectors = [
            [
                float(feat.get("danceability") or 0.0),
                float(feat.get("energy") or 0.0),
                float(feat.get("valence") or 0.0),
                float(feat.get("acousticness") or 0.0),
                float(feat.get("instrumentalness") or 0.0),
                float(feat.get("liveness") or 0.0),
                float(feat.get("speechiness") or 0.0),
                float(feat.get("tempo") or 0.0) / 200.0,
            ]
            for feat in seed_features.values() if feat
        ]

        if not seed_vectors:
            try:
                recs = self._spotify_fetch_recommendations(seed_track_ids, seed_artist_ids, seed_genres, limit)
                if recs:
                    if self._recs_debug_enabled():
                        print("[recs] spotify recommendations fallback count:", len(recs))
                    return recs[:limit]
            except Exception:
                pass

        candidate_tracks = self._spotify_related_artist_tracks(seed_artist_ids, limit=limit * 2)

        if not candidate_tracks:
            return []

        candidate_ids = [track.get("id") for track in candidate_tracks if track.get("id")]
        candidate_features = self._spotify_get_audio_features(candidate_ids)

        def vector(feat: dict) -> list[float]:
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

        seed_vectors = [vector(feat) for feat in seed_features.values() if feat]
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
            feat_vec = vector(candidate_features[track_id])
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

    def get_recommendations(self, playlist_id: str = "all", limit: int = 8) -> list:
        try:
            engine = self._get_recommendation_engine()
            spotify_items = self._spotify_recommendations(engine, playlist_id, limit)
            # If Spotify returned a non-empty list, prefer those. If it returned
            # None (meaning Spotify not available) or an empty list, fall back
            # to the local recommendation engine.
            if spotify_items:
                return spotify_items
            if playlist_id == "all":
                recommendations = engine.generate_home_recommendations(top_k=limit)
            else:
                seed_songs = self._playlist_seed_songs(playlist_id)
                recommendations = engine.recommend_from_seed_songs(seed_songs, top_k=limit)
            return [self._serialize_recommendation(item) for item in recommendations]
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
