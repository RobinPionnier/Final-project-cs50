from functools import wraps


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def check_pw(pw):
    length = len(pw)
    lowercase = 0
    uppercase = 0
    number = 0
    for letter in pw:
        if letter.isupper():
            uppercase += 1
        elif letter.islower():
            lowercase += 1
        elif letter.isnumeric():
            number += 1
    if length < 8 or lowercase == 0 or uppercase == 0 or number == 0:
        return False
    else:
        return True
