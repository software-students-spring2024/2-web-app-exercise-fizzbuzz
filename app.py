import pymongo
from bson.objectid import ObjectId
import datetime
from dotenv import dotenv_values
from flask import Flask, render_template, request, redirect, abort, url_for, session, make_response, send_from_directory
from flask_login import AnonymousUserMixin, login_required, LoginManager, login_user, current_user, logout_user
from src.User import *
from passlib.hash import pbkdf2_sha256
from src.NestedCollection import *


# Loading development configurations
config = dotenv_values(".env")

# Make flask app
app = Flask(__name__)
app.secret_key = config["FLASK_SECRET_KEY"]

# Make a connection to the database server
connection = pymongo.MongoClient("class-mongodb.cims.nyu.edu", 27017,
                                username = config["USERNAME"],
                                password = config["PASSWORD"],
                                authSource = config["AUTHSOURCE"])

# Select a specific database on the server
db = connection[config["MONGO_DBNAME"]] 

try:
    # verify the connection works by pinging the database
    connection.admin.command("ping")  # The ping command is cheap and does not require auth.
    print(" *", "Connected to MongoDB!")  # if we get here, the connection worked!
except Exception as e:
    # the ping command failed, so the connection is not available.
    print(" * MongoDB connection error:", e)  # debug


# Login manager using flask-login
login_manager = LoginManager()
login_manager.init_app(app)

SE2_DB= NestedCollection(db.nested_collections.find_one({"name": "SE_Project2"}), db)

users = SE2_DB["users"]

# projects = SE2_DB["posts"]

@login_manager.user_loader
def load_user(email):
    user = User.get(email, users)
    return user
    

@login_manager.request_loader
def request_loader(request):
    return User.get(None, users)

@app.route('/')
@login_required
def show_home():
    return render_template("index.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    print("Dakhalna")
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('logout'))
        return render_template("login.html", error_message = '')
    
    if request.method == 'POST':
        email = request.form['email']
        if users.find_one({"_id": email}) and pbkdf2_sha256.verify(request.form['password'], users.find_one({"_id": email})['password']):
            user = User(email)
            login_user(user)
            return redirect(url_for('show_home'))

    return render_template("login.html", error_message = 'Incorrect email or password')


@app.route('/protected')
@login_required
def protected():
    print(current_user.is_authenticated)
    return 'Logged in as: ' + current_user.id

@app.route('/logout')
@login_required
def logout():
    # session.clear()
    logout_user()
    print(current_user)
    return redirect(url_for('login'))


@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html", error_message = '')
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if users.find_one({"_id": email}):
            return render_template("register.html", error_message = 'Account with this email already exists')
        users.insert_one({"_id": email, "password": pbkdf2_sha256.encrypt(password)})
        user = User(email)
        login_user(user)
        return redirect(url_for('show_home'))

        

@app.route('/db_test')
def show_db_test():
    # Document to add
    doc = {
        "name": "Foo Barstein",
        "email": "fb1258@nyu.edu",
        "message": "We loved with a love that was more than love.\n -Edgar Allen Poe"
    }

    # Adding document to test collection
    db.test_collection.insert_one(doc)

    # Find and print
    found = db.test_collection.find_one({
        "name": "Foo Barstein"
    })

    # Formatting
    output = '{name} ({email}) - {message}'.format(
        name=found["name"],
        email=found["email"],
        message=found["message"]
    )

    print(output)

    # Deleting everything
    db.test_collection.delete_many({
        "email": "fb1258@nyu.edu"
    })
    response = make_response(output, 200) # put together an HTTP response with success code 200
    response.mimetype = "text/plain" # set the HTTP Content-type header to inform the browser that the returned document is plain text, not HTML
    return response # the return value is sent as the response to the web browser


if __name__ == '__main__': 
    # use the PORT environment variable
    
    # import logging
    # logging.basicConfig(filename='/home/ak8257/error.log',level=logging.DEBUG)
    print(config["FLASK_PORT"])
    app.run(port=config["FLASK_PORT"])