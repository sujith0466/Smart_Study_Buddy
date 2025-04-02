import requests

YOUTUBE_API_KEY = "your_youtube_api_key"

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
        response = requests.get(base_url, params=params).json()
        suggestions[subject] = [
            f"https://www.youtube.com/watch?v={item['id']['videoId']}" 
            for item in response.get('items', []) if 'videoId' in item.get('id', {})
        ]
    
    return suggestions
