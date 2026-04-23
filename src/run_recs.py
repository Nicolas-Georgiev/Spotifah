# Script to run the music recommender system
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controller.recs_controller import RecsController
from view.recs_view import RecsView

def main():
	metadata_path = os.path.join(os.path.dirname(__file__), '../data/metadata/spotify_metadata.json')
	user_history_path = os.path.join(os.path.dirname(__file__), '../data/metadata/user_history.json')
	controller = RecsController(metadata_path, user_history_path)
	view = RecsView(controller)

	# Example user preferences (customize as needed)
	user_preferences = {
		'genres': ['pop', 'rock'],
		'artists': ['Artist Name']
	}

	view.show_recommendations(user_preferences=user_preferences, top_n=5)

	# Example: Add a track to history (replace 'track_id' with a real ID)
	# view.add_track_to_history('track_id')

if __name__ == '__main__':
	main()
