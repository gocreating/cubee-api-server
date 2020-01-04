import os

from flask import Blueprint, current_app, jsonify

from app.errors import GenericError

bp = Blueprint('main', __name__, url_prefix='/')

def init_app(app):
    @app.errorhandler(GenericError)
    def handle_generic_error(error):
        return error.to_response()

    @app.errorhandler(Exception)
    def handle_uncaught_error(error):
        current_app.logger.error(error)
        return jsonify(code=500, data={
            'message': str(error),
        }), 500

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

@bp.route('/errors/4xx')
def raise_bad_request_error():
    raise GenericError('Raise 4xx error on purpose', code=400)

@bp.route('/errors/5xx')
def raise_internal_error():
    raise GenericError('Raise 5xx error on purpose')

@bp.route('/errors/uncaught')
def raise_uncaught_error():
    raise Exception('Raise uncaught error on purpose')
