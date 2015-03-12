import os, hashlib, datetime, random
from string import Template
from pymongo import MongoClient
from bson.objectid import ObjectId
import models
import utils.event_globals as EG
import db.db_globals as DB
import db.mongodb
import utils.email

db = db.mongodb.get_database()

def create_user(user):
    if not valid_user(user):
        raise InvalidUserError(__name__, 'user parameter incomplete')

    users = db[DB.DB_USER_COL]
    u = users.find_one( { DB.DB_USER_EMAIL : user.email } )

    if u != None:
        raise InvalidUserError(__name__, 'user ' + str(user.email) +
                               ' already exists')

    # Deactivate user password until user activates via email
    user.deactivate()

    # FIXME: need to add list of cities to receive events on
    date = datetime.datetime.utcnow()
    user_id = users.update(
                    { DB.DB_USER_EMAIL  : user.email },
                    { "$set" : {
                        DB.DB_USER_EMAIL        : user.email,
                        DB.DB_USER_NAME         : {
                                                 DB.DB_USER_FIRSTNAME : user.first_name,
                                                 DB.DB_USER_LASTNAME  : user.last_name
                                                  },
                        DB.DB_USER_PASS         : user.password,
                        DB.DB_USER_CREATED      : date,
                        DB.DB_USER_LAST_UPDATED : date,
                        DB.DB_USER_LAST_LOGIN   : date,
                        DB.DB_USER_ROLE         : user.role
                                },
                    },
                    upsert=True)
    user.id = user_id

    return EG.EVENTS_SUCCESS

def update_user(user):
    if not valid_user_with_id(user):
        raise InvalidUserError(__name__, 'user incomplete')
    
    users = db[DB.DB_USER_COL]
    # FIXME: Add check for raising OperationFailure error
    # and check dict returned to see if record was successfully
    # matched and updated (WriteResult)
    result = users.update(
        { DB.DB_ID: ObjectId(user.id) },
        {   "$set": {
                        DB.DB_USER_EMAIL: user.email,
                        DB.DB_USER_NAME: {
                                DB.DB_USER_FIRSTNAME: user.first_name,
                                DB.DB_USER_LASTNAME: user.last_name
                                         },
                        DB.DB_USER_PASS: user.password,
                        DB.DB_USER_ROLE: user.role
                    },
            "$currentDate": { DB.DB_USER_LAST_UPDATED: True }
        },
        upsert=True)

    #if result.hasWriteConcernError():
    #    raise WriteError(__name__,
    #                     result[DB.DB_WRITE_CONCERN_ERROR][DB.DB_WRITE_ERROR_CODE],
    #                     result[DB.DB.WRITE_CONCERN_ERROR][DB.DB_WRITE_ERROR_MSG])
    #elif result.hasWriteError():
    #    raise WriteError(__name__,
    #                     result[DB.DB_WRITE_ERROR][DB.DB_WRITE_ERROR_CODE],
    #                     result[DB.DB.WRITE_ERROR][DB.DB_WRITE_ERROR_MSG])

    return result

def get_user(user):
    if user.id == None and user.email == None:
        raise InvalidUserError(__name__, 'user email unspecified')

    users = db[DB.DB_USER_COL]

    if user.id != None:
        u = users.find( { DB.DB_ID : ObjectId(user.id) } )
    else:
        u = users.find( { DB.DB_USER_EMAIL : user.email } )

    if u.count() == 0:
        return None;
    elif u.count() > 1:
        raise NonUniqueUserError(__name__, user.email + ' not unique!')
    
    u = u[0]
    user.id = u[DB.DB_ID]
    user.email = u[DB.DB_USER_EMAIL]
    user.first_name = u[DB.DB_USER_NAME][DB.DB_USER_FIRSTNAME]
    user.last_name = u[DB.DB_USER_NAME][DB.DB_USER_LASTNAME]
    user.password = u[DB.DB_USER_PASS]
    user.date_created = u[DB.DB_USER_CREATED]
    user.date_last_updated = u[DB.DB_USER_LAST_UPDATED]
    user.date_last_login = u[DB.DB_USER_LAST_LOGIN]
    user.role = u[DB.DB_USER_ROLE]
    return EG.EVENTS_SUCCESS

def create_deactivated_entry(user):
    if not valid_user(user):
        raise InvalidUserError(__name__, 'user incomplete')

    deactivated_collection = db[DB.DB_PENDING_USER_COL]

    # Generate user activation key and expiration
    random_string = str(random.random()).encode('utf8')
    salt = hashlib.sha1(random_string).hexdigest()[:5]
    salted = (salt + user.email).encode('utf8')
    activation_key = hashlib.sha1(salted).hexdigest()
    key_expires = datetime.datetime.today() + datetime.timedelta(2)

    deactivated_id = deactivated_collection.update(
                        { DB.DB_PENDING_USER_EMAIL  : user.email },
                        {   "$set" : {
                                DB.DB_PENDING_USER_EMAIL         : user.email,
                                DB.DB_PENDING_USER_KEY           : activation_key,
                                DB.DB_PENDING_USER_EXPIRATION    : key_expires,
                                DB.DB_PENDING_USER_ROLE          : DB.DB_PENDING_USER_ROLE_ACTIVATE
                                     }
                        },
                        upsert=True)

    send_activation_email(user, activation_key)

    return EG.EVENTS_SUCCESS


