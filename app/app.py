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

if __name__ == '__main__':
    app.run(host='0.0.0.0')
