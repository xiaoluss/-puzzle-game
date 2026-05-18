import random
import string
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Room, RoomMember, Scene

rooms_bp = Blueprint('rooms', __name__, url_prefix='/api/rooms')

def generate_code():
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not Room.query.filter_by(code=code).first():
            return code

@rooms_bp.route('/create', methods=['POST'])
@jwt_required()
def create_room():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    max_players = data.get('max_players', 2)
    chapter_id = data.get('chapter_id')
    player_name = data.get('player_name', '')

    if max_players < 2 or max_players > 5:
        return jsonify({'error': '人数范围2-5'}), 400

    existing = Room.query.filter_by(host_id=user_id, status='waiting').first()
    if existing:
        return jsonify({'error': '你已有等待中的房间', 'room_code': existing.code}), 400

    code = generate_code()
    room = Room(
        code=code,
        host_id=user_id,
        chapter_id=chapter_id,
        status='waiting',
        max_players=max_players
    )
    db.session.add(room)
    db.session.flush()

    member = RoomMember(room_id=room.id, user_id=user_id, player_name=player_name)
    db.session.add(member)
    db.session.commit()

    return jsonify(room.to_dict()), 201

@rooms_bp.route('/join', methods=['POST'])
@jwt_required()
def join_room():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    code = data.get('code', '').strip().upper()
    player_name = data.get('player_name', '')

    room = Room.query.filter_by(code=code).first()
    if not room:
        return jsonify({'error': '房间不存在'}), 404
    if room.status != 'waiting':
        return jsonify({'error': '游戏已开始'}), 400
    if len(room.members) >= room.max_players:
        return jsonify({'error': '房间已满'}), 400
    if any(m.user_id == user_id for m in room.members):
        return jsonify(room.to_dict())

    member = RoomMember(room_id=room.id, user_id=user_id, player_name=player_name)
    db.session.add(member)
    db.session.commit()

    return jsonify(room.to_dict())

@rooms_bp.route('/<code>', methods=['GET'])
@jwt_required()
def get_room(code):
    room = Room.query.filter_by(code=code.upper()).first()
    if not room:
        return jsonify({'error': '房间不存在'}), 404
    return jsonify(room.to_dict())

@rooms_bp.route('/<code>/start', methods=['POST'])
@jwt_required()
def start_game(code):
    user_id = int(get_jwt_identity())
    room = Room.query.filter_by(code=code.upper()).first()
    if not room:
        return jsonify({'error': '房间不存在'}), 404
    if room.host_id != user_id:
        return jsonify({'error': '只有房主可以开始'}), 403

    data = request.get_json() or {}
    chapter_id = data.get('chapter_id') or room.chapter_id
    if not chapter_id:
        return jsonify({'error': '需要选择章节'}), 400

    if not room.chapter_id:
        room.chapter_id = chapter_id

    first_scene = Scene.query.filter_by(chapter_id=room.chapter_id).order_by(Scene.sort_order).first()
    if not first_scene:
        return jsonify({'error': '该章节没有场景'}), 400

    room.current_scene_id = first_scene.id
    room.status = 'playing'

    for m in room.members:
        m.puzzle_completed = 0

    db.session.commit()
    return jsonify(room.to_dict())

@rooms_bp.route('/<code>/puzzle-done', methods=['POST'])
@jwt_required()
def puzzle_done(code):
    user_id = int(get_jwt_identity())
    room = Room.query.filter_by(code=code.upper()).first()
    if not room:
        return jsonify({'error': '房间不存在'}), 404
    if room.status != 'playing':
        return jsonify({'error': '游戏未进行中'}), 400

    member = RoomMember.query.filter_by(room_id=room.id, user_id=user_id).first()
    if not member:
        return jsonify({'error': '你不是房间成员'}), 403

    member.puzzle_completed = 1
    db.session.commit()

    all_done = all(m.puzzle_completed == 1 for m in room.members)
    return jsonify({
        'all_completed': all_done,
        'completed_count': sum(1 for m in room.members if m.puzzle_completed == 1),
        'total_players': len(room.members)
    })

@rooms_bp.route('/<code>/advance-scene', methods=['POST'])
@jwt_required()
def advance_scene(code):
    user_id = int(get_jwt_identity())
    room = Room.query.filter_by(code=code.upper()).first()
    if not room:
        return jsonify({'error': '房间不存在'}), 404
    if room.host_id != user_id:
        return jsonify({'error': '只有房主可以推进'}), 403

    all_done = all(m.puzzle_completed == 1 for m in room.members)
    if not all_done:
        return jsonify({'error': '还有玩家未完成解谜'}), 400

    current = Scene.query.get(room.current_scene_id)
    if not current:
        return jsonify({'error': '场景不存在'}), 404

    next_scene = Scene.query.filter_by(chapter_id=room.chapter_id).filter(
        Scene.sort_order > current.sort_order
    ).order_by(Scene.sort_order).first()

    if not next_scene:
        room.status = 'completed'
        db.session.commit()
        return jsonify({'message': '所有关卡已完成', 'status': 'completed'})

    room.current_scene_id = next_scene.id
    for m in room.members:
        m.puzzle_completed = 0
    db.session.commit()

    return jsonify(room.to_dict())

@rooms_bp.route('/<code>/leave', methods=['POST'])
@jwt_required()
def leave_room(code):
    user_id = int(get_jwt_identity())
    room = Room.query.filter_by(code=code.upper()).first()
    if not room:
        return jsonify({'error': '房间不存在'}), 404

    member = RoomMember.query.filter_by(room_id=room.id, user_id=user_id).first()
    if not member:
        return jsonify({'error': '你不是房间成员'}), 403

    if room.host_id == user_id:
        db.session.delete(room)
    else:
        db.session.delete(member)
    db.session.commit()
    return jsonify({'message': '已离开房间'})

@rooms_bp.route('/<code>/heartbeat', methods=['POST'])
@jwt_required()
def heartbeat(code):
    user_id = int(get_jwt_identity())
    room = Room.query.filter_by(code=code.upper()).first()
    if not room:
        return jsonify({'error': '房间不存在'}), 404

    member = RoomMember.query.filter_by(room_id=room.id, user_id=user_id).first()
    if not member:
        return jsonify({'error': '你不是房间成员'}), 403

    member.last_heartbeat = datetime.utcnow()
    db.session.commit()
    return jsonify({'ok': True})

@rooms_bp.route('/my-active', methods=['GET'])
@jwt_required()
def my_active_room():
    user_id = int(get_jwt_identity())
    member = RoomMember.query.filter_by(user_id=user_id).join(Room).filter(
        Room.status.in_(['waiting', 'playing'])
    ).first()
    if not member:
        return jsonify({'room': None})
    return jsonify({'room': member.room.to_dict()})
