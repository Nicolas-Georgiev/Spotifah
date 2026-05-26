"""Embeddings utilities for recommender, integrated under src/model."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
import hashlib
import re

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
except Exception:
    TfidfVectorizer = None


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    value = re.sub(r"\s+", " ", value).strip()
    return value


def _tokenize(value: str) -> list[str]:
    return re.findall(r"[a-z0-9áéíóúüñ]+", value.casefold())


def _hash_token(token: str, dimension: int) -> int:
    digest = hashlib.blake2b(token.encode("utf-8"), digest_size=4).digest()
    return int.from_bytes(digest, "big") % dimension


def build_song_text(song) -> str:
    return normalize_text(song.as_text())


def build_artist_text(artist, songs: Sequence | None = None) -> str:
    try:
        text = artist.profile_text(songs)
    except Exception:
        parts = [artist.name, " ".join(getattr(artist, "genres", []))]
        if songs:
            parts.extend(getattr(song, "title", "") for song in list(songs)[:5])
        text = " ".join(part for part in parts if part)
    return normalize_text(text)


@dataclass
class EmbeddingService:
    model_name: str = "all-MiniLM-L6-v2"
    max_features: int = 2048

    def __post_init__(self) -> None:
        self._model = None
        self._vectorizer = None
        self._backend = "sentence-transformers" if SentenceTransformer is not None else "sklearn"
        self._manual_dimension = 384

    @property
    def backend(self) -> str:
        return self._backend

    def fit(self, texts: Sequence[str]) -> None:
        cleaned = [normalize_text(text) for text in texts if normalize_text(text)]
        if self._backend == "sentence-transformers":
            try:
                self._model = SentenceTransformer(self.model_name)
                return
            except Exception:
                self._backend = "sklearn"

        if self._backend == "sklearn" and TfidfVectorizer is None:
            self._backend = "manual-hash"

        if self._backend == "manual-hash":
            return

        if not cleaned:
            cleaned = ["sample music"]

        self._vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=self.max_features)
        self._vectorizer.fit(cleaned)

    def encode(self, texts: Sequence[str] | str) -> np.ndarray:
        if isinstance(texts, str):
            texts = [texts]

        cleaned = [normalize_text(text) for text in texts]
        if not any(cleaned):
            cleaned = ["sample music"]

        if self._backend == "sentence-transformers":
            if self._model is None:
                self.fit(cleaned)
            if self._model is not None:
                vectors = self._model.encode(cleaned, normalize_embeddings=True, convert_to_numpy=True)
                return np.asarray(vectors, dtype=np.float32)
            self._backend = "sklearn"

        if self._backend == "sklearn" and TfidfVectorizer is None:
            self._backend = "manual-hash"

        if self._vectorizer is None:
            if self._backend == "sklearn":
                self.fit(cleaned)

        if self._backend == "sklearn" and self._vectorizer is not None:
            matrix = self._vectorizer.transform(cleaned)
            dense = matrix.toarray().astype(np.float32, copy=False)
            norms = np.linalg.norm(dense, axis=1, keepdims=True)
            norms[norms == 0.0] = 1.0
            return dense / norms

        return self._manual_encode(cleaned)

    def encode_one(self, text: str) -> np.ndarray:
        return self.encode([text])[0]

    def _manual_encode(self, texts: Sequence[str]) -> np.ndarray:
        vectors = np.zeros((len(texts), self._manual_dimension), dtype=np.float32)
        for row_index, text in enumerate(texts):
            tokens = _tokenize(text)
            if not tokens:
                tokens = ["music"]

            for token in tokens:
                vectors[row_index, _hash_token(token, self._manual_dimension)] += 1.0

            for left, right in zip(tokens, tokens[1:], strict=False):
                vectors[row_index, _hash_token(f"{left}_{right}", self._manual_dimension)] += 0.5

        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0.0] = 1.0
        return vectors / norms
