import functools

from sqlalchemy.sql import select
from flask import Blueprint, current_app, request, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token,
    get_csrf_token,
    set_access_cookies,
    unset_jwt_cookies
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.models import users
from app.errors import BadRequest, Unauthorized, UnprocessableEntity

bp = Blueprint('auth', __name__, url_prefix='/auth')

def init_app(app):
    @app.jwt.unauthorized_loader
    def unauthorized_callback(message):
        return Unauthorized(message).to_response()

    @app.jwt.invalid_token_loader
    def invalid_token_callback(message):
        return Unauthorized(message).to_response()

@bp.route('/register', methods=['POST'])
def register():
    try:
        username = request.json.get('username', '')
        password = request.json.get('password', '')
        if not username:
            raise ValueError('Username is required.')
        elif not password:
            raise ValueError('Password is required.')
    except Exception as e:
        raise BadRequest(message=e)

    conn = current_app.db_engine.connect()
    query = select([ users.c.password ]).where(users.c.username == username)
    result = conn.execute(query)
    row = result.fetchone()
    result.close()

    if row:
        raise UnprocessableEntity('User {} is already registered.'.format(username))

    result = conn.execute(users.insert().returning(users.c.id, users.c.username),
        username=username, password=generate_password_hash(password))
    user = result.fetchone()
    return jsonify(code=200, data={
        'user': {
            'id': user[users.c.id],
            'username': user[users.c.username],
        },
    })

@bp.route('/login', methods=['POST'])
def login():
    try:
        username = request.json.get('username', '')
        password = request.json.get('password', '')
        if not username:
            raise ValueError('Username is required.')
        elif not password:
            raise ValueError('Password is required.')
    except Exception as e:
        raise BadRequest(message=e)

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
        raise Unauthorized('Unauthorized user.')

    identity = {
        'id': row[users.c.id],
        'username': row[users.c.username],
    }
    access_token = create_access_token(identity=identity)
    csrf_token = get_csrf_token(access_token)
    resp = jsonify(code=200, data={
        'user': identity,
        'access_token': access_token,
        'csrf_token': csrf_token,
    })
    set_access_cookies(resp, access_token)
    return resp

@bp.route('/logout', methods=['POST'])
@jwt_required
def logout():
    user = get_jwt_identity()
    resp = jsonify(code=200, data={
        'user': user,
    })
    unset_jwt_cookies(resp)
    return resp
