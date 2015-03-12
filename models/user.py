from passlib.hash import pbkdf2_sha256
import utils.event_globals as EG
#import db.user_db
import re

# Password Requirements
PASS_MIN_LENGTH = 8

# Password Hashing
ROUNDS = 200000
SALT_SIZE = 16

class User:
    def __init__(self, _id=None, email=None, first_name=None, last_name=None,
                 password=None, password_encrypted=False, date_created=None,
                 date_last_updated=None, date_last_login=None, role=None):
        self._id = _id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.password_encrypted = password_encrypted

        if password == None:
            self.password = password
        elif not password_encrypted:
            self.password = pbkdf2_sha256.encrypt(password, rounds=ROUNDS,
                                                  salt_size=SALT_SIZE)
            self.password_encrypted = True

        self.date_created = date_created
        self.date_last_updated = date_last_updated
        self.date_last_login = date_last_login
        self.role = role

    @property
    def id(self):
        """The 'id' property."""
        return self._id

    @id.setter
    def id(self, user_id):
        self._id = user_id

    def jsonify(self):
        return str(self._id)

    def validate_password(self, password=None):
        if password == None:
            password = self.password

        return (len(password) >= PASS_MIN_LENGTH)

    def validate_email(self, email=None):
        if email == None:
            email = self.email

        if not re.match(r"[^@]+@[^@]+\.[^@]+", str(email)) or re.search(r"=", str(email)):
            return EG.EVENTS_ERROR
        else:
            return EG.EVENTS_SUCCESS

    def deactivate(self):
        if not self.banned() and not self.deactivated():
            self.role = EG.USER_ROLE_DEACTIVATED

    def activate(self):
        self.role = EG.USER_ROLE_USER

    def deactivated(self):
        return self.role == EG.USER_ROLE_DEACTIVATED

    def ban(self):
        if not self.banned() and not self.deactivated():
            self.role = EG.USER_ROLE_BANNED

    def banned(self):
        return self.role == EG.USER_ROLE_BANNED

    def hash_my_password(self):
        if self.password == None:
            raise UnsetPasswordError(__name__, "password not set!")
        elif self.password_encrypted:
            return

        hash = pbkdf2_sha256.encrypt(self.password, rounds=ROUNDS,
                                     salt_size=SALT_SIZE)
        self.password = hash
        self.password_encrypted = True

    def hash_password(self, password):
        return pbkdf2_sha256.encrypt(password, rounds=ROUNDS,
                                     salt_size=SALT_SIZE)

    def password_matches(self, password):
        return pbkdf2_sha256.verify(password, self.password)

class UnsetPasswordError(Exception):
    """Exception raised for unset password

    Attributes:
        func -- function in which the error occurred
        msg  -- explanation of the error
    """
    def __init__(self, func, msg):
        self.func = func
        self.msg = msg

if __name__ == "__main__":
    print("Called from command line\n")
