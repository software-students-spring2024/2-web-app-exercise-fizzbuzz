from pymongo import MongoClient, cursor, collection
from typing import List, Dict, AnyStr

class NestedCollection:
    def __init__(self, name: AnyStr, root_db: MongoClient) -> None:
        self.root_db = root_db
        self.name = name
        self.config = self.root_db.nested_collections.find_one({"name": name})
        self.dict = {}
        for collection in self.config["children"]:
            # collection[0] : pseudonym - collection[1] : collection name
            self.dict[collection[0]] = collection[1]

    def name_from_pseudonym(self, pseudonym: AnyStr) -> AnyStr:
        return self.dict[pseudonym]

    def list_collections(self) -> None:
        print(self.config["children"])

    def add_collection(self, pseudonym: AnyStr, name: AnyStr) -> None:
        self.config["children"].append((pseudonym, name))
        self.dict[pseudonym] = name
        self.root_db.nested_collections.update_one({"name": self.name}, { "$set": { "children": self.config["children"] } })

    def remove_collection(self, pseudonym: AnyStr) -> None:
        for i in range(len(self.config["children"])):
            if self.config["children"][i][0] == pseudonym:
                del self.dict[pseudonym]
                self.config["children"].pop(i)
                self.root_db.nested_collections.update_one({"name": self.name}, { "$set": { "children": self.config["children"] } })
                return

    def __getitem__(self, pseudonym) -> collection:
        try:
            return self.root_db.get_collection(self.dict[pseudonym])
        except:
            print("Collection", pseudonym, "doesn't exist...")
        
    def __contains__(self, pseudonym):
        return pseudonym in self.dict
    
            
