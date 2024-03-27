from flask import redirect, request

from functools import wraps
from flask import session, render_template


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'id' not in session:
            print(request.path)
            return redirect("/connexion", 302)

        return f(*args, **kwargs)

    return decorated_function
