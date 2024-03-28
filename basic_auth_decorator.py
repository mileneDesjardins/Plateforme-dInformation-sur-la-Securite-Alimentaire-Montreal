from flask import make_response, request
from functools import wraps


def basic_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == "TODO" and auth.password == "TODO":
            return f(*args, **kwargs)
        return make_response("<H1>TODO Access denied </H1>"), 401, {
            'WWW-Authenticate': 'Basic realm="Login Required!"'}

    return decorated_function
