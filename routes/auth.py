from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from models import User, db
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')

            # Validate form inputs
            if not username or not password:
                flash("All fields are required!", "danger")
                return redirect(url_for('auth.register'))

            # Check if user already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash("Username already taken! Try a different one.", "warning")
                return redirect(url_for('auth.register'))

            # Hash password and save new user
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()  # Rollback transaction if error occurs
            flash(f"Error during registration: {str(e)}", "danger")  # Display actual error
            return redirect(url_for('auth.register'))

    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')

            # Validate inputs
            if not username or not password:
                flash("Please enter both username and password.", "danger")
                return redirect(url_for('auth.login'))

            # Retrieve user from database
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id  # Store user in session
                flash("Login successful!", "success")
                return redirect(url_for('study.dashboard'))  # Redirect to dashboard

            flash("Invalid username or password", "danger")
            return redirect(url_for('auth.login'))

        except Exception as e:
            flash(f"Login error: {str(e)}", "danger")
            return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logged out successfully.", "info")
    return redirect(url_for('auth.login'))
