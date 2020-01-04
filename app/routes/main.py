import os

from flask import Blueprint, jsonify

bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/')
def index():
    return jsonify(
        code=200,
        data={
            'message': 'This is the root endpoint of cubee api service.',
        },
    )

@bp.route('/info')
def info():
    return jsonify(
        code=200,
        data={
            'repoName': os.environ['repoName'],
            'commitSHA1': os.environ['commitSHA1'],
            'buildDate': os.environ['buildDate'],
            'imageTag': os.environ['imageTag'],
        },
    )
