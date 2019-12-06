import functools

from sqlalchemy.sql import select
from flask import Blueprint, current_app, request, make_response, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash

from app.models import users

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST'])
def register():
    error = None
    try:
        username = request.json['username']
        password = request.json['password']

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        conn = current_app.db_engine.connect()

        query = select([
            users.c.password,
        ]).where(users.c.username == username)
        result = conn.execute(query)
        row = result.fetchone()
        result.close()

        if row:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            result = conn.execute(users.insert().returning(users.c.id, users.c.username),
                username=username, password=generate_password_hash(password))
            user = result.fetchone()
            return jsonify(status=200, user={
                'id': user[users.c.id],
                'username': user[users.c.username],
            })
        return make_response(jsonify(status=400, error=error), 400)
    except KeyError as e:
        return make_response(jsonify(status=400, error=error), 400)
    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify(status=500), 500)

@bp.route('/login', methods=['POST'])
def login():
    error = None
    try:
        username = request.json['username']
        password = request.json['password']

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
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
                return jsonify(status=401, error='Unauthorized'), 401
            else:
                identity = {
                    'id': row[users.c.id],
                    'username': row[users.c.username],
                }
                access_token = create_access_token(identity=identity)
                return jsonify(status=200, user=identity, access_token=access_token)
        return make_response(jsonify(status=400, error=error), 400)
    except KeyError as e:
        return make_response(jsonify(status=400, error=error), 400)
    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify(status=500), 500)

    return jsonify(access_token=access_token), 200
