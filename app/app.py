# import os
# import yaml
# from flask import Flask, Blueprint, jsonify
# from app.models import db

# config_dict = yaml.load(open('/etc/config.yaml'))
# app = Flask(__name__, subdomain_matching=True)
# app.config['SERVER_NAME'] = config_dict['SERVER_NAME']
# app.config['SQLALCHEMY_DATABASE_URI'] = config_dict['SQLALCHEMY_DATABASE_URI']
# db.init_app(app)

# #########
# ## App ##
# #########
# @app.route('/')
# def app_index():
#     return 'app index'

# @app.route('/hello')
# def app_hello():
#     return 'app hello'

# #########
# ## API ##
# #########
# api = Blueprint('api', __name__, subdomain='api')
# @api.route('/')
# def api_index():
#     return 'Welcome to Cubee API Server'

# @api.route('/hello')
# def api_hello():
#     return jsonify(
#         hello='world',
#         num=777,
#     )

# @api.route('/config')
# def api_config():
#     return jsonify(config_dict)

# @api.route('/version')
# def api_version():
#     try:
#         return jsonify(
#             APP_COMMIT_REF=os.environ['APP_COMMIT_REF'],
#             APP_BUILD_DATE=os.environ['APP_BUILD_DATE'],
#         )
#     except:
#         return 'unknown'

# app.register_blueprint(api)

# #############
# ## Dynamic ##
# #############
# @app.route('/test', subdomain="<username>")
# def username_test(username):
#     return 'Hi, {0}'.format(username)

# @app.route('/', subdomain="<username>")
# def username_index(username):
#     return 'Fuck, {0}'.format(username)

# if __name__ == '__main__':
#     app.run()
