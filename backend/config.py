import os

class Config:
    SECRET_KEY = 'puzzle-game-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'instance', 'game.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'jwt-secret-key-2024'
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend', 'public', 'uploads', 'characters')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = 'admin123'
