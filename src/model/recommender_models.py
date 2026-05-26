"""Modelo para el motor de recomendaciones"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Sequence


@dataclass(slots=True)
class Song:
    id: int
    title: str
    artist: str
    album: str | None = None
    genre: str | None = None
    duration: int | None = None
    source: str = "local"
    added_at: datetime = field(default_factory=datetime.utcnow)
    play_count: int = 0
    embedding: list[float] = field(default_factory=list)
    path: str = ""
    cover_url: str = ""

    def as_text(self) -> str:
        parts = [self.title, self.artist, self.genre or "", self.album or ""]
        return " ".join(part for part in parts if part).strip()


@dataclass(slots=True)
class Artist:
    id: int
    name: str
    genres: list[str] = field(default_factory=list)
    popularity: float = 0.0
    embedding: list[float] = field(default_factory=list)

    def as_text(self) -> str:
        parts = [self.name, " ".join(self.genres)]
        return " ".join(part for part in parts if part).strip()

    def profile_text(self, songs: Sequence["Song"] | None = None) -> str:
        parts = [self.name, " ".join(self.genres)]
        if songs:
            parts.extend(song.title for song in songs[:5])
        return " ".join(part for part in parts if part).strip()


@dataclass(slots=True)
class ListeningEvent:
    id: int
    song_id: int
    listened_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(slots=True)
class RecommendationItem:
    song_id: int
    title: str
    artist: str
    score: float
    reason: str = ""
    source: str = "local"
    metadata: dict[str, Any] = field(default_factory=dict)
