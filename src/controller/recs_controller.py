# Controller for the Music Recommendation System
import os
from src.model.recs_model import MusicRecommender

class RecsController:
	def __init__(self, metadata_path, user_history_path=None):
		self.recommender = MusicRecommender(metadata_path, user_history_path)

	def get_recommendations(self, user_preferences=None, top_n=10):
		"""
		Returns a list of recommended tracks based on user preferences and history.
		"""
		return self.recommender.recommend(user_preferences, top_n)

	def add_track_to_history(self, track_id):
		self.recommender.add_to_history(track_id)
