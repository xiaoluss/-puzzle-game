from functools import wraps
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, verify_jwt_in_request
from models import db, AdminUser

admin_auth_bp = Blueprint('admin_auth', __name__, url_prefix='/api/admin')

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        identity = get_jwt_identity()
        if not identity.startswith('admin:'):
            return jsonify({'error': '需要管理员权限'}), 403
        return fn(*args, **kwargs)
    return wrapper

@admin_auth_bp.route('/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')

    admin = AdminUser.query.filter_by(username=username, password=password).first()
    if not admin:
        return jsonify({'error': '账号或密码错误'}), 401

    token = create_access_token(identity='admin:1')
    return jsonify({'token': token, 'username': username})

@admin_auth_bp.route('/change-password', methods=['POST'])
@admin_required
def change_password():
    data = request.get_json()
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')

    if not new_password or len(new_password) < 4:
        return jsonify({'error': '新密码至少4位'}), 400

    admin = AdminUser.query.first()
    if not admin or admin.password != old_password:
        return jsonify({'error': '旧密码错误'}), 403

    admin.password = new_password
    db.session.commit()
    return jsonify({'message': '密码修改成功'})