def create_password_recovery_entry(user):
    if not valid_user(user):
        raise InvalidUserError(__name__, 'user incomplete')

    collection = db[DB.DB_PENDING_USER_COL]

    # Generate user activation key and expiration
    random_string = str(random.random()).encode('utf8')
    salt = hashlib.sha1(random_string).hexdigest()[:5]
    salted = (salt + user.email).encode('utf8')
    activation_key = hashlib.sha1(salted).hexdigest()
    key_expires = datetime.datetime.today() + datetime.timedelta(2)

    deactivated_id = collection.update(
                        { DB.DB_PENDING_USER_EMAIL  : user.email },
                        {   "$set" : {
                                DB.DB_PENDING_USER_EMAIL        : user.email,
                                DB.DB_PENDING_USER_KEY          : activation_key,
                                DB.DB_PENDING_USER_EXPIRATION   : key_expires,
                                DB.DB_PENDING_USER_ROLE          : DB.DB_PENDING_USER_ROLE_PASSWORD_RECOVERY
                                     }
                        },
                        upsert=True)

    send_recovery_email(user, activation_key)
    
    return EG.EVENTS_SUCCESS


def create_email_reset_entry(user, updated_email):
    if not valid_user(user):
        raise InvalidUserError(__name__, 'user incomplete')

    collection = db[DB.DB_PENDING_USER_COL]

    # Generate user activation key and expiration
    random_string = str(random.random()).encode('utf8')
    salt = hashlib.sha1(random_string).hexdigest()[:5]
    salted = (salt + user.email).encode('utf8')
    activation_key = hashlib.sha1(salted).hexdigest()
    key_expires = datetime.datetime.today() + datetime.timedelta(2)

    deactivated_id = collection.update(
            { "$and" : [ { DB.DB_PENDING_USER_EMAIL  : user.email }, { DB.DB_PENDING_USER_ROLE : DB.DB_PENDING_USER_ROLE_EMAIL_RESET } ] },
                        {   "$set" : {
                                DB.DB_PENDING_USER_EMAIL        : user.email,
                                DB.DB_PENDING_USER_NEW_EMAIL        : updated_email,
                                DB.DB_PENDING_USER_KEY          : activation_key,
                                DB.DB_PENDING_USER_EXPIRATION   : key_expires,
                                DB.DB_PENDING_USER_ROLE          : DB.DB_PENDING_USER_ROLE_EMAIL_RESET
                                     }
                        },
                        upsert=True)

    user.email = updated_email
    send_reset_email(user, activation_key)

    return EG.EVENTS_SUCCESS

def send_reset_email(user, activation_key):
    if not valid_user(user):
        raise InvalidUserError(__name__, 'user incomplete')

    try:
        os.environ['SITE_SUB_DOMAIN']
    except KeyError:
        os.environ['SITE_SUB_DOMAIN'] = os.environ['USER']

    site_sub_domain = os.environ['SITE_SUB_DOMAIN']

    d = { 'first_name' : user.first_name,
          'site_sub_domain' : site_sub_domain,
          'email' : user.email,
          'key' : activation_key }

    filein = open( '../templates/email_reset_email.txt' )
    email_template = Template( filein.read() )
    email_subject = 'Reset Email'
    email_body = email_template.safe_substitute(d)
    sender_email = EG.SENDER_EMAIL % (site_sub_domain)
    utils.email.send_email(user.email, sender_email, email_subject, email_body)

def send_recovery_email(user, activation_key):
    if not valid_user(user):
        raise InvalidUserError(__name__, 'user incomplete')

    # Set the SITE_SUB_DOMAIN environment variable regardless if run
    # from command line or web server
    try:
        os.environ['SITE_SUB_DOMAIN']
    except KeyError:
        os.environ['SITE_SUB_DOMAIN'] = os.environ['USER']

    site_sub_domain = os.environ['SITE_SUB_DOMAIN']

    d = { 'first_name' : user.first_name,
          'site_sub_domain' : site_sub_domain,
          'email' : user.email,
          'key' : activation_key }
          

    filein = open( '../templates/email_forgot_password.txt' )
    email_template = Template( filein.read() )
    email_subject = 'Account Recovery'
    email_body = email_template.safe_substitute(d)
    sender_email = EG.SENDER_EMAIL % (site_sub_domain)
    utils.email.send_email(user.email, sender_email, email_subject, email_body)
    return EG.EVENTS_SUCCESS

