import os
from flask import Blueprint, request, jsonify, current_app
from routes.admin_auth import admin_required
from models import db, Character

characters_bp = Blueprint('characters', __name__, url_prefix='/api/characters')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@characters_bp.route('', methods=['GET'])
@admin_required
def get_characters():
    characters = Character.query.order_by(Character.id).all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'avatar': c.avatar,
        'description': c.description
    } for c in characters])

@characters_bp.route('', methods=['POST'])
@admin_required
def create_character():
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '')
    if not name:
        return jsonify({'error': '角色名不能为空'}), 400

    character = Character(name=name, description=description)

    if 'avatar' in request.files:
        file = request.files['avatar']
        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f'char_{character.id}_{secure_filename(file.filename)}'
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            character.avatar = f'/uploads/characters/{filename}'

    db.session.add(character)
    db.session.commit()

    return jsonify({
        'id': character.id,
        'name': character.name,
        'avatar': character.avatar,
        'description': character.description
    }), 201

@characters_bp.route('/<int:character_id>', methods=['PUT'])
@admin_required
def update_character(character_id):
    character = Character.query.get_or_404(character_id)
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '')

    if name:
        character.name = name
    character.description = description

    if 'avatar' in request.files:
        file = request.files['avatar']
        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f'char_{character_id}_{secure_filename(file.filename)}'
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            character.avatar = f'/uploads/characters/{filename}'

    db.session.commit()
    return jsonify({
        'id': character.id,
        'name': character.name,
        'avatar': character.avatar,
        'description': character.description
    })

@characters_bp.route('/<int:character_id>', methods=['DELETE'])
@admin_required
def delete_character(character_id):
    character = Character.query.get_or_404(character_id)
    db.session.delete(character)
    db.session.commit()
    return jsonify({'message': '删除成功'})
