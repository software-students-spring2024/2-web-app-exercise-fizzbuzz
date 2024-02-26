import pymongo
from bson.objectid import ObjectId
import datetime
from dotenv import dotenv_values
from flask import Flask, render_template, request, redirect, abort, url_for, make_response, send_from_directory


# Loading development configurations
config = dotenv_values(".env")

# Make flask app
app = Flask(__name__)

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



# Still figuring this out
# @app.route('/<path:path>')
# def send_report(path):
#     return send_from_directory('public', path)

@app.route('/')
def show_home():
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
    FLASK_PORT = config["FLASK_PORT"]

    # import logging
    # logging.basicConfig(filename='/home/ak8257/error.log',level=logging.DEBUG)
    app.run(port=FLASK_PORT)
    # Run flask 
    app.run()