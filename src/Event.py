from __future__ import annotations
from flask_login import UserMixin
from typing import List, Dict, AnyStr, Union
from bson.objectid import ObjectId
from pymongo import MongoClient, cursor, collection
from passlib.hash import pbkdf2_sha256

class Event():
    events : collection = None

    def __init__(self, eventhost: AnyStr, eventname: AnyStr, time: AnyStr, date: AnyStr, place: AnyStr, friends_in_event: List = [], id: ObjectId = None):
        self.eventhost = eventhost
        self.eventname = eventname
        self.time = time
        self.date = date
        self.place = place
        self.friends_in_event = friends_in_event[:]
        if id:
            self.id = id
        else:
            Event.events.insert_one(self.to_BSON())
            self.id = Event.events.find_one({'eventname': self.eventname})['_id']
        return
    
    def Already_Exists(eventname=""):
        if  eventname == "":
            return True
        return Event.events.find_one({'eventname': eventname.lower()})
    
    def update_db(self):
        Event.events.replace_one({'_id': self.id}, self.to_BSON())
    
    def get_id(self):
        return str(self.id)
    
    def to_BSON(self) -> Dict:
        bson_dict = {}
        if hasattr(self, 'id'):
            bson_dict["_id"] = self.id
        bson_dict['eventhost']=self.hostname
        bson_dict["eventname"] = self.eventname
        bson_dict["time"] = self.time
        bson_dict["date"] = self.date
        bson_dict["place"] = self.place
        bson_dict["friends_in_event"] = self.friends_in_event[:]
        return bson_dict
    
    def from_BSON(bson_dict: Dict) -> Event:
        if not bson_dict:
            return None
        return Event(eventname= bson_dict["eventname"],
                    time= bson_dict["time"],
                    date= bson_dict["date"],
                    place= bson_dict["place"],
                    friends= bson_dict["friends"],
                    id=bson_dict["_id"])


