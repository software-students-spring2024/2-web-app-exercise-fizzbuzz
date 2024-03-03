from typing import List, Dict, AnyStr
from bson.objectid import ObjectId

class Post:
    def __init__(self, id: ObjectId, title: AnyStr, labels: List[AnyStr], author: ObjectId) -> None:
        self.id = id
        self.title = title
        self.labels = labels[:]
        self.author = author

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

    def get_title(self) -> AnyStr:
        return self.title
    
    def get_author(self) -> ObjectId:
        return self.author

    def get_labels(self) -> List[AnyStr]:
        return self.labels[:]
    
    def list_labels(self) -> None:
        print(self.labels)

    def to_BSON(self) -> Dict:
        bson_dict = {}
        bson_dict["_id"] = self.id
        bson_dict["title"] = self.title
        bson_dict["labels"] = self.labels[:]
        bson_dict["author"] = self.author
