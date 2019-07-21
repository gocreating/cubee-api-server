import os
from flask import Flask, jsonify

app = Flask(__name__)
app.config['SERVER_NAME'] = 'cubee.cc'

@app.route('/')
def index():
    return 'Welcome to Cubee API Server'

@app.route('/hello')
def hello():
    return jsonify(
        hello='world',
        num=777,
    )

@app.route('/test', subdomain="<username>")
def username_test(username):
    return 'Hi, {0}'.format(username)

@app.route('/', subdomain="<username>")
def username_index(username):
    return 'Fuck, {0}'.format(username)

@app.route('/version')
def version():
    try:
        return jsonify(
            APP_COMMIT_REF=os.environ['APP_COMMIT_REF'],
            APP_BUILD_DATE=os.environ['APP_BUILD_DATE'],
        )
    except:
        return 'unknown'

if __name__ == '__main__':
    app.run()
