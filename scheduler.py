from collections import defaultdict

def generate_weekly_timetable(subjects, past_scores, study_method, daily_available_time=120):
    """
    Generate a weekly study timetable based on subjects, scores, study method, and time availability.

    Args:
        subjects (list): List of subject names.
        past_scores (list): Corresponding list of past scores (0-100).
        study_method (str): 'video' or 'reading'.
        daily_available_time (int): Minutes available for study per day.

    Returns:
        dict: A dictionary mapping days of the week to a list of study sessions.
    """
    method_multiplier = {
        "reading": 1.0,
        "video": 1.2  # Video takes ~20% longer
    }

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    timetable = defaultdict(list)
    day_index = 0
    session_queue = []

    for subject, score in zip(subjects, past_scores):
        if not (0 <= score <= 100):
            raise ValueError(f"Score for '{subject}' must be between 0 and 100.")

        # Lower scores = more hours
        base_hours = round(max(1, (100 - score) / 10), 1)
        multiplier = method_multiplier.get(study_method.lower(), 1.0)
        total_minutes = int(base_hours * 60 * multiplier)

        while total_minutes > 0:
            session_length = min(60, total_minutes)
            session_queue.append({'subject': subject, 'duration': session_length})
            total_minutes -= session_length

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

        day_index = (day_index + 1) % 7  # Rotate for even distribution

    return dict(timetable)

def create_schedule(study_plan):
    """
    Convert a flat study plan into a dictionary with days as keys.

    Args:
        study_plan (list): List of study sessions (e.g. [{"subject": ..., "duration": ...}, ...])

    Returns:
        dict: Schedule grouped by weekday.
    """
    schedule = {}
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    for i, plan in enumerate(study_plan):
        day = days[i % len(days)]
        schedule.setdefault(day, []).append(plan)

    return schedule
