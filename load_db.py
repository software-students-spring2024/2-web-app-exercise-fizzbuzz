import pymongo
from dotenv import dotenv_values


# Loading development configurations
config = dotenv_values(".env")

# Make a connection to the database server
connection = pymongo.MongoClient("class-mongodb.cims.nyu.edu", 27017,
                                username = config["USERNAME"],
                                password = config["PASSWORD"],
                                authSource = config["AUTHSOURCE"])

# Select a specific database on the server
db = connection[config["MONGO_DBNAME"]] 