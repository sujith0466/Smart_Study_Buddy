from flask import Blueprint, render_template, request
from recommender import generate_study_plan
from scheduler import create_schedule
from youtube_api import get_youtube_suggestions

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/generate', methods=['POST'])
def generate():
    subjects = request.form.getlist('subjects[]')
    scores = request.form.getlist('scores[]')
    learning_style = request.form.get('learning_style')  # Updated to match index.html

    if not subjects or not scores or not learning_style:
        return render_template('index.html', error="All fields are required.")

    try:
        scores = list(map(int, scores))
    except ValueError:
        return render_template('index.html', error="Scores must be numbers.")

    recommendations = generate_study_plan(subjects, scores, learning_style)
    schedule = create_schedule(recommendations)
    resources = get_youtube_suggestions(subjects, learning_style)

    return render_template('result.html', schedule=schedule, resources=resources, learning_style=learning_style)
