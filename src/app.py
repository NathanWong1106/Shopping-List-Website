from flask import Flask, redirect, render_template, request, session, flash
from util import login_required, checkEmpty
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import json
import hashlib
import datetime
import os

#setup
app = Flask(__name__)
app.secret_key = os.urandom(24)

#connect db
db = sqlite3.connect('./databases/app.db', check_same_thread=False)

@app.route("/")
@login_required
def index():
    return "index"

@app.route("/register", methods=["POST", "GET"])
def register():

    #check request method
    if request.method == "GET":
        return render_template("register.html")
    else:
        #check if input fields are empty
        if not checkEmpty([request.form.get("username"), request.form.get("password")]):
            flash("One or more input fields where left empty")
            return redirect('/register')
        
        username = request.form.get("username")
        password = request.form.get("password")

        #check if the username is unique
        checkDuplicates = db.execute('SELECT * FROM users WHERE username=?', [username])
        if len(checkDuplicates.fetchall()) != 0:
            flash("Username already taken")
            return redirect('/register')
        
        #insert into users and commit changes
        db.execute('INSERT INTO users (username, password_hash) VALUES (?,?)', [username, generate_password_hash(password)])
        db.commit()
        flash('Account Created!')
        return redirect('/login')

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        #check if input fields are empty
        if not checkEmpty([request.form.get("username"), request.form.get("password")]):
            flash("One or more input fields where left empty")
            return redirect('/login')
        
        username = request.form.get("username")
        password = request.form.get("password")

        checkDB = db.execute('SELECT * FROM users WHERE username = ?', [username])
        results = checkDB.fetchall()

        if len(results) != 1:
            flash("User not found")
            return redirect("/login")

        if not check_password_hash(results[0][2], password):
            flash("Incorrect password")
            return redirect("/login")
        
        #remember which user has logged in
        session['user_id'] = results[0][0]

        #redirect user to homepage
        flash("Logged In!")
        print(session['user_id'])
        return redirect('/')

@app.route('/list', methods=["POST", "GET"])
@login_required
def list():
    return "list"

@app.route("/recipes", methods=["POST", "GET"])
@login_required
def recipes():
    return "recipes"