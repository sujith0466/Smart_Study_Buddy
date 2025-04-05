import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_default_secret_key')
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', 'your_default_api_key')
