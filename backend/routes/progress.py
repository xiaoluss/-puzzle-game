import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, UserProgress

progress_bp = Blueprint('progress', __name__, url_prefix='/api/progress')

@progress_bp.route('', methods=['GET'])
@jwt_required()
def get_progress():
    user_id = int(get_jwt_identity())
    progress = UserProgress.query.filter_by(user_id=user_id).first()
    if not progress:
        return jsonify({
            'current_chapter_id': None,
            'current_scene_id': None,
            'completed_scenes': [],
            'puzzle_fails': {}
        })
    return jsonify(progress.to_dict())

@progress_bp.route('', methods=['PUT'])
@jwt_required()
def save_progress():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    progress = UserProgress.query.filter_by(user_id=user_id).first()
    if not progress:
        progress = UserProgress(user_id=user_id)
        db.session.add(progress)

    if 'current_chapter_id' in data:
        progress.current_chapter_id = data['current_chapter_id']
    if 'current_scene_id' in data:
        progress.current_scene_id = data['current_scene_id']
    if 'completed_scenes' in data:
        progress.completed_scenes = json.dumps(data['completed_scenes'], ensure_ascii=False)
    if 'puzzle_fails' in data:
        progress.puzzle_fails = json.dumps(data['puzzle_fails'], ensure_ascii=False)

    db.session.commit()
    return jsonify(progress.to_dict())
