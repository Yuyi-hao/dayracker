from functools import wraps
from flask import session, redirect

def login_required(func):
    @wraps(func)
    def decorate_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/auth/login")
        return func(*args, **kwargs)
    return decorate_function