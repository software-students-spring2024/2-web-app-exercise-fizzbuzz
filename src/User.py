from __future__ import annotations
from flask_login import UserMixin
from typing import List, Dict, AnyStr, Union
from bson.objectid import ObjectId
from pymongo import MongoClient, cursor, collection
from passlib.hash import pbkdf2_sha256


class User(UserMixin):
    users : collection = None

    def __init__(self, email: AnyStr, username: AnyStr, password: AnyStr, measurements: Dict = {'height':'?','weight':'?','pants':'?','shirt':'?','shoe':'?'}, posts: List[ObjectId] = [], friends: List = [], id: ObjectId = None) -> None:
        self.email = email.lower()
        self.username = username
        self.measurements = measurements
        self.posts = posts[:]
        self.friends = friends[:]
        if id:
            self.id = id
            self.password = password # Already encrypted
        else:
            self.password = pbkdf2_sha256.encrypt(password) # Encrypt before storing
            User.users.insert_one(self.to_BSON())
            self.id = User.users.find_one({'email': self.email})['_id']   
        super().__init__()

    def update_db(self):
        User.users.replace_one({'_id': self.id}, self.to_BSON())

    def like_post(self, post_id: ObjectId) -> None:
        self.posts.append(post_id)
        self.update_db()

    def unlike_post(self, post_id: ObjectId) -> bool:
        for i in range(len(self.posts)):
            if str(post_id) == str(self.posts[i]):
                print("Found at ", i)
                self.posts.pop(i)
                self.update_db()
                return True
        print("None found")
        return False

    def get_id(self):
        return str(self.id)
    
    def to_BSON(self) -> Dict:
        bson_dict = {}
        if hasattr(self, 'id'):
            bson_dict["_id"] = self.id
        bson_dict["email"] = self.email
        bson_dict["username"] = self.username
        bson_dict["password"] = self.password
        bson_dict["measurements"] = self.measurements
        bson_dict["posts"] = self.posts[:]
        bson_dict["friends"] = self.friends[:]
        return bson_dict
    
    def from_BSON(bson_dict: Dict) -> User:
        if not bson_dict:
            return None
        return User(email= bson_dict["email"],
                    username= bson_dict["username"],
                    password= bson_dict["password"],
                    measurements= bson_dict["measurements"],
                    posts= bson_dict["posts"],
                    friends= bson_dict["friends"],
                    id= bson_dict["_id"])
    
    def already_exists(email = "", username = ""):
        if email == "" and username == "":
            return True
        return User.users.find_one({'email': email.lower()}) or User.users.find_one({'username': username})
    
    def get(id: ObjectId) -> Union[User, None]:
        user = User.from_BSON(User.users.find_one({"_id" : ObjectId(id)}))
        if not user:
            user = None
        return user
    
    def __repr__(self) -> AnyStr:
        return "ID: " + str(self.id) + " - Email: " + self.email
    
    def login(username_email: AnyStr, password: AnyStr) -> Union[User, None]:
        user = User.from_BSON(User.users.find_one({"email" : username_email.lower()}))
        if not user:
            user = User.from_BSON(User.users.find_one({"username" : username_email}))
        if not user:
            user = None
        if user:
            if not pbkdf2_sha256.verify(password, user.password):
                user = None
        return user

    def get_username(username) -> Union[User, None]:
        user = User.from_BSON(User.users.find_one({"username": username}))
        if not user:
            user = None
        return user

    def update_sizes(user, form_data):
        user.measurements['height'] = form_data.get('height')
        user.measurements['weight'] = form_data.get('weight')
        user.measurements['shoe'] = form_data.get('shoe')
        user.measurements['shirt'] = form_data.get('shirt')
        user.measurements['pants'] = form_data.get('pants')

        user.update_db()
        return

    def delete_profile(user):
        filter_criteria={"username":user.username}
        User.users.delete_one(filter_criteria)
        return
