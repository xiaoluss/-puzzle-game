import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models import db, AdminUser

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance'), exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    CORS(app)
    db.init_app(app)
    JWTManager(app)

    from routes.auth import auth_bp
    from routes.characters import characters_bp
    from routes.chapters import chapters_bp
    from routes.scenes import scenes_bp
    from routes.progress import progress_bp
    from routes.game import game_bp
    from routes.rooms import rooms_bp
    from routes.admin_auth import admin_auth_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(characters_bp)
    app.register_blueprint(chapters_bp)
    app.register_blueprint(scenes_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(game_bp)
    app.register_blueprint(rooms_bp)
    app.register_blueprint(admin_auth_bp)

    @app.route('/uploads/characters/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    with app.app_context():
        db.create_all()
        if not AdminUser.query.first():
            admin = AdminUser(
                username=app.config['ADMIN_USERNAME'],
                password=app.config['ADMIN_PASSWORD']
            )
            db.session.add(admin)
            db.session.commit()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
