"""
用户认证模块 - 注册、登录、Session管理
"""
import os
import json
import hashlib
import secrets
from datetime import datetime
from functools import wraps
from flask import request, jsonify, session


USERS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'users.json')
SESSION_DURATION = 60 * 60 * 24 * 7  # 7天


class UserManager:
    """用户管理"""

    def __init__(self):
        self._ensure_file()

    def _ensure_file(self):
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        if not os.path.exists(USERS_FILE):
            self._save({})

    def _load(self):
        self._ensure_file()
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save(self, data):
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _hash_password(self, password, salt=None):
        if salt is None:
            salt = secrets.token_hex(16)
        h = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return f"{salt}${h.hex()}"

    def _verify_password(self, password, stored):
        salt = stored.split('$')[0]
        return self._hash_password(password, salt) == stored

    def register(self, username, password):
        """注册新用户"""
        users = self._load()
        username = username.strip().lower()

        if not username or len(username) < 2:
            return False, '用户名至少2个字符'
        if not password or len(password) < 4:
            return False, '密码至少4个字符'
        if username in users:
            return False, '用户名已存在'
        if len(users) >= 100:
            return False, '用户数已达上限'

        users[username] = {
            'password': self._hash_password(password),
            'is_admin': len(users) == 0,  # 第一个注册的用户自动成为管理员
            'created_at': datetime.now().isoformat()
        }
        self._save(users)
        return True, '注册成功'

    def login(self, username, password):
        """登录验证"""
        users = self._load()
        username = username.strip().lower()

        if username not in users:
            return False, '用户名或密码错误'

        if not self._verify_password(password, users[username]['password']):
            return False, '用户名或密码错误'

        return True, users[username]

    def get_user(self, username):
        """获取用户信息"""
        users = self._load()
        return users.get(username.strip().lower())

    def list_users(self):
        """列出所有用户（管理员用）"""
        users = self._load()
        result = {}
        for name, info in users.items():
            result[name] = {
                'is_admin': info['is_admin'],
                'created_at': info['created_at']
            }
        return result

    def delete_user(self, username):
        """删除用户（管理员用）"""
        users = self._load()
        username = username.strip().lower()
        if username not in users:
            return False
        if users[username]['is_admin']:
            return False  # 不能删除管理员
        del users[username]
        self._save(users)
        return True

    def change_password(self, username, old_password, new_password):
        """修改密码"""
        users = self._load()
        username = username.strip().lower()
        if username not in users:
            return False, '用户不存在'
        if not self._verify_password(old_password, users[username]['password']):
            return False, '原密码错误'
        users[username]['password'] = self._hash_password(new_password)
        self._save(users)
        return True, '密码修改成功'


# 全局实例
user_manager = UserManager()


def login_required(f):
    """装饰器：需要登录"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return jsonify({'success': False, 'error': '请先登录', 'code': 'AUTH_REQUIRED'}), 401
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """装饰器：需要管理员权限"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return jsonify({'success': False, 'error': '请先登录', 'code': 'AUTH_REQUIRED'}), 401
        user = user_manager.get_user(session['username'])
        if not user or not user.get('is_admin'):
            return jsonify({'success': False, 'error': '需要管理员权限', 'code': 'ADMIN_REQUIRED'}), 403
        return f(*args, **kwargs)
    return decorated
