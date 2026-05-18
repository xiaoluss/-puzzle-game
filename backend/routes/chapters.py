from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from routes.admin_auth import admin_required
from models import db, Chapter, Scene

chapters_bp = Blueprint('chapters', __name__, url_prefix='/api/chapters')

@chapters_bp.route('', methods=['GET'])
@admin_required
def get_chapters():
    chapters = Chapter.query.order_by(Chapter.sort_order).all()
    return jsonify([{
        'id': c.id,
        'title': c.title,
        'sort_order': c.sort_order,
        'scene_count': len(c.scenes)
    } for c in chapters])

@chapters_bp.route('/<int:chapter_id>', methods=['GET'])
@admin_required
def get_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    scenes = Scene.query.filter_by(chapter_id=chapter_id).order_by(Scene.sort_order).all()
    return jsonify({
        'id': chapter.id,
        'title': chapter.title,
        'sort_order': chapter.sort_order,
        'scenes': [s.to_dict() for s in scenes]
    })

@chapters_bp.route('', methods=['POST'])
@admin_required
def create_chapter():
    data = request.get_json()
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': '章节标题不能为空'}), 400

    max_order = db.session.query(db.func.max(Chapter.sort_order)).scalar() or 0
    chapter = Chapter(title=title, sort_order=max_order + 1)
    db.session.add(chapter)
    db.session.commit()

    return jsonify({'id': chapter.id, 'title': chapter.title, 'sort_order': chapter.sort_order}), 201

@chapters_bp.route('/<int:chapter_id>', methods=['PUT'])
@admin_required
def update_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    data = request.get_json()
    if 'title' in data:
        chapter.title = data['title'].strip()
    if 'sort_order' in data:
        chapter.sort_order = data['sort_order']
    db.session.commit()
    return jsonify({'id': chapter.id, 'title': chapter.title, 'sort_order': chapter.sort_order})

@chapters_bp.route('/<int:chapter_id>', methods=['DELETE'])
@admin_required
def delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    return jsonify({'message': '删除成功'})

@chapters_bp.route('/<int:chapter_id>/duplicate', methods=['POST'])
@admin_required
def duplicate_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    new_chapter = Chapter(title=chapter.title + ' (副本)', sort_order=chapter.sort_order + 1)
    db.session.add(new_chapter)
    db.session.flush()

    for scene in Scene.query.filter_by(chapter_id=chapter_id).order_by(Scene.sort_order).all():
        new_scene = Scene(
            chapter_id=new_chapter.id,
            sort_order=scene.sort_order,
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
        db.session.add(new_scene)

    db.session.commit()
    return jsonify({'id': new_chapter.id, 'title': new_chapter.title}), 201

@chapters_bp.route('/reorder', methods=['PUT'])
@admin_required
def reorder_chapters():
    data = request.get_json()
    for item in data:
        chapter = Chapter.query.get(item['id'])
        if chapter:
            chapter.sort_order = item['sort_order']
    db.session.commit()
    return jsonify({'message': '排序成功'})
