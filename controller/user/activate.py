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
    dRender = {}
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

    if "email" in dGET and "key" in dGET and 'error_message' not in dRender:
        rc = db.user_db.activate_user(user, dGET['key'][0])
        if rc == EG.EVENTS_SUCCESS:
            success = 1
        if rc == EG.EVENTS_USER_NOT_FOUND:
            dRender['error_message'] = "We do not have an account to activate for this email address"
            dRender['error_class'] = "error_box"
        if rc == EG.EVENTS_WRONG_ACTIVATION_KEY:
            dRender['error_message'] = "That is not the correct Activation Key for this account"
            dRender['error_class'] = "error_box"


    filein = open( '../templates/website.html' )
    src = Template( filein.read() )

    if success == 0:
        activate_content = _render(dRender)
    else:
        activate_content = _render_success()

    header = controller.header.render(request)
    css_includes = "<link rel=\"stylesheet\" type=\"text/css\" href=\"" + EG.DOCUMENT_ROOT + "css/user/activate_user.css\">"
    js_includes = ""
    d = {
           'content':activate_content,
           'header':header,
           'css_includes':css_includes,
           'js_includes':js_includes,
           'DOCUMENT_ROOT' : EG.DOCUMENT_ROOT,
           'title':"Activate"}

    site_content = src.safe_substitute(d)
    return Response(site_content, mimetype='text/html')

def _render(HEADER):
    d = {
		    'error_class':"",
		    'error_message':"",
		    'email':"",
                    'key':"",
                    'site_name':EG.EVENTS_SITE_NAME}
    d.update(HEADER)

    filein = open( '../templates/user/activate_user.html' )
    src = Template( filein.read() )
    content = src.safe_substitute(d)
    return content


def _render_success():
    filein = open( '../templates/user/activation_success.html' )
    src = Template( filein.read() )
    content = src.safe_substitute({})
    return content

