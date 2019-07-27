import os
import yaml

from flask import Flask, jsonify

is_prod = not 'CONFIG_PATH' in os.environ

def get_config():
    config_dict = yaml.safe_load(open(
        '/etc/config.yaml' if is_prod else os.path.join(os.path.dirname(__file__), '..', os.environ['CONFIG_PATH'])
    ))
    return config_dict

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

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
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route('/config')
    def config():
        return jsonify(config_dict)

    @app.route('/')
    def index():
        return 'Yo, this is cubee.cc'

    return app
