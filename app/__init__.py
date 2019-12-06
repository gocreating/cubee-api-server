import os
import yaml

from datetime import timedelta
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS

from app import db

is_prod = not 'CONFIG_PATH' in os.environ

def get_config():
    config_dict = yaml.safe_load(open(
        '/etc/config.yaml' if is_prod else os.path.join(os.path.dirname(__file__), '..', os.environ['CONFIG_PATH'])
    ))
    return config_dict

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True, subdomain_matching=True)

    ###############
    ## Setup JWT ##
    ###############
    jwt = JWTManager(app)

    ################
    ## Setup CORS ##
    ################
    CORS(app)

    ##################
    ## Setup config ##
    ##################
    config_dict = get_config()
    app.config.from_mapping(
        SECRET_KEY=None if is_prod else 'dev',
        SERVER_NAME=None if is_prod else config_dict['SERVER_NAME'],
        SQLALCHEMY_DATABASE_URI=config_dict['SQLALCHEMY_DATABASE_URI'],
        JWT_SECRET_KEY=config_dict['JWT_SECRET_KEY'],
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(days=1),
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
    db_engine = db.init_app(app)
    app.db_engine = db_engine
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

    @app.route('/protected', methods=['GET'])
    @jwt_required
    def protected():
        user = get_jwt_identity()
        return jsonify(loggedInUser=user)

    return app
