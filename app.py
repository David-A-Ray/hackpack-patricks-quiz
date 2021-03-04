import os
from flask import (
    Flask, flash, render_template, 
    redirect, request, session, url_for)
from flask_pymongo import PyMongo, pymongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

users = mongo.db.users.find()

@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html", users=users)

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        existing_email = mongo.db.users.find_one(
                    {"email": request.form.get("email").lower()})
        existing_username = mongo.db.users.find_one(
                        {"username": request.form.get("username").lower()})

        if existing_email:
            flash("Email is already registered.")
            return redirect(url_for('register'))

        if existing_username:
            flash("Username is already in use, please choose a different one.")
            return redirect(url_for('register'))

        password1 = request.form.get("password")
        password2 = request.form.get("password-confirmation")

        if password1 != password2:
            flash("Passwords do not match, please try again.")
            return redirect(url_for('register'))

        register_user = {
        "username": request.form.get("username").lower(),
        "email": request.form.get("email").lower(),
        "password": generate_password_hash(request.form.get("password")),
        "points": None
        }

        mongo.db.users.insert_one(register_user)

        session["user"] = request.form.get("username").lower()
        flash("Registration successful Welcome to the pub quiz!")
        username = session["user"]

    return render_template("registration.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form.get("email").lower()
        password = request.form.get("password")

        existing_user = mongo.db.users.find_one(
        {"email": email})

        if existing_user:
            if check_password_hash(
                    existing_user["password"], password):
                username = existing_user["username"]
                session["user"] = username
                flash(f"Welcome, {username}!")
                return redirect(url_for("home"))
            else:
                flash("Incorrect username and/or password!")
                return redirect(url_for("login"))
        else:
            flash("Incorrect username and/or password!")
            return redirect(url_for("login"))

    return render_template("login.html")

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
    port=int(os.environ.get("PORT")),
    debug=True)
