import re
from pymongo import MongoClient
import db.db_globals as DB
import db.mongodb

db = db.mongodb.get_database()

def get_city(city_string, max_results):
    if len(city_string) < 1:
        return None

    if not max_results:
        max_results = 10

    city = db[DB.DB_CITY_COL]
    pattern = '^' + city_string
    regx = re.compile(pattern, re.IGNORECASE)
    c = city.find( { DB.DB_CITY_NAME : regx } ).limit( max_results )

    return c

