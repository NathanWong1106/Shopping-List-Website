from flask import Flask, redirect, render_template, request, session, flash, url_for, jsonify, make_response
from util import login_required, checkEmpty
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import json
import hashlib
import datetime
import os

# Check for negative numbers you stupid idiot

#setup
app = Flask(__name__)
app.secret_key = os.urandom(24)

#connect db
db = sqlite3.connect('./databases/app.db', check_same_thread=False)

# BASIC ROUTES, REGISTER, LOGIN, lOGOUT ------------------------------------------------------------------------------------------------
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

# LIST ROUTES ------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/lists')
@login_required
def lists():
    lists = db.execute("SELECT * FROM lists WHERE user_id = ?", [session['user_id']])
    lists = lists.fetchall()
    return render_template('lists.html', lists=lists)

@app.route('/lists/<listID>')
@login_required
def list(listID):
    ingredients = db.execute("SELECT * FROM ingredients JOIN 'lists-ingredients-relations' ON ingredients.id = 'lists-ingredients-relations'.ingredient_id WHERE list_id = ?", [listID]).fetchall()
    listName = db.execute('SELECT * FROM lists WHERE id = ?', [listID]).fetchall()[0][2]
    return render_template('groceryList.html', ingredients=ingredients, listID = listID, listName = listName)

@app.route('/lists/<listID>/<ingredientID>/<checked>')
@login_required
def listCheck(listID, ingredientID, checked):
    if checked == '0':
        db.execute("UPDATE 'lists-ingredients-relations' SET checked = 1 WHERE list_id = ? AND ingredient_id = ?", [listID, ingredientID])
    else:
        db.execute("UPDATE 'lists-ingredients-relations' SET checked = 0 WHERE list_id = ? AND ingredient_id = ?", [listID, ingredientID])

    db.commit()
    return redirect(f'/lists/{listID}')

@app.route('/lists/create', methods=["POST"])
@login_required
def createlist():
    name = request.form['name']
    try:
        listCheck = db.execute('SELECT * FROM lists WHERE user_id = ? AND name = ?', [session['user_id'], name]).fetchall()

        if len(listCheck) != 0:
            return make_response(jsonify(
                status = 406,
                message = "You already have a list of the same name"
            ))

        db.execute("INSERT INTO lists ('user_id', 'name', 'time_created') VALUES (?,?,?)", [session['user_id'], name, datetime.datetime.now().strftime("%x")])
        db.commit()
        return make_response(jsonify(
            status=200
        ))
    except:
        return make_response(jsonify(
            status = 500,
            message = '500 - Internal Server Error: Name could not be changed'
        ))

@app.route('/lists/delete', methods=["POST"])
@login_required
def deleteList():
    listID = request.form['id']

    try:
        db.execute("DELETE FROM lists WHERE id = ?", [listID])
        db.execute("DELETE FROM 'lists-ingredients-relations' WHERE list_id = ?", [listID])
        db.commit()
        return redirect("/lists")
    except:
        return make_response(jsonify(
            status = 500,
            message = '500 - Internal Server Error: List could not be deleted'
        ))

@app.route('/lists/edit/<listID>', methods=["GET"])
@login_required
def editList(listID):
    lists = db.execute('SELECT * FROM lists WHERE id = ?', [listID]).fetchall()
    ingredients = db.execute("SELECT * FROM ingredients JOIN 'lists-ingredients-relations' ON ingredients.id = 'lists-ingredients-relations'.ingredient_id WHERE list_id = ?", [listID]).fetchall()
    recipes = db.execute('SELECT * FROM recipes WHERE user_id = ? ORDER BY name', [session['user_id']]).fetchall()

    return render_template('listEdit.html', recipes=recipes, list=lists, ingredients=ingredients)

@app.route('/lists/edit/name', methods=["POST"])
@login_required
def editListName():
    try:
        listID = request.form['listID']
        name = request.form['name']

        if len(db.execute('SELECT * FROM lists WHERE name = ? AND user_id = ?', [name, session['user_id']]).fetchall()) != 0:
            return make_response(jsonify(
                status = 406,
                message = 'You already have a list of the same name'
            ))
        
        db.execute('UPDATE lists SET name = ? WHERE id = ?', [name, listID])
        db.commit()

        return make_response(jsonify(
            status = 200,
            message = 'List name changed'
        ))

    except:
        return make_response(jsonify(
            status = 500,
            message = '500 - Internal Server Error: List could not be modified'
        ))

@app.route('/lists/edit/add', methods=["POST"])
@login_required
def addListIngredient():
    try:
        ingredientName = request.form['name']
        listID = request.form['listID']
        
        #check if ingredient already exists --if not, add it to the ingredients table and assign it a unique id
        ingredientCheck = db.execute('SELECT * FROM ingredients WHERE name = ?', [ingredientName])
        if len(ingredientCheck.fetchall()) != 1:
            db.execute("INSERT INTO ingredients ('name') VALUES (?)", [ingredientName])
            db.commit()
        else:
            ingredientID = db.execute('SELECT id FROM ingredients WHERE name = ?', [ingredientName]).fetchall()[0][0]
            ingredientCheck = db.execute("SELECT * FROM 'lists-ingredients-relations' WHERE list_id = ? AND ingredient_id = ?", [listID, ingredientID])

            if len(ingredientCheck.fetchall()) >= 1:
                return make_response(jsonify(
                    status = 406,
                    message = "There is already an ingredient in this list called " + ingredientName
                ))

        #insert into the lists-ingredients relational list
        db.execute("INSERT INTO 'lists-ingredients-relations' (list_id, ingredient_id, quantity) VALUES (?, ?, ?)",
        [listID, db.execute('SELECT id FROM ingredients WHERE name = ?', [ingredientName]).fetchall()[0][0], request.form['quantity']])
        db.commit()

        return make_response(jsonify(
            status = 200
        ))
    except:
        return make_response(jsonify(
            status = 500,
            message = '500 - Internal Server Error: List could not be modified'
        ))

