from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    with app.app_context():
        try:
            db.create_all()  # Create database tables
        except Exception as e:
            print(f"Error creating database tables: {e}")
