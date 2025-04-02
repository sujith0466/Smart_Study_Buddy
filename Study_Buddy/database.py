from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import config

db = SQLAlchemy()

def init_db():
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    with app.app_context():
        db.create_all()
