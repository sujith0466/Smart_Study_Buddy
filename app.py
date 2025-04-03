from flask import Flask, render_template, request, session, redirect, url_for, flash
from database import init_db, db
from recommender import generate_study_plan
from scheduler import create_schedule
from youtube_api import get_youtube_suggestions
from routes.auth import auth
from routes.study import study
from routes.api import api
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)

# Load configuration
from config import Config
app.config.from_object(Config)

# Enable CSRF protection
csrf = CSRFProtect(app)

# Initialize database
with app.app_context():
    try:
        init_db(app)
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing the database: {e}")

# Register blueprints
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(study, url_prefix='/study')
app.register_blueprint(api, url_prefix='/api')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        subjects = request.form.getlist('subjects')
        past_scores = request.form.getlist('scores')

        if not subjects or not past_scores:
            return render_template('dashboard.html', error="Subjects and scores are required.")

        try:
            past_scores = list(map(int, past_scores))
        except ValueError:
            return render_template('dashboard.html', error="Scores must be integers.")

        study_method = request.form['study_method']
        recommendations = generate_study_plan(subjects, past_scores, study_method)
        schedule = create_schedule(recommendations)
        resources = get_youtube_suggestions(subjects)

        return render_template('result.html', schedule=schedule, resources=resources)
    
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)