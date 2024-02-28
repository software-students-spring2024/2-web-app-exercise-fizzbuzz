from pymongo import MongoClient, cursor, collection
from typing import List, Dict

class NestedCollection:
    def __init__(self, config: Dict, root_db: MongoClient) -> None:
        self.root_db = root_db
        self.dict = {}
        for collection in config["children"]:
            # collection[0] : pseudonym - collection[1] : collection name
            self.dict[collection[0]] = collection[1]

    def __getitem__(self, pseudonym) -> collection:
        return self.root_db.get_collection(self.dict[pseudonym])
        
    
            
