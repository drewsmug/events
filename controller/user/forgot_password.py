#!/usr/bin/env python3

from string import Template
from cgi import parse_qs, escape
from utils.wrappers import Request, Response
from werkzeug.utils import redirect
import controller.header
import utils.event_globals as EG
import models
import db.user_db

def render(request):
    environ = request.environ
    retval = ""
    dRender = {}
    u = models.User()
    success = 0
    session = request.client_session

    # Make sure we're not already logged in
    try:
        session['id']
        return redirect('/events')
    except KeyError:
        pass

    # get POST
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0

    request_body = environ['wsgi.input'].read(request_body_size)
    dPOST = parse_qs(request_body)

    if b'email' in dPOST:
        pemail = dPOST[b'email'][0].decode()
        u.email = pemail
        if db.user_db.get_user(u) == EG.EVENTS_SUCCESS:
            success = 1
        else:
            retval = "We do not have an account with this email address"
	
        if len(retval) == 0 and u.deactivated():
            success = 0
            retval = "This account has not been activated yet. Please check your email."


    if len(retval) > 0:
        if b'email' in dPOST:
            dRender['email'] = dPOST[b'email'][0].decode()
            dRender['error_message'] = retval
            dRender['error_class'] = "error_box"

    filein = open( '../templates/website.html' )
    src = Template( filein.read() )

    if success == 1:
        # TODO
        # add document to pending_user collection
        if db.user_db.create_password_recovery_entry(u) == EG.EVENTS_SUCCESS:
            forgot_password_content = _render_success()
        else:
            success = 0
            dRender['error_message'] = "We're sorry. There was an error sending your email. Please try again."
            dRender['error_class'] = "error_box"

    if success == 0:
        forgot_password_content = _render(dRender)

    header = controller.header.render(request)

    css_includes = "<link rel=\"stylesheet\" type=\"text/css\" href=\"" + EG.DOCUMENT_ROOT + "css/user/forgot_password.css\">"
    js_includes = ""
    d = {
           'content':forgot_password_content,
           'header':header,
           'css_includes':css_includes,
           'js_includes':js_includes,
           'DOCUMENT_ROOT' : EG.DOCUMENT_ROOT,
           'title':"Account Recovery"}

    site_content = src.safe_substitute(d)
    return Response(site_content, mimetype='text/html')

def _render(FILLER):
    d = {
		    'error_class':"",
		    'error_message':"",
		    'email':""}
    d.update(FILLER)

    filein = open( '../templates/user/forgot_password.html' )
    src = Template( filein.read() )
    content = src.safe_substitute(d)

    return content


def _render_success():
    filein = open( '../templates/user/forgot_password_success.html' )
    src = Template( filein.read() )
    content = src.safe_substitute({})
    return content


if __name__ == "__main__":
    print( _render({}) )

