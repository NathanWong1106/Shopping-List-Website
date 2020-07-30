from functools import wraps
from flask import g, request, redirect, url_for, session, flash

#decorated function to check if user is logged in or not
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get("user_id") is None:
            flash("You need to login first")
            return redirect('/login')
        else:
            return f(*args, **kwargs)
    return wrap

#function to check if user input is empty
def checkEmpty(argInput):

    #check through all arguments
    for userInput in argInput:
        if not userInput:
            return False
    
    return True