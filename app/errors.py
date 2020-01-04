from flask import jsonify

class GenericError(Exception):
    code = 500
    message = 'Something wrong happened'

    def __init__(self, message=None, code=None, payload=None):
        Exception.__init__(self)

        if message is not None:
            self.message = str(message)
        if code is not None:
            self.code = code
        self.payload = payload

    def to_response(self):
        return jsonify(code=self.code, data={
            'message': self.message,
        }), self.code
