# View for displaying music recommendations
class RecsView:
	def __init__(self, controller):
		self.controller = controller

	def show_recommendations(self, user_preferences=None, top_n=10):
		recommendations = self.controller.get_recommendations(user_preferences, top_n)
		if not recommendations:
			print("No recommendations available.")
			return
		print("Recommended Tracks:")
		for idx, track in enumerate(recommendations, 1):
			title = track.get('title', 'Unknown Title')
			artist = track.get('artist', 'Unknown Artist')
			genre = track.get('genre', 'Unknown Genre')
			print(f"{idx}. {title} - {artist} [{genre}]")

	def add_track_to_history(self, track_id):
		self.controller.add_track_to_history(track_id)
