import functools

from sqlalchemy.sql import select
from flask import Blueprint, current_app, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash

from app.models import users

bp = Blueprint('auth', __name__, url_prefix='/auth')

def init_app(app):
    @app.jwt.unauthorized_loader
    def unauthorized_callback(message):
        return jsonify(code=401, data={
            'message': message,
        }), 401

    @app.jwt.invalid_token_loader
    def invalid_token_callback(message):
        return jsonify(code=401, data={
            'message': message,
        }), 401

@bp.route('/register', methods=['POST'])
def register():
    error = None
    try:
        username = request.json.get('username', '')
        password = request.json.get('password', '')

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is not None:
            return jsonify(code=400, data={ 'message': error }), 400

        conn = current_app.db_engine.connect()

        query = select([
            users.c.password,
        ]).where(users.c.username == username)
        result = conn.execute(query)
        row = result.fetchone()
        result.close()

        if row:
            error = 'User {} is already registered.'.format(username)
            return jsonify(code=422, data={ 'message': error }), 422

        result = conn.execute(users.insert().returning(users.c.id, users.c.username),
            username=username, password=generate_password_hash(password))
        user = result.fetchone()
        return jsonify(code=200, data={
            'user': {
                'id': user[users.c.id],
                'username': user[users.c.username],
            },
        })

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=500, data={}), 500

@bp.route('/login', methods=['POST'])
def login():
    error = None
    try:
        username = request.json.get('username', '')
        password = request.json.get('password', '')

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is not None:
            return jsonify(code=400, data={ 'message': error }), 400

        conn = current_app.db_engine.connect()
        query = select([
            users.c.id,
            users.c.username,
            users.c.password,
        ]).where(users.c.username == username)
        result = conn.execute(query)
        row = result.fetchone()
        result.close()

        if not row or not check_password_hash(row[users.c.password], password):
            return jsonify(code=401, data={ 'message': 'Unauthorized user.' }), 401
        else:
            identity = {
                'id': row[users.c.id],
                'username': row[users.c.username],
            }
            access_token = create_access_token(identity=identity)
            return jsonify(code=200, data={
                'user': identity,
                'access_token': access_token,
            })

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=500, data={}), 500

    return jsonify(code=200, data={
        'access_token': access_token,
    })
