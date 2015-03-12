#!/usr/bin/env python3
import sys
sys.path.append('../')
import re
from pymongo import MongoClient
from bson.objectid import ObjectId
import db_globals as DB

client = MongoClient(DB.DB_URI)
db = client[DB.DB_NAME]
cities_collection = db[DB.DB_CITY_COL]

# Initialize timezones
#with open("timeZones.txt", "r") as f:
#    f.readline() # Remove first line containing column names
#    timezones = f.readlines()
#
#    for timezone in timezones:
#        country_code, timezone_id, gmt_offset, dst_offset, raw_offset = timezone.split()
#        #print("countryCode =", countryCode, " timezoneId =", timezoneId,
#        #      " gmtOffset =", gmtOffset, " dstOffset =", dstOffset,
#        #      " rawOffset =", rawOffset)
#        timezone = { "timezone" : timezone_id,
#                     "country"  : country_code,
#                     "gmt_offset" : gmt_offset,
#                     "dst_offset" : dst_offset,
#                     "raw_offset" : raw_offset
#                   }
#        print(timezone)
#        db.timezones.insert(timezone)

with open("cities1000.txt", "r") as f:
    cities = f.readlines()

    for city in cities:
            #print(city)
            #print("city split =", re.split(r'\t', city))
            (geoname_id, name, asciiname, alternate_names, latitude, longitude,
            feature_class, feature_code, country_code, cc2, admin1_code,
            admin2_code, admin3_code, admin4_code, population, elevation, dem,
            timezone, modifcation_date) = re.split(r'\t', city)

            #timezone = db.timezones.find_one({"timezone" : timezone})

            #if timezone == None:
            #    print("ERROR: could not find timezone", timezone)
            #    sys.exit(-1)
                
            # Only insert US cities
            if country_code != "US":
                continue

            city = { DB.DB_CITY_GEONAME_ID : geoname_id,
                     DB.DB_CITY_NAME : name,
                     DB.DB_CITY_STATE : admin1_code,
                     DB.DB_CITY_COUNTRY : country_code,
                     DB.DB_CITY_GEOLOC : {
                                    "type" : "Point",
                                    "coordinates" : [latitude, longitude]
                                  },
                     #"timezone_id" : ObjectId(timezone["_id"])
                   }
            print(city)
            cities_collection.insert(city)

