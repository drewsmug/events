import os, hashlib, datetime, random
from string import Template
from pymongo import MongoClient
import utils.event_globals as EG
import db.db_globals as DB
import db.mongodb

db = db.mongodb.get_database()

def create_feedback(feedback):
    if (feedback.submitter_id == None or feedback.comment_type == None or
        feedback.comment == None):
        raise InvalidFeedbackError(__name__, 'feedback parameter incomplete')

    feedbacks = db[DB.DB_FEEDBACK_COL]

    date = datetime.datetime.utcnow()
    feedbacks.insert( {
                    DB.DB_FEEDBACK_COMMENT : feedback.comment,
                    DB.DB_FEEDBACK_COMMENT_TYPE : feedback.comment_type,
                    DB.DB_FEEDBACK_CREATED : date,
                    DB.DB_FEEDBACK_SUBMITTER_ID : feedback.submitter_id,
                   } )

    return EG.EVENTS_SUCCESS


class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class InvalidFeedbackError(Error):
    """Exception raised for invalid feedback parameters

    Attributes:
        func -- function in which the error occurred
        msg  -- explanation of the error
    """
    def __init__(self, func, msg):
        self.func = func
        self.msg = msg

