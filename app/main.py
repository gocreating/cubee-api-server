import os
import yaml

from datetime import timedelta
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from app import db
from app.routes import main, auth, user

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
    app.jwt = jwt

    ################
    ## Setup CORS ##
    ################
    CORS(app, supports_credentials=True)

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
    app.register_blueprint(main.bp)
    auth.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(user.bp)

    return app
