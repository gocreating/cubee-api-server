from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('user', __name__, url_prefix='/users')

@bp.route('/me', methods=['GET'])
@jwt_required
def protected():
    user = get_jwt_identity()
    return jsonify(code=200, data={
        'user': user,
    })
