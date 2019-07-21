import os
from flask import Flask, Blueprint, jsonify

app = Flask(__name__, subdomain_matching=True)
app.config['SERVER_NAME'] = 'cubee.cc'

#########
## App ##
#########
@app.route('/')
def app_index():
    return 'app index'

#########
## API ##
#########
api = Blueprint('api', __name__, subdomain='api')
@api.route('/')
def api_index():
    return 'Welcome to Cubee API Server'

@api.route('/hello')
def api_hello():
    return jsonify(
        hello='world',
        num=777,
    )

@api.route('/version')
def api_version():
    try:
        return jsonify(
            APP_COMMIT_REF=os.environ['APP_COMMIT_REF'],
            APP_BUILD_DATE=os.environ['APP_BUILD_DATE'],
        )
    except:
        return 'unknown'

app.register_blueprint(api)

#############
## Dynamic ##
#############
@app.route('/test', subdomain="<username>")
def username_test(username):
    return 'Hi, {0}'.format(username)

@app.route('/', subdomain="<username>")
def username_index(username):
    return 'Fuck, {0}'.format(username)

if __name__ == '__main__':
    app.run()
