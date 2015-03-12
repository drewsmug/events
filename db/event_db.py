import os, hashlib, datetime, random
from string import Template
from pymongo import MongoClient
from bson.objectid import ObjectId
import utils.event_globals as EG
import db.db_globals as DB
import db.mongodb
import utils.email

db = db.mongodb.get_database()

def create_event(event):
    if not valid_event(event):
        raise InvalidEventError(__name__, 'event parameter incomplete')

    collection = db[DB.DB_EVENT_COL]

    categories = []
    for category in event.categories:
        categories.append(category)

    date = datetime.datetime.utcnow()
    event_id = collection.insert(
                    { DB.DB_EVENT_CREATOR_ID  : ObjectId(event.creator_id),
                      DB.DB_EVENT_TITLE       : event.title,
                      DB.DB_EVENT_START_TIME  : event.start_time,
                      DB.DB_EVENT_END_TIME    : event.end_time,
                      DB.DB_EVENT_CITY_ID     : event.city_id,
                      DB.DB_EVENT_DESCRIPTION : event.description,
                      DB.DB_EVENT_ADDRESS1    : event.address1,
                      DB.DB_EVENT_ADDRESS2    : event.address2,
                      DB.DB_EVENT_ZIP         : event.zip,
                      DB.DB_EVENT_WEBSITE     : event.website,
                      DB.DB_EVENT_CATEGORIES  : categories,
                      DB.DB_EVENT_CREATED     : date,
                      DB.DB_EVENT_LAST_UPDATED: date,
                      DB.DB_EVENT_HIT_COUNTER : 0,
                      DB.DB_EVENT_CREDITS_PAID: 0,
                    })

    event.id = event_id
    return EG.EVENTS_SUCCESS

def update_event(event):
    if not valid_event_with_id(event):
        raise InvalidEventError(__name__, 'event incomplete')
    
    collection = db[DB.DB_EVENT_COL]
    result = collection.update(
        { DB.DB_ID: ObjectId(event.id) },
        {   "$set": {
                        DB.DB_EVENT_CREATOR_ID: ObjectId(event.creator_id),
                        DB.DB_EVENT_TITLE: event.title,
                        DB.DB_EVENT_START_TIME: event.start_time,
                        DB.DB_EVENT_END_TIME: event.end_time,
                        DB.DB_EVENT_CITY_ID: ObjectId(event.city_id),
                        DB.DB_EVENT_DESCRIPTION: event.description,
                        DB.DB_EVENT_ADDRESS1: event.address1,
                        DB.DB_EVENT_ADDRESS2: event.address2,
                        DB.DB_EVENT_ZIP: event.zip,
                        DB.DB_EVENT_WEBSITE: event.website,
                        DB.DB_EVENT_CATEGORIES: event.categories,
                        DB.DB_EVENT_HIT_COUNTER: event.hit_counter,
                        DB.DB_EVENT_CREDITS_PAID: event.credits_paid,
                    },
            "$currentDate": { DB.DB_EVENT_LAST_UPDATED: True }
        },
        upsert=True)

    return result

def get_event(event):
    if event.id == None:
        raise InvalidEventError(__name__, 'event id unspecified')

    collections = db[DB.DB_EVENT_COL]

    u = collection.find( { DB.DB_ID : ObjectId(event.id) } )

    if e.count() == 0:
        return None;
    elif e.count() > 1:
        raise NonUniqueEventError(__name__, event.id + ' not unique!')
    
    e = e[0]
    event.id = e[DB.DB_ID]
    event.creator_id = e[DB.DB_EVENT_CREATOR_ID]
    event.title = e[DB.DB_EVENT_TITLE]
    event.start_time = e[DB.DB_EVENT_START_TIME]
    event.end_time = e[DB.DB_EVENT_END_TIME]
    event.city_id = e[DB.DB_EVENT_CITY_ID]
    event.description = e[DB.DB_EVENT_DESCRIPTION]
    event.address1 = e[DB.DB_EVENT_ADDRESS1]
    event.address2 = e[DB.DB_EVENT_ADDRESS2]
    event.zip = e[DB.DB_EVENT_ZIP]
    event.website = e[DB.DB_EVENT_WEBSITE]
    event.categories = e[DB.DB_EVENT_CATEGORIES]
    event.hit_counter = e[DB.DB_EVENT_HIT_COUNTER]
    event.credits_paid = e[DB.DB_EVENT_CREDITS_PAID]
    return EG.EVENTS_SUCCESS

def valid_event(event):
    return (event.creator_id != None and event.title != None
            and event.start_time != None and event.end_time != None
            and event.city_id != None and event.description != None
            and event.categories != None)

def valid_event_with_id(event):
    return (event.id != None and valid_event(event))

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class InvalidEventError(Error):
    """Exception raised for invalid event parameters

    Attributes:
        func -- function in which the error occurred
        msg  -- explanation of the error
    """
    def __init__(self, func, msg):
        self.func = func
        self.msg = msg

class NonUniqueEventError(Error):
    """Exception raised for non-unique event

    Attributes:
        func -- function in which the error occurred
        msg  -- explanation of the error
    """
    def __init__(self, func, msg):
        self.func = func
        self.msg = msg

class WriteError(Error):
    """Exception raised for write error

    Attributes:
        func -- function in which the error occurred
        code -- error code
        msg  -- explanation of the error
    """
    def __init__(self, func, code, msg):
        self.func = func
        self.code = code
        self.msg = msg

