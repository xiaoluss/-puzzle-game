from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    progress = db.relationship('UserProgress', backref='user', lazy=True)

class Character(db.Model):
    __tablename__ = 'characters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    avatar = db.Column(db.String(200), default='')
    description = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Chapter(db.Model):
    __tablename__ = 'chapters'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    scenes = db.relationship('Scene', backref='chapter', lazy=True,
                             order_by='Scene.sort_order',
                             cascade='all, delete-orphan')

class Scene(db.Model):
    __tablename__ = 'scenes'
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    sort_order = db.Column(db.Integer, default=0)
    scene_type = db.Column(db.String(20), nullable=False)

    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=True)
    character = db.relationship('Character')

    lines = db.Column(db.Text, default='[]')
    text = db.Column(db.Text, default='')
    question = db.Column(db.Text, default='')
    answer = db.Column(db.Text, default='')
    answer_type = db.Column(db.String(20), default='text')
    choices = db.Column(db.Text, default='[]')
    image_areas = db.Column(db.Text, default='[]')
    image_url = db.Column(db.String(200), default='')
    accepted_answers = db.Column(db.Text, default='[]')
    hints = db.Column(db.Text, default='[]')
    fail_limit = db.Column(db.Integer, default=3)
    success_next_scene_id = db.Column(db.Integer, nullable=True)
    branches = db.Column(db.Text, default='[]')

    def to_dict(self):
        return {
            'id': self.id,
            'chapter_id': self.chapter_id,
            'sort_order': self.sort_order,
            'scene_type': self.scene_type,
            'character_id': self.character_id,
            'character': {
                'id': self.character.id,
                'name': self.character.name,
                'avatar': self.character.avatar
            } if self.character else None,
            'lines': json.loads(self.lines) if self.lines else [],
            'text': self.text,
            'question': self.question,
            'answer': self.answer,
            'answer_type': self.answer_type,
            'choices': json.loads(self.choices) if self.choices else [],
            'image_areas': json.loads(self.image_areas) if self.image_areas else [],
            'image_url': self.image_url,
            'accepted_answers': json.loads(self.accepted_answers) if self.accepted_answers else [],
            'hints': json.loads(self.hints) if self.hints else [],
            'fail_limit': self.fail_limit,
            'success_next_scene_id': self.success_next_scene_id,
            'branches': json.loads(self.branches) if self.branches else []
        }

class UserProgress(db.Model):
    __tablename__ = 'user_progress'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    current_chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=True)
    current_scene_id = db.Column(db.Integer, db.ForeignKey('scenes.id'), nullable=True)
    completed_scenes = db.Column(db.Text, default='[]')
    puzzle_fails = db.Column(db.Text, default='{}')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'current_chapter_id': self.current_chapter_id,
            'current_scene_id': self.current_scene_id,
            'completed_scenes': json.loads(self.completed_scenes) if self.completed_scenes else [],
            'puzzle_fails': json.loads(self.puzzle_fails) if self.puzzle_fails else {}
        }

class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(6), unique=True, nullable=False)
    host_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=True)
    current_scene_id = db.Column(db.Integer, db.ForeignKey('scenes.id'), nullable=True)
    status = db.Column(db.String(20), default='waiting')
    max_players = db.Column(db.Integer, default=2)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    members = db.relationship('RoomMember', backref='room', lazy=True,
                              cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'host_id': self.host_id,
            'chapter_id': self.chapter_id,
            'current_scene_id': self.current_scene_id,
            'status': self.status,
            'max_players': self.max_players,
            'member_count': len(self.members),
            'members': [m.to_dict() for m in self.members]
        }

class RoomMember(db.Model):
    __tablename__ = 'room_members'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    player_name = db.Column(db.String(50), default='')
    puzzle_completed = db.Column(db.Integer, default=0)
    last_heartbeat = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'player_name': self.player_name,
            'puzzle_completed': self.puzzle_completed,
            'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None
        }

class AdminUser(db.Model):
    __tablename__ = 'admin_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
