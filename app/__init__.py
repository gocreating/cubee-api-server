import os
import yaml

from flask import Flask, jsonify
from flask_cors import CORS

is_prod = not 'CONFIG_PATH' in os.environ

def get_config():
    config_dict = yaml.safe_load(open(
        '/etc/config.yaml' if is_prod else os.path.join(os.path.dirname(__file__), '..', os.environ['CONFIG_PATH'])
    ))
    return config_dict

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True, subdomain_matching=True)

    ##################
    ## Setup CORS ##
    ##################
    CORS(app)

    ##################
    ## Setup config ##
    ##################
    config_dict = get_config()
    app.config.from_mapping(
        SECRET_KEY=None if is_prod else 'dev',
        SERVER_NAME=None if is_prod else config_dict['SERVER_NAME'],
        SQLALCHEMY_DATABASE_URI=config_dict['SQLALCHEMY_DATABASE_URI'],
    )
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    app.logger.info('Config loaded.')
    app.logger.info('\tinstance_path: {0}'.format(app.instance_path))

    ####################
    ## Setup database ##
    ####################
    from . import db
    db.init_app(app)
    app.logger.info('Database connected.')

    ###################
    ## Setup routing ##
    ###################
    from . import auth
    app.register_blueprint(auth.bp)

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route('/info')
    def config():
        return jsonify(
            repoName=os.environ['repoName'],
            commitSHA1=os.environ['commitSHA1'],
            buildDate=os.environ['buildDate'],
            imageTag=os.environ['imageTag'],
        )

    @app.route('/')
    def index():
        return 'Yo, this is cubee.cc'

    @app.route('/sub', subdomain="<username>")
    def username_test(username):
        return 'Hi, {0}'.format(username)

    return app
