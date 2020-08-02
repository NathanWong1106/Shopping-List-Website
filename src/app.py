from flask import Flask, redirect, render_template, request, session, flash, url_for, jsonify, make_response
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
def index():
    if 'user_id' not in session:
        return render_template('initial.html')
    else:
        return render_template('home.html')

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
        return redirect('/')

@app.route('/logout')
@login_required
def logout():
    #clear session dict --forget user_id
    session.clear()
    #return user to introduction page
    return redirect('/')

@app.route('/lists', methods=["POST", "GET"])
@login_required
def list():
    return "list"

@app.route("/recipes")
@login_required
def recipes():
    recipes = db.execute('SELECT * FROM recipes WHERE user_id = ?',[session['user_id']])
    db.commit()
    return render_template('recipes.html', recipes=recipes.fetchall())

# called through ajax/jquery in /recipes
@app.route("/recipes/create", methods=["POST"])
@login_required
def createRecipe():
    if not checkEmpty([request.form['name'], request.form['description']]):
        flash('One or more fields where left empty')
        return redirect('/recipes')
    
    db.execute('INSERT INTO recipes ("name", "user_id", "description") VALUES (?, ?, ?)',[request.form['name'], session['user_id'], request.form['description']])
    db.commit()
    
    flash('Recipe Created')
    return redirect('/recipes')

@app.route("/recipes/edit/<recipeID>", methods=["GET"])
@login_required
def editRecipe(recipeID):
    recipe = db.execute('SELECT * FROM recipes WHERE id = ?', [recipeID])
    ingredients = db.execute("SELECT * FROM ingredients JOIN 'recipe-ingredients-list' ON ingredients.id = 'recipe-ingredients-list'.ingredient_id WHERE recipe_id = ?", [recipeID])
    ingredients = ingredients.fetchall()

    return render_template('edit.html', recipe = recipe.fetchall(), ingredients = ingredients)

@app.route("/recipes/delete", methods=["POST"])
@login_required
def deleteRecipe():
    db.execute('DELETE FROM recipes WHERE id = ?', [request.form.get('id')])
    db.execute("DELETE FROM 'recipe-ingredients-list' WHERE recipe_id = ?", [request.form.get('id')])
    db.commit()

    flash('Recipe Deleted')
    return redirect('/recipes')

@app.route("/recipes/edit/remove", methods=["POST"])
@login_required
def removeIngredient():
    recipeID = request.form['recipeID']
    ingredientID = request.form['ingredientID']

    db.execute("DELETE FROM 'recipe-ingredients-list' WHERE ingredient_id = ? AND recipe_id = ?", [ingredientID, recipeID])
    db.commit()
    return redirect(f'/recipes/edit/{recipeID}')


@app.route("/recipes/edit/add", methods=["POST"])
@login_required
def addIngredient():

    ingredientName = request.form['name']
    recipeID = request.form['recipeID']
    
    #check if ingredient already exists --if not, add it to the ingredients table and assign it a unique id
    ingredientCheck = db.execute('SELECT * FROM ingredients WHERE name = ?', [ingredientName])
    if len(ingredientCheck.fetchall()) != 1:
        db.execute("INSERT INTO ingredients ('name') VALUES (?)", [ingredientName])
        db.commit()
    else:
        ingredientID = db.execute('SELECT id FROM ingredients WHERE name = ?', [ingredientName]).fetchall()[0][0]
        ingredientCheck = db.execute("SELECT * FROM 'recipe-ingredients-list' WHERE recipe_id = ? AND ingredient_id = ?", [recipeID, ingredientID])

        if len(ingredientCheck.fetchall()) >= 1:
            return make_response(jsonify(
                status = 406,
                message = "There is already an ingredient in this recipe called " + ingredientName
            ))

    #insert into the recipes-ingredients relational list
    db.execute("INSERT INTO 'recipe-ingredients-list' (recipe_id, ingredient_id, quantity) VALUES (?, ?, ?)",
    [recipeID, db.execute('SELECT id FROM ingredients WHERE name = ?', [ingredientName]).fetchall()[0][0], request.form['quantity']])
    db.commit()

    # row order --> 0: user_id, 1: ingredient_name, 2: recipe_id, 3: ingredient_id, 4: ingredient_quantity

    return make_response(jsonify(
        status = 200
    ))

@app.route("/recipes/edit/name", methods=["POST"])
@login_required
def editName():
    recipeName = request.form['name']
    recipeID = request.form['recipeID']

    try:
        db.execute("UPDATE recipes SET 'name' = ? WHERE id = ?", [recipeName, recipeID])
        db.commit()

        return make_response(jsonify(
            status = 200,
            message = "Name successfully changed to " + recipeName
        ))

    except:
        return make_response(jsonify(
            status = 500,
            message = "500 - Internal Server Error: Name could not be changed"
        ))

@app.route("/recipes/edit/description", methods=["POST"])
@login_required
def editDescription():
    description = request.form['description']
    recipeID = request.form['recipeID']

    try:
        db.execute("UPDATE recipes SET 'description' = ? WHERE id = ?", [description, recipeID])
        db.commit()

        return make_response(jsonify(
            status = 200,
            message = "Description successfully changed"
        ))

    except:
        return make_response(jsonify(
            status = 500,
            message = "500 - Internal Server Error: Description could not be changed"
        ))