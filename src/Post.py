from __future__ import annotations
from typing import List, Dict, AnyStr
from bson.objectid import ObjectId
from pymongo import MongoClient, cursor, collection
from src.User import User

class Post:

    posts: collection = None

    def __init__(self, id: ObjectId, title: AnyStr, labels: List[AnyStr], author: ObjectId) -> None:
        self.id = id
        self.title = title
        self.labels = labels[:]
        self.author = author
        self.liked = False

    def matches_query(self, query_labels: List[AnyStr]) -> bool:
        matches = False
        for label in self.labels:
            for query_label in query_labels:
                if label == query_label:
                    matches = True
                    break
        return matches
    
    def get_id(self) -> ObjectId:
        return self.id
    
    def toggle_like(self) -> None:
        self.liked = not self.liked
    
    def is_liked(self) -> bool:
        return self.liked

    def get_title(self) -> AnyStr:
        return self.title
    
    def get_author(self) -> ObjectId:
        return self.author

    def get_labels(self) -> List[AnyStr]:
        return self.labels[:]
    
    def list_labels(self) -> None:
        print(self.labels)

    def fetch_posts(current_user: User, query_labels = [], max_per_page = 10) -> List[Post]:
        if len(query_labels):
            # Would rather find a way to do it with mongoDB
            to_return = []
            for post in Post.posts.find().limit(max_per_page):
                post = Post.from_BSON(post)
                if post.matches_query(query_labels):
                    to_return.append(post)
                    string_ids = [str(post) for post in current_user.posts]
                    if str(to_return[-1].get_id()) in string_ids:
                        to_return[-1].toggle_like()
            return to_return 
        to_return = []
        for post in Post.posts.find().limit(max_per_page):
                to_return.append(Post.from_BSON(post))
                string_ids = [str(post) for post in current_user.posts]
                if str(to_return[-1].get_id()) in string_ids:
                    to_return[-1].toggle_like()
        return to_return
    
    def toggle_in_current_user(post_id: ObjectId, current_user: User) -> bool:
        if not current_user.unlike_post(post_id):
            print("Found none therefore liking :P")
            current_user.like_post(post_id)
            return True
        else:
            return False

    def to_BSON(self) -> Dict:
        bson_dict = {}
        bson_dict["_id"] = self.id
        bson_dict["title"] = self.title
        bson_dict["labels"] = self.labels[:]
        bson_dict["author"] = self.author
        return bson_dict
    
    def from_BSON(bson_dict) -> Post:
        return Post(id= bson_dict["_id"],
                    title= bson_dict["title"],
                    labels= bson_dict["labels"],
                    author= bson_dict["author"])
