from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from . import login
from . import logout
from . import activate
from . import forgot_password
from . import profile
from . import register
from . import recovery
from . import update_email
from . import reset_email
import controller.error_404

url_map = Map([
                Rule('/user/login', endpoint='login'),
                Rule('/user/logout', endpoint='logout'),
                Rule('/user/activate', endpoint='activate'),
                Rule('/user/forgot', endpoint='forgot_password'),
                Rule('/user/edit', endpoint='profile'),
                Rule('/user/register', endpoint='register'),
                Rule('/user/recovery', endpoint='recovery'),
                Rule('/user/email/new', endpoint='update_email'),
                Rule('/user/email/reset', endpoint='reset_email'),
              ])

def dispatch(request, path):
    adapter = url_map.bind_to_environ(request.environ)
    try:
        endpoint, values = adapter.match()
        return getattr(controller.user, 'on_' + endpoint)(request, **values)
    except NotFound as e:
        return error_404(request)
    except HTTPException as e:
        return e

def on_login(request):
    return login.render(request)

def on_logout(request):
    return controller.user.logout.render(request)

def on_activate(request):
    return activate.render(request)

def on_forgot_password(request):
    return forgot_password.render(request)

def on_profile(request):
    return profile.render(request)

def on_register(request):
    return register.render(request)

def on_recovery(request):
    return recovery.render(request)

def on_update_email(request):
    return update_email.render(request)

def on_reset_email(request):
    return reset_email.render(request)

def error_404(request):
    return controller.error_404.render(request)
