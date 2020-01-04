from sqlalchemy.sql import select, func
from flask import Blueprint, current_app, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models import users, posts
from app.utils import datetime

bp = Blueprint('user', __name__, url_prefix='/users')

@bp.route('/me', methods=['GET'])
@jwt_required
def read_user():
    user = get_jwt_identity()
    return jsonify(code=200, data={
        'user': user,
    })

@bp.route('/<username>/posts', methods=['GET'])
def list_user_post(username):
    error = None
    try:
        offset = int(request.args.get('offset', 0))
        limit = int(request.args.get('limit', 20))
        if limit <= 0:
            error = 'Limit should be positive.'
        if limit > 50:
            error = 'Limit should be under 50.'
        if error is not None:
            return jsonify(code=400, data={ 'message': error }), 400

        conn = current_app.db_engine.connect()
        query = select([
            posts.c.id,
            posts.c.title,
            posts.c.created_ts,
            posts.c.updated_ts,
        ])\
            .select_from(posts.join(users, users.c.id == posts.c.author_id))\
            .where(users.c.username == username)\
            .order_by(posts.c.created_ts)\
            .offset(offset)\
            .limit(limit)
        count_query = select([func.count(posts.c.id)])\
            .select_from(posts.join(users, users.c.id == posts.c.author_id))\
            .where(users.c.username == username)

        raw_posts = conn.execute(query).fetchall()
        count = conn.execute(count_query).fetchone()[0]
        res_posts = []
        for row in raw_posts:
            res_posts.append({
                'id': row[posts.c.id],
                'title': row[posts.c.title],
                'created_ts': datetime.to_seconds(row[posts.c.created_ts]),
                'updated_ts': datetime.to_seconds(row[posts.c.updated_ts]),
            })
        return jsonify(code=200, data={
            'posts': res_posts,
            'meta': {
                'offset': offset,
                'limit': limit,
                'total': count,
            },
        })

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=500, data=str(e)), 500