def send_activation_email(user, activation_key):
    if not valid_user(user):
        raise InvalidUserError(__name__, 'user incomplete')

    # Set the SITE_SUB_DOMAIN environment variable regardless if run
    # from command line or web server
    try:
        os.environ['SITE_SUB_DOMAIN']
    except KeyError:
        os.environ['SITE_SUB_DOMAIN'] = os.environ['USER']

    site_sub_domain = os.environ['SITE_SUB_DOMAIN']

    d = { 'first_name' : user.first_name,
          'site_sub_domain' : site_sub_domain,
          'email' : user.email,
          'key' : activation_key,
          'site_name' : EG.EVENTS_SITE_NAME }

    filein = open( '../templates/email_activation.txt' )
    email_template = Template( filein.read() )
    email_subject = 'Account Confirmation'
    email_body = email_template.safe_substitute(d)
    sender_email = EG.SENDER_EMAIL % (site_sub_domain)
    utils.email.send_email(user.email, sender_email, email_subject, email_body)
    return EG.EVENTS_SUCCESS

def activate_user(user, activation_key):
    if user.email == None:
        raise InvalidUserError(__name__, 'user incomplete')

    collection = db[DB.DB_PENDING_USER_COL]

    u = collection.find( { "$and" : [ { DB.DB_PENDING_USER_EMAIL : user.email }, { DB.DB_PENDING_USER_ROLE : DB.DB_PENDING_USER_ROLE_ACTIVATE } ] } )

    if u.count() == 0:
        return EG.EVENTS_USER_NOT_FOUND
    elif u.count() > 1:
        raise NonUniqueUserError(__name__, user.email + ' not unique!')

    u = u[0]
    if u[DB.DB_PENDING_USER_KEY] != activation_key:
        return EG.EVENTS_WRONG_ACTIVATION_KEY
    
    if get_user(user) != EG.EVENTS_SUCCESS:
        return EG.EVENTS_ERROR

    user.role = EG.USER_ROLE_USER
    update_user(user)
    collection.remove( { "$and" : [ { DB.DB_PENDING_USER_EMAIL : user.email }, { DB.DB_PENDING_USER_ROLE : DB.DB_PENDING_USER_ROLE_ACTIVATE } ] } )
    return EG.EVENTS_SUCCESS

def reset_email(activation_key):
    user = models.User()
    collection = db[DB.DB_PENDING_USER_COL]

    u = collection.find( { "$and" : [
                                    { DB.DB_PENDING_USER_KEY : activation_key },
                                    { DB.DB_PENDING_USER_ROLE : DB.DB_PENDING_USER_ROLE_EMAIL_RESET }
                                    ] } )

    if u.count() == 0 or u.count() > 1:
        return EG.EVENTS_ERROR

    u = u[0]
    user.email = u[DB.DB_PENDING_USER_EMAIL]
    get_user(user)
    user.email = u[DB.DB_PENDING_USER_NEW_EMAIL]
    update_user(user)
    collection.remove( { "$and" : [ { DB.DB_PENDING_USER_KEY : activation_key }, { DB.DB_PENDING_USER_ROLE : DB.DB_PENDING_USER_ROLE_EMAIL_RESET } ] } )
    return EG.EVENTS_SUCCESS

def recover_user(user, activation_key, password):
    if user.email == None:
        raise InvalidUserError(__name__, 'user incomplete')

    collection = db[DB.DB_PENDING_USER_COL]

    u = collection.find( { "$and" : [ { DB.DB_PENDING_USER_EMAIL : user.email }, { DB.DB_PENDING_USER_ROLE : DB.DB_PENDING_USER_ROLE_PASSWORD_RECOVERY }, { DB.DB_PENDING_USER_KEY : activation_key } ] } )

    if u.count() == 0:
        return EG.EVENTS_ERROR
    # If they forget their password and request an email twice
    # there may be multiple pending_user request
    #elif u.count() > 1:
    #    raise NonUniqueUserError(__name__, user.email + ' not unique!')

    u = u[0]
    if u[DB.DB_PENDING_USER_KEY] != activation_key:
        return EG.EVENTS_WRONG_ACTIVATION_KEY
    
    if get_user(user) != EG.EVENTS_SUCCESS:
        return EG.EVENTS_ERROR

    user.password = password
    user.hash_my_password()
    update_user(user)
    collection.remove( { "$and" : [ { DB.DB_PENDING_USER_EMAIL : user.email }, { DB.DB_PENDING_USER_ROLE : DB.DB_PENDING_USER_ROLE_PASSWORD_RECOVERY }, { DB.DB_PENDING_USER_KEY : activation_key } ] } )
    return EG.EVENTS_SUCCESS

def valid_user(user):
    return (user.email != None and user.first_name != None
            and user.last_name != None and user.password != None)

def valid_user_with_id(user):
    return (user.id != None and valid_user(user))

def ban_user(user):
    user.ban()
    update_user(user)
    return EG.EVENTS_SUCCESS

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class InvalidUserError(Error):
    """Exception raised for invalid user parameters

    Attributes:
        func -- function in which the error occurred
        msg  -- explanation of the error
    """
    def __init__(self, func, msg):
        self.func = func
        self.msg = msg

class NonUniqueUserError(Error):
    """Exception raised for non-unique user

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

