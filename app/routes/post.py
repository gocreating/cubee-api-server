from sqlalchemy.sql import select
from flask import Blueprint, current_app, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models import posts

bp = Blueprint('post', __name__, url_prefix='/posts')

@bp.route('/', methods=['POST'])
@jwt_required
def create_post():
    error = None
    try:
        title = request.json.get('title', '')
        body = request.json.get('body', {})
        if not title:
            error = 'Title is required.'
        if error is not None:
            return jsonify(code=400, data={ 'message': error }), 400

        user = get_jwt_identity()
        conn = current_app.db_engine.connect()
        result = conn.execute(posts.insert().returning(posts.c.id, posts.c.title, posts.c.body),
            author_id=user['id'], title=title, body=body)
        post = result.fetchone()
        return jsonify(code=200, data={
            'post': {
                'id': post[posts.c.id],
                'title': post[posts.c.title],
                'body': post[posts.c.body],
            },
        })

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=500, data=e), 500

@bp.route('/<id>', methods=['GET'])
def read_post(id):
    conn = current_app.db_engine.connect()
    query = select([
        posts.c.id,
        posts.c.title,
        posts.c.body,
    ]).where(posts.c.id == id)
    result = conn.execute(query)
    post = result.fetchone()
    result.close()

    if not post:
        return jsonify(code=404, data={ 'message': 'Post not found.' }), 404

    return jsonify(code=200, data={
            'post': {
                'id': post['id'],
                'title': post['title'],
                'body': post['body'],
            },
        })

@bp.route('/<id>', methods=['PUT', 'PATCH'])
@jwt_required
def update_post(id):
    error = None
    try:
        title = request.json.get('title', '')
        body = request.json.get('body', {})
        if not title:
            error = 'Title is required.'
        if error is not None:
            return jsonify(code=400, data={ 'message': error }), 400

        user = get_jwt_identity()
        conn = current_app.db_engine.connect()
        query = posts\
            .update()\
            .values(title=title, body=body)\
            .where(posts.c.author_id == user['id'])\
            .where(posts.c.id == id)\
            .returning(posts.c.id, posts.c.title, posts.c.body)
        result = conn.execute(query)
        post = result.fetchone()

        if not post:
            return jsonify(code=403, data={ 'message': 'You are not allowed to access this post.' }), 403

        return jsonify(code=200, data={
            'post': {
                'id': post[posts.c.id],
                'title': post[posts.c.title],
                'body': post[posts.c.body],
            },
        })

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=500, data=e), 500
