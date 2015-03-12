#!/usr/bin/env python3

from string import Template
from cgi import parse_qs, escape
import re
from utils.wrappers import Request, Response
from werkzeug.utils import redirect
import controller.header
import models
import db.user_db
import utils.event_globals as EG

def render(request):
    environ = request.environ
    success = 0
    dRender = {}
    response_body = ""
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
   
    #check POST for hidden
    if b'page' in dPOST:

        # validate user input
        retval = validate(dPOST)
        # make sure user doesn't already exist
        if b'email' in dPOST:
            pemail = dPOST[b'email'][0].decode()
            u = models.User(email=pemail)
            if db.user_db.get_user(u) == EG.EVENTS_SUCCESS:
                retval = "We already have a user with this email address"
        # There was an error validating user input
        if len(str(retval)) > 0:
            if b'email' in dPOST:
                dRender['email'] = dPOST[b'email'][0].decode()
            if b'first_name' in dPOST:
                dRender['first_name'] = dPOST[b'first_name'][0].decode()
            if b'last_name' in dPOST:
                dRender['last_name'] = dPOST[b'last_name'][0].decode()
            dRender['error_message'] = retval
            dRender['error_class'] = "error_box"
        else:
            # User was successful
            success = 1
            # Generate a validation string and email it to them
            pemail = dPOST[b'email'][0].decode()
            pfirst_name = dPOST[b'first_name'][0].decode()
            plast_name = dPOST[b'last_name'][0].decode()
            ppassword = dPOST[b'password'][0].decode()
            u = models.User(
                   email=pemail,
                   first_name=pfirst_name,
                   last_name=plast_name,
                   password=ppassword)
            db.user_db.create_user(u)
            db.user_db.create_deactivated_entry(u)

    if success == 0:
        register_content = _render(dRender)
    else:
        name = dPOST[b'first_name'][0].decode()
        register_content = _render_success()

    filein = open( '../templates/website.html' )
    src = Template( filein.read() )
    header = controller.header.render(request)
    css_includes = "<link rel=\"stylesheet\" type=\"text/css\" href=\"" + EG.DOCUMENT_ROOT + "css/user/register.css\">"
    js_includes = ""
    d = {
           'content':register_content,
           'header':header,
           'css_includes':css_includes,
           'js_includes':js_includes,
           'DOCUMENT_ROOT' : EG.DOCUMENT_ROOT,
           'title':"Register"}

    site_content = src.safe_substitute(d)
    return Response(site_content, mimetype='text/html')

def _render(HEADER):
    d = {
            'site_name':EG.EVENTS_SITE_NAME,
            'error_class':"",
            'error_message':"",
            'first_name':"",
            'last_name':"",
            'email':""}

    d.update(HEADER)

    filein = open( '../templates/user/register.html' )
    src = Template( filein.read() )
    content = src.safe_substitute(d)

    return content


def validate(post):
    # check email
    if b'email' in post:
        email = post[b'email'][0].decode()
    else:
        return "Please provide an email address"

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email) or re.search(r"=", email):
        return "Invalid Email Address format"
    # check password
    if b'password' in post:
        password = post[b'password'][0].decode()
    else:
        return "Please enter a password"

    if b'confirmation' in post:
        confirmation = post[b'confirmation'][0].decode()
    else:
        return "Please confirm your password"

    if password != confirmation:
        return "Your password does not match your confirmation password"

    if len(password) < 8:
        return "Your Password must be at least 8 characters long"
    # check first name
    if b'first_name' in post:
        first_name = post[b'first_name'][0].decode()
    else:
        return "Please provide your first name"
    # check last name
    if b'last_name' in post:
        last_name = post[b'last_name'][0].decode()
    else:
        return "Please provide your last name"
    # Validate TOS was checked
    if b'tos' not in post:
        return "You must accept the terms"

    return "";

def _render_success():
    filein = open( '../templates/user/register_success.html' )
    src = Template( filein.read() )
    content = src.safe_substitute({})
    return content

