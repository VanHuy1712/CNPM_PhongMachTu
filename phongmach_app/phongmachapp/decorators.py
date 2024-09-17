from functools import wraps
from flask import session, request, redirect, url_for
from flask_login import current_user
from phongmachapp.models import VaiTroNguoiDung



def loggedin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('index', next=request.url))

        return f(*args, **kwargs)

    return decorated_function


def not_loggedin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('index', next=request.url))

        return f(*args, **kwargs)

    return decorated_function


def thuNgan_loggedin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.vaiTro_NguoiDung != VaiTroNguoiDung.ThuNgan:
            return redirect(url_for('index', next=request.url))

        return f(*args, **kwargs)

    return decorated_function