import requests
from config import Config  # Import your config class

YOUTUBE_API_KEY = Config.YOUTUBE_API_KEY  # Use from config

def get_youtube_suggestions(subjects, study_method='video'):
    base_url = "https://www.googleapis.com/youtube/v3/search"
    suggestions = {}

    for subject in subjects:
        search_term = f'{subject} tutorial'
        if study_method == 'video':
            search_term = f'{subject} video tutorial'
        elif study_method == 'reading':
            search_term = f'{subject} explained lecture'

        params = {
            'part': 'snippet',
            'q': search_term,
            'key': YOUTUBE_API_KEY,
            'maxResults': 3
        }

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            suggestions[subject] = [
                f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                for item in data.get('items', []) if 'videoId' in item.get('id', {})
            ]
        except requests.RequestException as e:
            print(f"Error fetching YouTube suggestions: {e}")
            suggestions[subject] = []

    return suggestions
