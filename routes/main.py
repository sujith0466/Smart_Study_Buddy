from flask import Blueprint, render_template, request
from recommender import generate_weekly_timetable as generate_study_plan
from scheduler import create_schedule, generate_weekly_timetable
from youtube_api import get_youtube_suggestions

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/generate', methods=['POST'])
def generate():
    subjects = request.form.getlist('subjects[]')
    scores = request.form.getlist('scores[]')
    study_method = request.form.get('study_method')
    daily_time = request.form.get('daily_time', 120)  # Defaults to 120 mins/day if not provided

    if not subjects or not scores or not study_method:
        return render_template('index.html', error="All fields are required.")

    try:
        scores = list(map(int, scores))
        daily_time = int(daily_time)
    except ValueError:
        return render_template('index.html', error="Scores and available time must be valid numbers.")

    # Generate personalized study plan
    study_sessions = generate_study_plan(subjects, scores, study_method)
    schedule = create_schedule(study_sessions)

    # Generate weekly timetable (structured by day)
    timetable = generate_weekly_timetable(subjects, scores, study_method, daily_time)

    # Fetch learning resources (YouTube or article links)
    resources = get_youtube_suggestions(subjects, study_method)

    return render_template(
        'result.html',
        schedule=schedule,
        timetable=timetable,
        resources=resources,
        learning_style=study_method
    )
