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

class BadRequest(GenericError):
    def __init__(self, message=None, payload=None):
        if message is None:
            message = 'Bad request'
        GenericError.__init__(self, message=message, payload=payload, code=400)

class Forbidden(GenericError):
    def __init__(self, message=None, payload=None):
        if message is None:
            message = 'Forbidden'
        GenericError.__init__(self, message=message, payload=payload, code=403)

class NotFound(GenericError):
    def __init__(self, message=None, payload=None):
        if message is None:
            message = 'Not found'
        GenericError.__init__(self, message=message, payload=payload, code=404)
