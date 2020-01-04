from sqlalchemy.sql import select, func
from flask import Blueprint, current_app, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models import users, posts
from app.errors import BadRequest, Forbidden, NotFound
from app.utils import datetime

bp = Blueprint('post', __name__, url_prefix='/posts')

@bp.route('/', methods=['GET'])
def list_post():
    try:
        offset = int(request.args.get('offset', 0))
        limit = int(request.args.get('limit', 20))
        if limit <= 0:
            raise ValueError('Limit should be positive.')
        if limit > 50:
            raise ValueError('Limit should be under 50.')
    except Exception as e:
        raise BadRequest(message=e)

    conn = current_app.db_engine.connect()
    query = select([
        posts.c.id,
        posts.c.title,
        posts.c.created_ts,
        posts.c.updated_ts,
        users.c.id,
        users.c.username,
    ])\
        .select_from(posts.join(users, users.c.id == posts.c.author_id))\
        .order_by(posts.c.created_ts)\
        .offset(offset)\
        .limit(limit)
    count_query = select([func.count(posts.c.id)])

    raw_posts = conn.execute(query).fetchall()
    count = conn.execute(count_query).fetchone()[0]
    res_posts = []
    for row in raw_posts:
        res_posts.append({
            'id': row[posts.c.id],
            'title': row[posts.c.title],
            'created_ts': datetime.to_seconds(row[posts.c.created_ts]),
            'updated_ts': datetime.to_seconds(row[posts.c.updated_ts]),
            'author': {
                'id': row[users.c.id],
                'username': row[users.c.username],
            },
        })
    return jsonify(code=200, data={
        'posts': res_posts,
        'meta': {
            'offset': offset,
            'limit': limit,
            'total': count,
        },
    })

@bp.route('/', methods=['POST'])
@jwt_required
def create_post():
    try:
        title = request.json.get('title', '')
        body = request.json.get('body', {})
        if not title:
            raise ValueError('Title is required.')
    except Exception as e:
        raise BadRequest(message=e)

    user = get_jwt_identity()
    conn = current_app.db_engine.connect()
    result = conn.execute(
        posts.insert().returning(
            posts.c.id,
            posts.c.title,
            posts.c.body,
            posts.c.created_ts,
            posts.c.updated_ts,
        ),
        author_id=user['id'], title=title, body=body
    )
    post = result.fetchone()
    return jsonify(code=200, data={
        'post': {
            'id': post[posts.c.id],
            'title': post[posts.c.title],
            'body': post[posts.c.body],
            'created_ts': datetime.to_seconds(post[posts.c.created_ts]),
            'updated_ts': datetime.to_seconds(post[posts.c.updated_ts]),
        },
    })

@bp.route('/<id>', methods=['GET'])
def read_post(id):
    conn = current_app.db_engine.connect()
    query = select([
        posts.c.id,
        posts.c.title,
        posts.c.body,
        posts.c.created_ts,
        posts.c.updated_ts,
    ]).where(posts.c.id == id)
    result = conn.execute(query)
    post = result.fetchone()
    result.close()

    if not post:
        raise NotFound(message='Post not found.')

    return jsonify(code=200, data={
            'post': {
                'id': post[posts.c.id],
                'title': post[posts.c.title],
                'body': post[posts.c.body],
                'created_ts': datetime.to_seconds(post[posts.c.created_ts]),
                'updated_ts': datetime.to_seconds(post[posts.c.updated_ts]),
            },
        })

@bp.route('/<id>', methods=['PUT', 'PATCH'])
@jwt_required
def update_post(id):
    try:
        title = request.json.get('title', '')
        body = request.json.get('body', {})
        if not title:
            raise ValueError('Title is required.')
    except Exception as e:
        raise BadRequest(message=e)

    user = get_jwt_identity()
    conn = current_app.db_engine.connect()
    query = posts\
        .update()\
        .values(title=title, body=body)\
        .where(posts.c.author_id == user['id'])\
        .where(posts.c.id == id)\
        .returning(
            posts.c.id,
            posts.c.title,
            posts.c.body,
            posts.c.created_ts,
            posts.c.updated_ts,
        )
    result = conn.execute(query)
    post = result.fetchone()

    if not post:
        raise Forbidden(message='You are not allowed to access this post.')

    return jsonify(code=200, data={
        'post': {
            'id': post[posts.c.id],
            'title': post[posts.c.title],
            'body': post[posts.c.body],
            'created_ts': datetime.to_seconds(post[posts.c.created_ts]),
            'updated_ts': datetime.to_seconds(post[posts.c.updated_ts]),
        },
    })

@bp.route('/<id>', methods=['DELETE'])
@jwt_required
def delete_post(id):
    user = get_jwt_identity()
    conn = current_app.db_engine.connect()
    query = posts\
        .delete()\
        .where(posts.c.author_id == user['id'])\
        .where(posts.c.id == id)\
        .returning(posts.c.id, posts.c.title, posts.c.body)
    result = conn.execute(query)
    post = result.fetchone()

    if not post:
        raise Forbidden(message='You are not allowed to access this post.')

    return jsonify(code=200, data={
        'post': {
            'id': post[posts.c.id],
            'title': post[posts.c.title],
            'body': post[posts.c.body],
        },
    })
