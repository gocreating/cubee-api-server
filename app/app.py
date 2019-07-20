import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return 'Welcome to Cubee API Server'

@app.route('/hello')
def hello():
    return jsonify(
        hello='world',
        num=777,
    )

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
    app.run(host='0.0.0.0')
