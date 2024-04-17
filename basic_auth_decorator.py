from flask import make_response, request, current_app
from functools import wraps


def basic_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization
        if (auth and auth.username == current_app.config["SITE_USER"] and
                auth.password == current_app.config["SITE_PASS"]):
            return f(*args, **kwargs)
        return make_response("<H1>Access denied </H1>"), 401, {
            'WWW-Authenticate': 'Basic realm="Login Required!"'}

    return decorated_function
