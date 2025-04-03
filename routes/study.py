from flask import Blueprint, render_template, request, session, redirect, url_for
from recommender import generate_study_plan
from scheduler import create_schedule

study = Blueprint('study', __name__)

@study.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dashboard.html')

@study.route('/generate_plan', methods=['POST'])
def generate_plan():
    subjects = request.form.getlist('subjects')
    past_scores = [int(score) for score in request.form.getlist('scores')]
    study_method = request.form['study_method']
    
    study_plan = generate_study_plan(subjects, past_scores, study_method)
    schedule = create_schedule(study_plan)
    
    return render_template('result.html', plan=study_plan, schedule=schedule)
