from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from models import User, db
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for('auth.login'))  # Redirect to login page

    return render_template('register.html')  # Render form for GET request

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id  # Store user session
            flash("Login successful!", "success")
            return redirect(url_for('study.dashboard'))  # Redirect to dashboard

        flash("Invalid username or password", "error")

    return render_template('login.html')  # Render form for GET request

@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logged out successfully", "info")
    return redirect(url_for('auth.login'))
