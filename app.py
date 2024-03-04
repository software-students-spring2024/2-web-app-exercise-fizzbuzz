import pymongo
from bson.objectid import ObjectId
import datetime
from dotenv import dotenv_values
from flask import Flask, render_template, request, redirect, abort, url_for, session, make_response, send_from_directory
from flask_login import AnonymousUserMixin, login_required, LoginManager, login_user, current_user, logout_user
from src.User import *
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
User.users = SE2_DB["users"]

if "posts" not in SE2_DB:
    SE2_DB.add_collection("posts", "SE_PROJECT2_posts")
Post.posts = SE2_DB["posts"]

if "chats" not in SE2_DB:
    SE2_DB.add_collection("chats", "SE_PROJECT2_chats")
chats = SE2_DB["chats"]


# Signing up and logging in

@login_manager.user_loader
def load_user(id):
    user = User.get(id)
    return user
    
@login_manager.request_loader
def request_loader(request):
    return User.get(None)

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html", error_message = '')
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if User.already_exists(username = username):
            return render_template("register.html", error_message = 'Account with this username already exists')
        if User.already_exists(email = email):
            return render_template("register.html", error_message = 'Account with this email already exists')
        if password != confirm_password:
            return render_template("register.html", error_message = "Passwords don't match")
        user = User(username=username, email=email, password=password)
        login_user(user)
        return redirect(url_for('home'))

@app.route("/profile/<string:username>", methods=['GET'])
def show_profile(username):
    user = User.get_username(username)
    if(user == None):
        # give page that says user not found
        return render_template("user_not_found.html")
    elif(current_user.username == username):
        friends_size = len(user.friends)
        bookmarks_size = len(user.posts)
        
        return render_template("profile.html", user=user, friends_size=friends_size, bookmarks_size = bookmarks_size)
    else:
        friend=False
        for possible_friend in current_user.friends:
            document_possible_friend = User.users.find_one({'_id': possible_friend})
            if document_possible_friend['username']==username:
                friend=True
                break
        if(friend == True):
            # give page that says user is friend 
            return render_template("profile_is_friend.html")
        else:
            # give page that says user is not friend 
            return render_template("profile_is_not_friend.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('logout'))
        return render_template("login.html", error_message = '')
    
    if request.method == 'POST':
        username_email = request.form['username_email']
        password = request.form['password']
        user = User.login(username_email, password)
        if user:
            login_user(user)
            return redirect(url_for('home'))

    return render_template("login.html", error_message = 'Incorrect email or password')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    if 'query' in session:
        session.pop('query')
    return redirect(url_for('login'))


# Main Pages

@app.route('/')
@login_required
def show():
    return redirect(url_for('home'))

@app.route('/home', methods=["GET", "POST"])
@login_required
def home(query= None):
    if request.method == "POST":
        if request.form.get('post_id'):
            Post.toggle_in_current_user(request.form.get('post_id'), current_user)
            return redirect(url_for("home", query= session['query'] if 'query' in session else None))
            
    # request.method = "GET"
    query = request.args.get('query') if (request.query_string != b'') else query if query else None
    if query == '':
        session['query'] = query
        query = None
    query_labels = []
    if query is not None:
        session['query'] = query
        query_labels = [label.strip() for label in query.split(' ')]
    posts = Post.fetch_posts(current_user= current_user, query_labels= query_labels)
    return render_template("home.html", query_type="posts", posts = posts, action= '/home/upload', button_text= 'Upload')

@app.route('/home/upload', methods=["GET", "POST"])
@login_required
def upload_post():
    if request.method == "POST":
        title = request.form.get("title")
        labels = [label.strip() for label in request.form.get("labels").split()]
        Post.upload_new_post(current_user, title, labels)
        return redirect(url_for("home"))

    return render_template("upload_post.html", action= '/home/upload', button_text= 'Upload')


@app.route('/gift')
@login_required
def gift():
    return "Page not available yet"

@app.route('/profile')
@login_required
def profile():
    return redirect('profile/'+current_user.username)


if __name__ == '__main__': 
    # use the PORT environment variable
    
    # import logging
    # logging.basicConfig(filename='/home/ak8257/error.log',level=logging.DEBUG)
    app.run(port=config["FLASK_PORT"])