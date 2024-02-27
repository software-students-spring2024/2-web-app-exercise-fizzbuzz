from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id):
        self.id = id

    def get(email, users):
        if email == None or not users.find_one({"_id" : email}):
            return None
        user = User(email)
        return user
    