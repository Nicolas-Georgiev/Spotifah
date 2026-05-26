"""Recommendation engine controller integrated under src/controller."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
from math import exp, log1p
from random import Random
from typing import Iterable

import numpy as np

from model.recommender_models import RecommendationItem, Song
from model.recommender_embedding import EmbeddingService


def _ensure_utc(value: datetime) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _safe_normalize(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float32)
    norm = np.linalg.norm(values)
    if norm == 0.0:
        return values
    return values / norm


def _genre_overlap(left: list[str], right: list[str]) -> float:
    left_set = {genre.casefold().strip() for genre in left if genre}
    right_set = {genre.casefold().strip() for genre in right if genre}
    if not left_set or not right_set:
        return 0.0
    return len(left_set & right_set) / len(left_set | right_set)


class _VectorIndex:
    def __init__(self) -> None:
        self._ids: list[int] = []
        self._matrix: np.ndarray | None = None

    def build(self, ids: list[int], matrix: np.ndarray | None) -> None:
        if not ids or matrix is None:
            self._ids = []
            self._matrix = None
            return
        mat = np.asarray(matrix, dtype=np.float32)
        norms = np.linalg.norm(mat, axis=1, keepdims=True)
        norms[norms == 0.0] = 1.0
        self._matrix = mat / norms
        self._ids = list(ids)

    def search(self, query: Iterable[float], top_k: int = 10) -> list[tuple[int, float]]:
        if self._matrix is None or not self._ids or top_k <= 0:
            return []
        q = np.asarray(list(query), dtype=np.float32)
        q_norm = np.linalg.norm(q)
        if q_norm == 0.0:
            return []
        q = q / q_norm
        scores = np.dot(self._matrix, q)
        top_k = min(top_k, len(self._ids))
        idx = np.argpartition(-scores, top_k - 1)[:top_k]
        idx = idx[np.argsort(-scores[idx])]
        return [(self._ids[i], float(scores[i])) for i in idx]


class RecommendationEngine:
    """Orquesta el flujo completo de recomendacion musical."""

    def __init__(self, source, embedding_service: EmbeddingService | None = None) -> None:
        self.source = source
        self.embedding_service = embedding_service or EmbeddingService()
        self.song_index = _VectorIndex()
        self.artist_index = _VectorIndex()
        self.refresh()

    def refresh(self) -> None:
        self.songs = self.source.get_songs()
        self.artists = self.source.get_artists()
        self.history = sorted(self.source.get_listening_history(), key=lambda event: _ensure_utc(event.listened_at))

        song_texts = [song.as_text() for song in self.songs]
        self.embedding_service.fit(song_texts)

        existing_map: dict[int, list[float]] = {}
        try:
            if hasattr(self.source, "get_embeddings"):
                existing_map = self.source.get_embeddings([song.id for song in self.songs]) or {}
        except Exception:
            existing_map = {}

        missing_songs: list[Song] = []
        missing_texts: list[str] = []

        self._song_by_id = {}
        for song in self.songs:
            vec = existing_map.get(song.id)
            if vec:
                song.embedding = np.asarray(vec, dtype=np.float32).tolist()
            else:
                missing_songs.append(song)
                missing_texts.append(song.as_text())
            self._song_by_id[song.id] = song

        if missing_songs:
            missing_embeddings = self.embedding_service.encode(missing_texts)
            for song, embedding in zip(missing_songs, missing_embeddings, strict=False):
                song.embedding = embedding.astype(float).tolist()
                try:
                    if hasattr(self.source, "set_embedding"):
                        self.source.set_embedding(song.id, song.embedding)
                except Exception:
                    pass

        if self.songs:
            song_vectors = np.asarray([song.embedding for song in self.songs], dtype=np.float32)
            self.song_index.build([song.id for song in self.songs], song_vectors)
        else:
            self.song_index.build([], None)

        self._build_artist_embeddings()

    def _build_artist_embeddings(self) -> None:
        songs_by_artist: dict[str, list[Song]] = defaultdict(list)
        for song in self.songs:
            songs_by_artist[song.artist.casefold()].append(song)

        artist_vectors: list[np.ndarray] = []
        artist_ids: list[int] = []
        self._artist_by_name = {}

        for artist in self.artists:
            artist_songs = songs_by_artist.get(artist.name.casefold(), [])
            profile_text = artist.profile_text(artist_songs)
            profile_vector = self.embedding_service.encode_one(profile_text)
            if artist_songs:
                matrix = np.asarray([song.embedding for song in artist_songs], dtype=np.float32)
                song_vector = matrix.mean(axis=0)
                vector = _safe_normalize(0.65 * song_vector + 0.35 * profile_vector)
            else:
                vector = profile_vector
            vector = _safe_normalize(vector)
            artist.embedding = vector.astype(float).tolist()
            artist_vectors.append(vector)
            artist_ids.append(artist.id)
            self._artist_by_name[artist.name.casefold()] = artist

        if artist_vectors:
            self.artist_index.build(artist_ids, np.asarray(artist_vectors, dtype=np.float32))


    def search_similar(self, embedding: Iterable[float], top_k: int = 10) -> list[tuple[Song, float]]:
        query = np.asarray(list(embedding), dtype=np.float32)
        matches = self.song_index.search(query, top_k=top_k)
        return [(self._song_by_id[song_id], score) for song_id, score in matches if song_id in self._song_by_id]

    def get_similar_songs(self, song_id: int, top_k: int = 10) -> list[RecommendationItem]:
        song = self._song_by_id.get(song_id)
        if song is None:
            return []

        matches = self.search_similar(song.embedding, top_k=top_k + 1)
        return self._rank_candidates(matches, excluded_ids={song.id}, reason="similitud musical")

    def get_similar_artists(self, artist_name: str, top_k: int = 10) -> list[RecommendationItem]:
        artist = self._artist_by_name.get(artist_name.casefold())
        if artist is None:
            return []

        query = np.asarray(artist.embedding, dtype=np.float32)
        matches = self.artist_index.search(query, top_k=max(top_k + 5, len(self.artists)))
        results: list[RecommendationItem] = []
        for matched_artist_id, score in matches:
            matched_artist = next((item for item in self.artists if item.id == matched_artist_id), None)
            if matched_artist is None or matched_artist.id == artist.id:
                continue

            embedding_similarity = max(float(score), 0.0)
            genre_similarity = _genre_overlap(artist.genres, matched_artist.genres)
            popularity_similarity = 1.0 - min(abs(artist.popularity - matched_artist.popularity) / 100.0, 1.0)
            blended_similarity = (
                0.60 * embedding_similarity
                + 0.30 * genre_similarity
                + 0.10 * popularity_similarity
            )

            if blended_similarity < 0.12:
                continue

            results.append(
                RecommendationItem(
                    song_id=matched_artist.id,
                    title=matched_artist.name,
                    artist=matched_artist.name,
                    score=blended_similarity,
                    reason="artista similar",
                    source="local",
                    metadata={
                        "genres": matched_artist.genres,
                        "popularity": matched_artist.popularity,
                        "embedding_similarity": embedding_similarity,
                        "genre_similarity": genre_similarity,
                    },
                )
            )
            if len(results) >= top_k:
                break

        if results:
            results.sort(key=lambda item: item.score, reverse=True)
        return results

    def recommend_from_history(self, top_k: int = 10) -> list[RecommendationItem]:
        if not self.history:
            return self._rank_by_popularity(top_k=top_k, reason="popularidad y exploracion")

        query_vector = self._build_history_profile()
        matches = self.search_similar(query_vector, top_k=max(top_k * 3, 10))

        listened_ids = {event.song_id for event in self.history}
        return self._rank_candidates(matches, excluded_ids=listened_ids, reason="basado en historial")[:top_k]

    def generate_home_recommendations(
        self,
        trend_tracks: Iterable[Song] | None = None,
        top_k: int = 10,
    ) -> list[RecommendationItem]:
        history_items = self.recommend_from_history(top_k=max(top_k * 2, 10))
        similarity_items = []
        if self.history:
            seed_song = self._song_by_id[self.history[-1].song_id]
            similarity_items = self.get_similar_songs(seed_song.id, top_k=max(top_k * 2, 10))

        trend_items: list[RecommendationItem] = []
        if trend_tracks:
            trend_items = self._rank_external_tracks(trend_tracks)

        return self._blend_recommendation_sources(history_items, similarity_items, trend_items, top_k=top_k)

    def recommend_from_seed_songs(self, seed_songs: Iterable[Song], top_k: int = 10) -> list[RecommendationItem]:
        seeds = [song for song in seed_songs if song.id in self._song_by_id]
        if not seeds:
            return self.generate_home_recommendations(top_k=top_k)

        matrix = np.asarray([song.embedding for song in seeds], dtype=np.float32)
        query = _safe_normalize(matrix.mean(axis=0))
        matches = self.search_similar(query, top_k=max(top_k * 3, 15))
        excluded_ids = {song.id for song in seeds}
        ranked = self._rank_candidates(matches, excluded_ids=excluded_ids, reason="basado en tu playlist")

        if len(ranked) >= top_k:
            return ranked[:top_k]

        fallback = self.recommend_from_history(top_k=max(top_k * 2, 10))
        blended = self._blend_recommendation_sources(fallback, ranked, [], top_k=top_k)
        if blended:
            return blended[:top_k]
        return ranked[:top_k]

    def _build_history_profile(self) -> np.ndarray:
        now = datetime.now(timezone.utc)
        accumulator = None
        total_weight = 0.0

        for index, event in enumerate(reversed(self.history[-50:]), start=1):
            song = self._song_by_id.get(event.song_id)
            if song is None:
                continue

            listened_at = _ensure_utc(event.listened_at)
            age_days = max((now - listened_at).total_seconds() / 86400.0, 0.0)
            recency_weight = exp(-age_days / 30.0)
            play_weight = 1.0 + log1p(max(song.play_count, 0)) / 5.0
            order_weight = 1.0 / (1.0 + index / 5.0)
            weight = recency_weight * play_weight * order_weight

            vector = np.asarray(song.embedding, dtype=np.float32)
            accumulator = vector * weight if accumulator is None else accumulator + vector * weight
            total_weight += weight

        if accumulator is None or total_weight == 0.0:
            return np.asarray(self.songs[0].embedding, dtype=np.float32)

        return _safe_normalize(accumulator / total_weight)

    def _score_song(self, song: Song, similarity: float) -> float:
        popularity_score = self._normalise_play_count(song.play_count)
        recency_score = self._recency_score(song)
        randomness_score = Random(song.id).random()
        return (
            0.45 * float(similarity)
            + 0.25 * popularity_score
            + 0.20 * recency_score
            + 0.10 * randomness_score
        )

    def _normalise_play_count(self, play_count: int) -> float:
        max_play_count = max((song.play_count for song in self.songs), default=1)
        if max_play_count <= 0:
            return 0.0
        return min(log1p(max(play_count, 0)) / log1p(max_play_count), 1.0)

    def _recency_score(self, song: Song) -> float:
        now = datetime.now(timezone.utc)
        added_at = _ensure_utc(song.added_at)
        age_days = max((now - added_at).total_seconds() / 86400.0, 0.0)
        return float(exp(-age_days / 45.0))

    def _rank_candidates(
        self,
        matches: list[tuple[Song, float]],
        excluded_ids: set[int] | None = None,
        reason: str = "recomendacion",
    ) -> list[RecommendationItem]:
        excluded_ids = excluded_ids or set()
        results: list[RecommendationItem] = []
        for song, similarity in matches:
            if song.id in excluded_ids:
                continue
            score = self._score_song(song, similarity)
            results.append(
                RecommendationItem(
                    song_id=song.id,
                    title=song.title,
                    artist=song.artist,
                    score=score,
                    reason=reason,
                    source=song.source,
                    metadata=asdict(song),
                )
            )

        results.sort(key=lambda item: item.score, reverse=True)
        return results

    def _rank_by_popularity(self, top_k: int, reason: str) -> list[RecommendationItem]:
        matches = sorted(self.songs, key=lambda song: (song.play_count, self._recency_score(song)), reverse=True)
        result: list[RecommendationItem] = []
        for song in matches[:top_k]:
            result.append(
                RecommendationItem(
                    song_id=song.id,
                    title=song.title,
                    artist=song.artist,
                    score=self._score_song(song, self._normalise_play_count(song.play_count)),
                    reason=reason,
                    source=song.source,
                    metadata=asdict(song),
                )
            )
        return result

    def _rank_external_tracks(self, tracks: Iterable[Song]) -> list[RecommendationItem]:
        results: list[RecommendationItem] = []
        for position, track in enumerate(tracks, start=1):
            if isinstance(track, Song):
                song = track
            else:
                continue

            score = 1.0 - min((position - 1) / 20.0, 0.75)
            results.append(
                RecommendationItem(
                    song_id=song.id,
                    title=song.title,
                    artist=song.artist,
                    score=score,
                    reason="tendencia externa",
                    source=song.source,
                    metadata=asdict(song),
                )
            )
        return results

    def _blend_recommendation_sources(
        self,
        history_items: list[RecommendationItem],
        similarity_items: list[RecommendationItem],
        trend_items: list[RecommendationItem],
        top_k: int,
    ) -> list[RecommendationItem]:
        scores: dict[tuple[str, str], RecommendationItem] = {}

        def add_items(items: list[RecommendationItem], weight: float) -> None:
            if not items:
                return
            max_score = max(item.score for item in items) or 1.0
            for item in items:
                key = (item.title.casefold(), item.artist.casefold())
                merged = scores.get(key)
                normalized = item.score / max_score
                blended_score = normalized * weight
                if merged is None:
                    scores[key] = RecommendationItem(
                        song_id=item.song_id,
                        title=item.title,
                        artist=item.artist,
                        score=blended_score,
                        reason=item.reason,
                        source=item.source,
                        metadata=dict(item.metadata),
                    )
                else:
                    merged.score += blended_score
                    merged.metadata.setdefault("sources", []).append(item.reason)

        add_items(history_items, 0.40)
        add_items(similarity_items, 0.40)
        add_items(trend_items, 0.20)

        blended = list(scores.values())
        blended.sort(key=lambda item: item.score, reverse=True)
        return blended[:top_k]
