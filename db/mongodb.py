from pymongo import MongoClient

DB_USERNAME = "" # append ':'
DB_PASSWORD = "" # append '@'
DB_HOSTNAME = "localhost"
DB_PORT = "27017"
DB_NAME = "events_beta"

_connection = None

def connection(host=DB_HOSTNAME, port=DB_PORT, user=DB_USERNAME,
               password=DB_PASSWORD):
    global _connection
    db_uri = "mongodb://" + user + password + host + ":" + port + "/"
    if not _connection:
        _connection = MongoClient(db_uri)
    return _connection

def get_database(db_name=DB_NAME):
    return connection()[db_name]

#if __name__ == "__main__":
#    # Do stuff when executed as a script
#    db = Db()
