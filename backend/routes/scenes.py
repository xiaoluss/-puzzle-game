import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from routes.admin_auth import admin_required
from models import db, Scene, Chapter

scenes_bp = Blueprint('scenes', __name__, url_prefix='/api/scenes')

@scenes_bp.route('', methods=['POST'])
@admin_required
def create_scene():
    data = request.get_json()
    chapter_id = data.get('chapter_id')
    scene_type = data.get('scene_type')

    if not chapter_id or not scene_type:
        return jsonify({'error': '缺少必要参数'}), 400
    if scene_type not in ('dialog', 'narrative', 'puzzle_text', 'puzzle_choice', 'puzzle_image'):
        return jsonify({'error': '无效的场景类型'}), 400

    max_order = db.session.query(db.func.max(Scene.sort_order)).filter_by(
        chapter_id=chapter_id
    ).scalar() or 0

    scene = Scene(
        chapter_id=chapter_id,
        sort_order=max_order + 1,
        scene_type=scene_type,
        character_id=data.get('character_id'),
        lines=json.dumps(data.get('lines', []), ensure_ascii=False),
        text=data.get('text', ''),
        question=data.get('question', ''),
        answer=data.get('answer', ''),
        answer_type=data.get('answer_type', 'text'),
        choices=json.dumps(data.get('choices', []), ensure_ascii=False),
        image_areas=json.dumps(data.get('image_areas', []), ensure_ascii=False),
        image_url=data.get('image_url', ''),
        accepted_answers=json.dumps(data.get('accepted_answers', []), ensure_ascii=False),
        hints=json.dumps(data.get('hints', []), ensure_ascii=False),
        fail_limit=data.get('fail_limit', 3),
        success_next_scene_id=data.get('success_next_scene_id'),
        branches=json.dumps(data.get('branches', []), ensure_ascii=False)
    )
    db.session.add(scene)
    db.session.commit()

    return jsonify(scene.to_dict()), 201

@scenes_bp.route('/<int:scene_id>', methods=['PUT'])
@admin_required
def update_scene(scene_id):
    scene = Scene.query.get_or_404(scene_id)
    data = request.get_json()

    if 'character_id' in data:
        scene.character_id = data['character_id']
    if 'lines' in data:
        scene.lines = json.dumps(data['lines'], ensure_ascii=False)
    if 'text' in data:
        scene.text = data['text']
    if 'question' in data:
        scene.question = data['question']
    if 'answer' in data:
        scene.answer = data['answer']
    if 'answer_type' in data:
        scene.answer_type = data['answer_type']
    if 'choices' in data:
        scene.choices = json.dumps(data['choices'], ensure_ascii=False)
    if 'image_areas' in data:
        scene.image_areas = json.dumps(data['image_areas'], ensure_ascii=False)
    if 'image_url' in data:
        scene.image_url = data['image_url']
    if 'accepted_answers' in data:
        scene.accepted_answers = json.dumps(data['accepted_answers'], ensure_ascii=False)
    if 'hints' in data:
        scene.hints = json.dumps(data['hints'], ensure_ascii=False)
    if 'fail_limit' in data:
        scene.fail_limit = data['fail_limit']
    if 'success_next_scene_id' in data:
        scene.success_next_scene_id = data['success_next_scene_id']
    if 'branches' in data:
        scene.branches = json.dumps(data['branches'], ensure_ascii=False)
    if 'sort_order' in data:
        scene.sort_order = data['sort_order']

    db.session.commit()
    return jsonify(scene.to_dict())

@scenes_bp.route('/<int:scene_id>', methods=['DELETE'])
@admin_required
def delete_scene(scene_id):
    scene = Scene.query.get_or_404(scene_id)
    db.session.delete(scene)
    db.session.commit()
    return jsonify({'message': '删除成功'})

@scenes_bp.route('/<int:scene_id>/duplicate', methods=['POST'])
@admin_required
def duplicate_scene(scene_id):
    scene = Scene.query.get_or_404(scene_id)
    new_scene = Scene(
        chapter_id=scene.chapter_id,
        sort_order=scene.sort_order + 1,
        scene_type=scene.scene_type,
        character_id=scene.character_id,
        lines=scene.lines,
        text=scene.text,
        question=scene.question,
        answer=scene.answer,
        answer_type=scene.answer_type,
        choices=scene.choices,
        image_areas=scene.image_areas,
        image_url=scene.image_url,
        accepted_answers=scene.accepted_answers,
        hints=scene.hints,
        fail_limit=scene.fail_limit,
        success_next_scene_id=scene.success_next_scene_id,
        branches=scene.branches
    )
    Scene.query.filter_by(chapter_id=scene.chapter_id).filter(
        Scene.sort_order > scene.sort_order
    ).update({Scene.sort_order: Scene.sort_order + 1})

    db.session.add(new_scene)
    db.session.commit()
    return jsonify(new_scene.to_dict()), 201

@scenes_bp.route('/reorder', methods=['PUT'])
@admin_required
def reorder_scenes():
    data = request.get_json()
    for item in data:
        scene = Scene.query.get(item['id'])
        if scene:
            scene.sort_order = item['sort_order']
    db.session.commit()
    return jsonify({'message': '排序成功'})

@scenes_bp.route('/available-next', methods=['GET'])
@admin_required
def get_available_next_scenes():
    chapter_id = request.args.get('chapter_id', type=int)
    if not chapter_id:
        return jsonify({'error': '需要chapter_id参数'}), 400
    scenes = Scene.query.filter_by(chapter_id=chapter_id).order_by(Scene.sort_order).all()
    return jsonify([{
        'id': s.id,
        'label': f'#{s.sort_order} {s.scene_type}'
    } for s in scenes])
