import requests
from config import Config  # Import your config class
from collections import defaultdict

YOUTUBE_API_KEY = Config.YOUTUBE_API_KEY  # Use from config

# Function for YouTube Suggestions (Video-based)
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

# Function for Reading Suggestions (GFG and W3Schools)
def get_reading_suggestions(subjects):
    gfg_url = "https://www.geeksforgeeks.org/"
    w3_url = "https://www.w3schools.com/"

    suggestions = {}

    for subject in subjects:
        # GeeksforGeeks suggestion
        gfg_link = f"{gfg_url}{subject}-tutorial/"
        w3_link = f"{w3_url}{subject.lower()}/"

        suggestions[subject] = {
            "GeeksforGeeks": gfg_link,
            "W3Schools": w3_link
        }

    return suggestions

# Function to generate Weekly Timetable with study preferences
def generate_weekly_timetable(subjects, past_scores, study_method, daily_available_time=120):
    method_multiplier = {
        "reading": 1.0,
        "video": 1.2
    }

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    timetable = defaultdict(list)
    day_index = 0

    # Build session list with subject info
    session_queue = []

    for subject, score in zip(subjects, past_scores):
        if score < 0 or score > 100:
            raise ValueError("Scores must be between 0 and 100.")

        base_hours = round(max(1, (100 - score) / 10), 1)
        multiplier = method_multiplier.get(study_method.lower(), 1.0)
        total_minutes = int(base_hours * 60 * multiplier)

        while total_minutes > 0:
            session_length = min(60, total_minutes)
            session_queue.append({'subject': subject, 'duration': session_length})
            total_minutes -= session_length

    # Distribute sessions across the week
    daily_time_remaining = [daily_available_time] * 7

    for session in session_queue:
        placed = False
        attempts = 0
        while not placed and attempts < 7:
            if daily_time_remaining[day_index] >= session['duration']:
                timetable[days[day_index]].append(session)
                daily_time_remaining[day_index] -= session['duration']
                placed = True
            else:
                day_index = (day_index + 1) % 7
                attempts += 1

        # Rotate to spread subjects more evenly
        day_index = (day_index + 1) % 7

    return dict(timetable)

# Example usage
subjects = ["Python", "HTML", "CSS"]
study_method = "video"  # or "reading"
past_scores = [85, 90, 70]  # Example past scores

# Get YouTube video suggestions (if study_method is 'video')
if study_method == "video":
    youtube_suggestions = get_youtube_suggestions(subjects, study_method)
    print("YouTube Video Recommendations:", youtube_suggestions)

# Get Reading suggestions (if study_method is 'reading')
if study_method == "reading":
    reading_suggestions = get_reading_suggestions(subjects)
    print("Reading Recommendations (GFG & W3Schools):", reading_suggestions)

# Generate weekly timetable
weekly_timetable = generate_weekly_timetable(subjects, past_scores, study_method)
print("Weekly Timetable:", weekly_timetable)
