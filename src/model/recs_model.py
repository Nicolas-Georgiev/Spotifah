# Hybrid Music Recommendation System
import json
import os
from typing import List, Dict, Optional

class MusicRecommender:
	def __init__(self, metadata_path: str, user_history_path: Optional[str] = None):
		self.metadata_path = metadata_path
		self.user_history_path = user_history_path
		self.tracks = self._load_metadata()
		self.user_history = self._load_user_history() if user_history_path else []

	def _load_metadata(self) -> List[Dict]:
		if not os.path.exists(self.metadata_path):
			return []
		with open(self.metadata_path, 'r', encoding='utf-8') as f:
			data = json.load(f)
		return data.get('tracks', [])

	def _load_user_history(self) -> List[str]:
		if not self.user_history_path or not os.path.exists(self.user_history_path):
			return []
		with open(self.user_history_path, 'r', encoding='utf-8') as f:
			return json.load(f).get('history', [])

	def recommend(self, user_preferences: Optional[Dict] = None, top_n: int = 10) -> List[Dict]:
		"""
		Recommend tracks based on metadata, user preferences, and history.
		user_preferences: dict with keys like 'genres', 'artists', etc.
		"""
		if not self.tracks:
			return []

		# Score each track
		scored_tracks = []
		for track in self.tracks:
			score = 0
			# Content-based: match genres, artists, etc.
			if user_preferences:
				if 'genres' in user_preferences and 'genre' in track:
					if track['genre'] in user_preferences['genres']:
						score += 2
				if 'artists' in user_preferences and 'artist' in track:
					if track['artist'] in user_preferences['artists']:
						score += 2
			# Collaborative: boost if in user history
			if self.user_history and track.get('id') in self.user_history:
				score += 3
			scored_tracks.append((score, track))

		# Sort by score descending, then by title
		scored_tracks.sort(key=lambda x: (-x[0], x[1].get('title', '')))
		return [track for score, track in scored_tracks[:top_n]]

	def add_to_history(self, track_id: str):
		if not self.user_history_path:
			return
		if track_id not in self.user_history:
			self.user_history.append(track_id)
			with open(self.user_history_path, 'w', encoding='utf-8') as f:
				json.dump({'history': self.user_history}, f, ensure_ascii=False, indent=2)
