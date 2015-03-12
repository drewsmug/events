#!/usr/bin/env python3

from string import Template
from cgi import parse_qs, escape
from utils.wrappers import Request, Response
from werkzeug.utils import redirect
#import controller.forgot_password
import controller.header
import utils.event_globals as EG
import models
import db.user_db

def render(request):
    environ = request.environ
    retval = ""
    dRender = {}
    u = models.User()
    u_check_dupes = models.User()
    success = 0
    session = request.client_session

    # Make sure we are logged in
    try:
        session['id']
    except KeyError:
        return redirect('/user/login')

    u = models.User(_id=session['id'])
    db.user_db.get_user(u)

    # get POST
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0

    request_body = environ['wsgi.input'].read(request_body_size)
    dPOST = parse_qs(request_body)

    if b'email' in dPOST:
        pemail = dPOST[b'email'][0].decode()
        dRender['email'] = pemail
        # Validate valid email address
        if u.validate_email(pemail) != EG.EVENTS_SUCCESS:
            retval = "Invalid email address format"

        if pemail == u.email:
            retval = "This is the same as the current email we have for you"

        u_check_dupes.email = pemail
        if len(retval) == 0 and db.user_db.get_user(u_check_dupes) == EG.EVENTS_SUCCESS:
            retval = "We already have a user with this email address"

        # check password
        ppassword = dPOST[b'password'][0].decode()
        if not u.password_matches(ppassword):
            retval = "Invalid password"

        if len(retval) == 0:
            success = 1
	

    filein = open( '../templates/website.html' )
    src = Template( filein.read() )


    if success == 1:
        # TODO
        # add document to pending_user collection
        pemail = dPOST[b'email'][0].decode()
        if db.user_db.create_email_reset_entry(u, pemail) == EG.EVENTS_SUCCESS:
            update_email_content = _render_success()
        else:
            success = 0
            retval = "We're sorry. There was an error sending your email. Please try again."

    if success == 0:
        if len(retval) > 0:
            dRender['error_message'] = retval
            dRender['error_class'] = "error_box"
        update_email_content = _render(dRender)

    header = controller.header.render(request)

    css_includes = "<link rel=\"stylesheet\" type=\"text/css\" href=\"" + EG.DOCUMENT_ROOT + "css/user/update_email.css\">"
    js_includes = ""
    d = {
           'content':update_email_content,
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

    filein = open( '../templates/user/update_email.html' )
    src = Template( filein.read() )
    content = src.safe_substitute(d)

    return content


def _render_success():
    filein = open( '../templates/user/update_email_success.html' )
    src = Template( filein.read() )
    content = src.safe_substitute({})
    return content

