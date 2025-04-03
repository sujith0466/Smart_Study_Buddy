import requests
import os

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")  # Use environment variable

def get_youtube_suggestions(subjects):
    base_url = "https://www.googleapis.com/youtube/v3/search"
    suggestions = {}
    
    for subject in subjects:
        params = {
            'part': 'snippet',
            'q': f'{subject} tutorial',
            'key': YOUTUBE_API_KEY,
            'maxResults': 3
        }
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()
            suggestions[subject] = [
                f"https://www.youtube.com/watch?v={item['id']['videoId']}" 
                for item in data.get('items', []) if 'videoId' in item.get('id', {})
            ]
        except requests.RequestException as e:
            print(f"Error fetching YouTube suggestions: {e}")
            suggestions[subject] = []  # Return empty list on error
    
    return suggestions
