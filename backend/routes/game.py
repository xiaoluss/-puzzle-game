from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from models import Chapter, Scene

game_bp = Blueprint('game', __name__, url_prefix='/api/game')

@game_bp.route('/chapters', methods=['GET'])
@jwt_required()
def get_game_chapters():
    chapters = Chapter.query.order_by(Chapter.sort_order).all()
    return jsonify([{
        'id': c.id,
        'title': c.title,
        'sort_order': c.sort_order
    } for c in chapters])

@game_bp.route('/chapter/<int:chapter_id>/scenes', methods=['GET'])
@jwt_required()
def get_game_scenes(chapter_id):
    scenes = Scene.query.filter_by(chapter_id=chapter_id).order_by(Scene.sort_order).all()
    result = []
    for s in scenes:
        data = s.to_dict()
        data.pop('answer', None)
        data.pop('accepted_answers', None)
        result.append(data)
    return jsonify(result)

@game_bp.route('/scene/<int:scene_id>', methods=['GET'])
@jwt_required()
def get_game_scene(scene_id):
    scene = Scene.query.get_or_404(scene_id)
    data = scene.to_dict()
    data.pop('answer', None)
    data.pop('accepted_answers', None)
    return jsonify(data)

@game_bp.route('/verify/<int:scene_id>', methods=['POST'])
@jwt_required()
def verify_answer(scene_id):
    from flask import request
    scene = Scene.query.get_or_404(scene_id)
    user_answer = request.get_json().get('answer', '')

    import json
    accepted = json.loads(scene.accepted_answers) if scene.accepted_answers else []

    if scene.answer_type == 'text':
        correct = user_answer.strip() == scene.answer.strip()
        if not correct:
            for acc in accepted:
                if user_answer.strip() == acc.strip():
                    correct = True
                    break
    elif scene.answer_type == 'choice':
        correct = str(user_answer) == str(scene.answer)
    elif scene.answer_type == 'image':
        correct = str(user_answer) == str(scene.answer)
    else:
        correct = False

    return jsonify({
        'correct': correct,
        'success_next_scene_id': scene.success_next_scene_id if correct else None
    })
