import functools

from flask import Blueprint, current_app, request, make_response, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from app.db import get_db
from app.models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST'])
def register():
    try:
        username = request.json['username']
        password = request.json['password']
        db_session = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif User.query.filter_by(username=username).first():
            error = 'User {} is already registered.'.format(username)

        if error is None:
            user = User(username, generate_password_hash(password))
            db_session.add(user)
            db_session.commit()
            return jsonify(status=200, user={
                'id': user.id,
                'username': user.username,
            })
        return make_response(jsonify(status=400, error=error), 400)
    except KeyError as e:
        return make_response(jsonify(status=400, error=error), 400)
    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify(status=500), 500)
