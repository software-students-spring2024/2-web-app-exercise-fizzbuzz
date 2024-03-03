import pymongo
from bson.objectid import ObjectId
import datetime
from dotenv import dotenv_values
from flask import Flask, render_template, request, redirect, abort, url_for, session, make_response, send_from_directory
from flask_login import AnonymousUserMixin, login_required, LoginManager, login_user, current_user, logout_user
from src.User import *
from passlib.hash import pbkdf2_sha256
from src.NestedCollection import *
from src.Post import *


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

if (not db.nested_collections.find_one({"name": "SE_Project2"})):
    db.nested_collections.insert({"name": "SE_Project2", "children": []})
SE2_DB= NestedCollection("SE_Project2", db)

if "users" not in SE2_DB:
    SE2_DB.add_collection("users", "SE_PROJECT2_users")
users = SE2_DB["users"]

if "posts" not in SE2_DB:
    SE2_DB.add_collection("posts", "SE_PROJECT2_posts")
posts = SE2_DB["posts"]

# To be replaced with fetching from database
all_posts = [Post(ObjectId(), "Post 1", ['happy', 'joy', 'excited'], ObjectId()),
                Post(ObjectId(), "Post 2", ['sad', 'upset', 'unhappy'], ObjectId()), 
                Post(ObjectId(), "Post 3", ['happy', 'calm', 'relaxation'], ObjectId()), 
                Post(ObjectId(), "Post 4", ['upset', 'depressed'], ObjectId()),
                Post(ObjectId(), "Post 5", ['dance', 'party', 'joy'], ObjectId()),
                Post(ObjectId(), "Post 6", ['happy', 'glad'], ObjectId()),
                Post(ObjectId(), "Post 7", ['book', 'library'], ObjectId()),
                Post(ObjectId(), "Post 8", ['rage', 'anger', 'upset'], ObjectId()),]

if "chats" not in SE2_DB:
    SE2_DB.add_collection("chats", "SE_PROJECT2_chats")
chats = SE2_DB["chats"]


# Signing up and logging in

@login_manager.user_loader
def load_user(email):
    user = User.get(email, users)
    return user
    
@login_manager.request_loader
def request_loader(request):
    return User.get(None, users)

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('logout'))
        return render_template("login.html", error_message = '')
    
    if request.method == 'POST':
        email = request.form['email']
        if users.find_one({"_id": email}) and pbkdf2_sha256.verify(request.form['password'], users.find_one({"_id": email})['password']):
            user = User(email)
            login_user(user)
            return redirect(url_for('home'))

    return render_template("login.html", error_message = 'Incorrect email or password')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# Main Pages

@app.route('/')
@login_required
def show():
    return redirect(url_for('home'))

@app.route('/home', methods=["GET", "POST"])
@login_required
def home():
    if request.method == "POST":
        for i in range(len(all_posts)):
            if str(all_posts[i].get_id()) == request.form.get('post_id'):
                all_posts[i].toggle_like()
                return redirect(url_for("home"))
        return redirect(url_for("home"))
            
    # request.method = "GET"
    posts = []
    if (request.query_string != b'' and request.args.get('query') != ''):
        query_labels = [label.strip() for label in request.args.get('query').split(' ')]
        print(query_labels)
        posts = [post for post in all_posts if post.matches_query(query_labels) ]
    else:
        posts = all_posts[:4]
        print("No queries received")
    return render_template("home.html", query_type="posts", posts = posts)

@app.route('/gift')
@login_required
def gift():
    return "Page not available yet"

@app.route('/profile')
@login_required
def profile():
    return "Page not available yet"

if __name__ == '__main__': 
    # use the PORT environment variable
    
    # import logging
    # logging.basicConfig(filename='/home/ak8257/error.log',level=logging.DEBUG)
    print(config["FLASK_PORT"])
    app.run(port=config["FLASK_PORT"])