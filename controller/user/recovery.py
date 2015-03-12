#!/usr/bin/env python3

from string import Template
from cgi import parse_qs, escape
from utils.wrappers import Request, Response
from werkzeug.utils import redirect
import utils.event_globals as EG
import controller.header
import models
import db.user_db

def render(request):
    retval = ""
    environ = request.environ
    dRender = {'error_message':""}
    user = models.User()
    success = 0
    session = request.client_session

    # Make sure we're not already logged in
    try:
        session['id']
        return redirect('/events')
    except KeyError:
        pass

    # get GET
    dGET = parse_qs(environ['QUERY_STRING'])
    if "email" in dGET:
        dRender['email'] = dGET['email'][0]
        user.email = str(dRender['email'])
        if not user.validate_email(user):
            dRender['error_message'] = "This is not a valid email address"
            dRender['error_class'] = "error_box"

    if "key" in dGET:
        dRender['key'] = dGET['key'][0]

    # get POST
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0

    request_body = environ['wsgi.input'].read(request_body_size)
    dPOST = parse_qs(request_body)

    if b'email' in dPOST:
        dRender['email'] = dPOST[b'email'][0].decode()
        user.email = dRender['email']
        if not user.validate_email(user):
            dRender['error_message'] = "This is not a valid email address"
            dRender['error_class'] = "error_box"
    if b'key' in dPOST:
        dRender['key'] = dPOST[b'key'][0].decode()

    # TODO: This case can never happen right? HTML5 handles this for us...
    if b'password' in dPOST and b'confirmation' not in dPOST:
        dRender['error_message'] = "You must provide a new password and confirmation password"
        dRender['error_class'] = "error_box"
    elif b'password' not in dPOST and b'confirmation' in dPOST:
        dRender['error_message'] = "You must provide a new password and confirmation password"
        dRender['error_class'] = "error_box"

    # check if password and confirmation are in dPOST
    if b'password' in dPOST and b'confirmation' in dPOST and len(dRender['error_message']) == 0:
        password = dPOST[b'password'][0].decode()
        confirmation = dPOST[b'confirmation'][0].decode()
        # make sure password is valid and matches confirmation password
        if password != confirmation:
            dRender['error_message'] = "Please check that your passwords match and try again"
            dRender['error_class'] = "error_box"
        if len(password) < 8:
            dRender['error_message'] = "Your Password must be at least 8 characters long"
            dRender['error_class'] = "error_box"
        # if they are make sure user exist in pending user table
        # update users password
        # remove pending_user request
        if len(dRender['error_message']) == 0 and db.user_db.get_user(user) == EG.EVENTS_SUCCESS:
            rc = db.user_db.recover_user(user, dRender['key'], password)
            if rc == EG.EVENTS_SUCCESS:
                success = 1
            if rc == EG.EVENTS_ERROR:
                dRender['error_message'] = "We do not have a matching password activation key for this email address"
                dRender['error_class'] = "error_box"
        elif len(dRender['error_message']) == 0:
            dRender['error_message'] = "We do not have any accounts with this email address in our records"
            dRender['error_class'] = "error_box"
            # TODO login / create session


    filein = open( '../templates/website.html' )
    src = Template( filein.read() )


    if success == 0:
        activate_content = _render(dRender)
    else:
        activate_content = _render_success()

    header = controller.header.render(request)
    css_includes = "<link rel=\"stylesheet\" type=\"text/css\" href=\"" + EG.DOCUMENT_ROOT + "css/user/recovery.css\">"
    js_includes = ""
    d = {
           'content':activate_content,
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
		    'email':"",
                    'key':"",
                    'site_name':EG.EVENTS_SITE_NAME}
    d.update(FILLER)

    filein = open( '../templates/user/recovery.html' )
    src = Template( filein.read() )
    content = src.safe_substitute(d)
    return content


def _render_success():
    filein = open( '../templates/user/recovery_success.html' )
    src = Template( filein.read() )
    content = src.safe_substitute({})
    return content


if __name__ == "__main__":
    print( _render() )