@app.route('/lists/edit/remove', methods=["POST"])
@login_required
def removeListIngredient():
    try:
        ingredientID = request.form['ingredientID']
        listID = request.form['listID']

        db.execute("DELETE FROM 'lists-ingredients-relations' WHERE list_id = ? AND ingredient_id = ?", [listID, ingredientID])
        db.commit()

        return make_response(jsonify(
            status = 200
        ))
    except:
        return make_response(jsonify(
            status = 500,
            message = '500 - Internal Server Error: List could not be modified'
        ))

@app.route('/lists/edit/add/recipes', methods=["POST"])
@login_required
def addRecipeList():
    try:
        listID = request.form['listID']
        recipeName = request.form['recipeName']
        recipeID = db.execute('SELECT * FROM recipes WHERE user_id = ? AND name = ?', [session['user_id'], recipeName]).fetchall()[0][0]
        recipeIngredients = db.execute("SELECT * FROM 'recipe-ingredients-list' WHERE recipe_id = ?", [recipeID]).fetchall()

        for ingredient in recipeIngredients:
            ingredientCheck = db.execute("SELECT * FROM 'lists-ingredients-relations' WHERE list_id = ? AND ingredient_id = ?", [listID, ingredient[1]]).fetchall()

            if len(ingredientCheck) != 0:
                db.execute("UPDATE 'lists-ingredients-relations' SET quantity = quantity + ? WHERE list_id = ? AND ingredient_id = ?",[ingredient[2], listID, ingredient[1]])
            else:
                db.execute("INSERT INTO 'lists-ingredients-relations' (list_id, ingredient_id, quantity) VALUES (?,?,?)", [listID, ingredient[1], ingredient[2]])
        
        db.commit()
        return make_response(jsonify(
            status = 200,
            message = f'{recipeName} added to the list'
        ))
    except:
        return make_response(jsonify(
            status = 500,
            message = '500 - Internal Server Error: List could not be modified'
        ))

@app.route('/lists/edit/quantity', methods=["POST"])
@login_required
def updateListQuantity():
    try:
        listID = request.form['listID']
        quantity = request.form['quantity']
        ingredientID = request.form['ingredientID']

        db.execute("UPDATE 'lists-ingredients-relations' SET quantity = ? WHERE list_id = ? AND ingredient_id = ?", [quantity, listID, ingredientID])
        db.commit()

        return make_response(jsonify(
            status = 200,
            message = "List Updated"
        ))
    except:
        return make_response(jsonify(
            status = 500,
            message = "500 - Internal Server Error: List could not be modified"
        ))

# RECIPE ROUTES -------------------------------------------------------------------------------------------------------------------------------------------------------------

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
    
    recipeCheck = db.execute('SELECT * FROM recipes WHERE name = ? AND user_id = ?', [request.form['name'], session['user_id']]).fetchall()

    if len(recipeCheck) != 0:
        return make_response(jsonify(
            status = 406,
            message = "You already have a recipe of the same name"
        ))
    
    db.execute('INSERT INTO recipes ("name", "user_id", "description") VALUES (?, ?, ?)',[request.form['name'], session['user_id'], request.form['description']])
    db.commit()

    return make_response(jsonify(
        status = 200
    ))

@app.route("/recipes/edit/<recipeID>", methods=["GET"])
@login_required
def editRecipe(recipeID):
    recipe = db.execute('SELECT * FROM recipes WHERE id = ?', [recipeID])
    ingredients = db.execute("SELECT * FROM ingredients JOIN 'recipe-ingredients-list' ON ingredients.id = 'recipe-ingredients-list'.ingredient_id WHERE recipe_id = ?", [recipeID])
    ingredients = ingredients.fetchall()

    return render_template('recipeEdit.html', recipe = recipe.fetchall(), ingredients = ingredients)

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
def removeRecipeIngredient():
    recipeID = request.form['recipeID']
    ingredientID = request.form['ingredientID']

    db.execute("DELETE FROM 'recipe-ingredients-list' WHERE ingredient_id = ? AND recipe_id = ?", [ingredientID, recipeID])
    db.commit()
    return redirect(f'/recipes/edit/{recipeID}')


@app.route("/recipes/edit/add", methods=["POST"])
@login_required
def addRecipeIngredient():

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
def editRecipeName():
    recipeName = request.form['name']
    recipeID = request.form['recipeID']

    try:

        if len(db.execute('SELECT * FROM recipes WHERE name = ? AND user_id = ?', [recipeName, session['user_id']]).fetchall()) != 0:
            return make_response(jsonify(
                status = 406,
                message = "You already have recipes of the same name"
            ))

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
def editRecipeDescription():
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

@app.route('/recipes/edit/quantity', methods=["POST"])
@login_required
def updateRecipeQuantity():
    try:
        recipeID = request.form['recipeID']
        quantity = request.form['quantity']
        ingredientID = request.form['ingredientID']

        db.execute("UPDATE 'recipe-ingredients-list' SET quantity = ? WHERE recipe_id = ? AND ingredient_id = ?", [quantity, recipeID, ingredientID])
        db.commit()

        return make_response(jsonify(
            status = 200,
            message = "Recipe Updated"
        ))
    except:
        return make_response(jsonify(
            status = 500,
            message = "500 - Internal Server Error: Recipe could not be modified"
        ))