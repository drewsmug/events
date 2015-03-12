# Database ID
DB_ID = "_id"

# User Collection
DB_USER_COL = "user"
DB_USER_EMAIL = "email"
DB_USER_NAME = "name"
DB_USER_FIRSTNAME = "first"
DB_USER_LASTNAME = "last"
DB_USER_PASS = "password"
DB_USER_CREATED = "date_created"
DB_USER_LAST_UPDATED = "date_last_updated"
DB_USER_LAST_LOGIN = "date_last_login"
DB_USER_ROLE = "role"

# Pending User Collection
DB_PENDING_USER_COL = "pending_user"
DB_PENDING_USER_EMAIL = "email"
DB_PENDING_USER_NEW_EMAIL = "new_email"
DB_PENDING_USER_KEY = "activation_key"
DB_PENDING_USER_ROLE = "role"
DB_PENDING_USER_EXPIRATION = "expiration"
DB_PENDING_USER_ROLE_ACTIVATE = 1
DB_PENDING_USER_ROLE_PASSWORD_RECOVERY = 2
DB_PENDING_USER_ROLE_EMAIL_RESET = 3

# Event collection
DB_EVENT_COL = "event"
DB_EVENT_CREATOR_ID = "creator_id"
DB_EVENT_TITLE = "title"
DB_EVENT_START_TIME = "start_time"
DB_EVENT_END_TIME = "end_time"
DB_EVENT_CITY_ID = "city_id"
DB_EVENT_DESCRIPTION = "description"
DB_EVENT_ADDRESS1 = "address1"
DB_EVENT_ADDRESS2 = "address2"
DB_EVENT_ZIP = "zip"
DB_EVENT_WEBSITE = "website"
DB_EVENT_CATEGORIES = "categories"
DB_EVENT_CREATED = "date_created"
DB_EVENT_LAST_UPDATED = "date_last_updated"
DB_EVENT_HIT_COUNTER = "hit_counter"
DB_EVENT_CREDITS_PAID = "credits_paid"

# City Collection
DB_CITY_COL = "city"
DB_CITY_GEONAME_ID = "geoname_id"
DB_CITY_NAME = "name"
DB_CITY_STATE = "state"
DB_CITY_COUNTRY = "country"
DB_CITY_GEOLOC = "geoloc"

# Feedback Collection
DB_FEEDBACK_COL = "feedback"
DB_FEEDBACK_COMMENT = "comment"
DB_FEEDBACK_COMMENT_TYPE = "comment_type"
DB_FEEDBACK_CREATED = "date_created"
DB_FEEDBACK_SUBMITTER_ID = "submitter_id"
DB_FEEDBACK_OWNER_ID = "owner_id"
DB_FEEDBACK_CLOSED = "date_closed"

# Write Error
DB_WRITE_CONCERN_ERROR = "writeConcernError"
DB_WRITE_ERROR = "writeError"
DB_WRITE_ERROR_CODE = "code"
DB_WRITE_ERROR_MSG = "errmsg"
