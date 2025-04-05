from collections import defaultdict

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
