import json
from bson.objectid import ObjectId
from werkzeug.utils import cached_property
from werkzeug.wrappers import Request as BaseRequest, Response as BaseResponse
from werkzeug.contrib.securecookie import SecureCookie as SecureCookieBase
import utils.event_globals as EG

COOKIE_SECRET_KEY = 'Ky\xafF\x14\xd2\xf6\xa6\x88\x7f\x91p\xa8\xd5\x01\x9a\xb8mR\xae'

class Request(BaseRequest):
    @cached_property
    def client_session(self):
        data = self.cookies.get(EG.SESSION_COOKIE_NAME)
        if not data:
            return SecureCookie(secret_key=COOKIE_SECRET_KEY)
        return SecureCookie.unserialize(data, COOKIE_SECRET_KEY)

class Response(BaseResponse):
    """
    """
    
class SecureCookie(SecureCookieBase):
    serialization_method = json
    _delete = False

    @property
    def delete(self):
        """The 'delete' property."""
        return self._delete
    
    @delete.setter
    def delete(self, value):
        self._delete = value

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)
