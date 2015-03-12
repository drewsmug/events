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
        #TODO
        pemail = dPOST[b'email'][0].decode()
        u.email = pemail
        if db.user_db.get_user(u) != EG.EVENTS_SUCCESS:
            retval = "Username or Password is invalid"
	
        if len(retval) == 0 and u.deactivated():
            retval = "This account has not been activated yet. Please check your email."

        if b'password' in dPOST and len(retval) == 0:
            ppassword = dPOST[b'password'][0].decode()
            if u.password_matches(ppassword):
                retval = ""
            else:
                retval = "Username or Password is invalid"

        if len(retval) == 0:
            session = request.client_session
            session['id'] = u.jsonify()
            return redirect('/events')

    if len(str(retval)) > 0:
        if b'email' in dPOST:
            dRender['email'] = dPOST[b'email'][0].decode()
            dRender['error_message'] = retval
            dRender['error_class'] = "error_box"

    filein = open( '../templates/website.html' )
    src = Template( filein.read() )

    login_content = _render(dRender)
    header = controller.header.render(request)
    css_includes = "<link rel=\"stylesheet\" type=\"text/css\" href=\"" + EG.DOCUMENT_ROOT + "css/user/login.css\">"
    js_includes = ""
    d = {
           'content':login_content,
           'header':header,
           'css_includes':css_includes,
           'js_includes':js_includes,
           'DOCUMENT_ROOT' : EG.DOCUMENT_ROOT,
           'title':"Login"}

    site_content = src.safe_substitute(d)
    return Response(site_content, mimetype='text/html')

def _render(HEADER):
    d = {
		    'site_name':EG.EVENTS_SITE_NAME,
		    'error_class':"",
		    'error_message':"",
		    'email':""}
    d.update(HEADER)

    filein = open( '../templates/user/login.html' )
    src = Template( filein.read() )
    content = src.safe_substitute(d)

    return content

