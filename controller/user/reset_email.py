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
    success = 0
    session = request.client_session

    # get GET
    dGET = parse_qs(environ['QUERY_STRING'])
    if "key" in dGET:
        dRender['key'] = dGET['key'][0]

    if "key" in dGET and 'error_message' not in dRender:
        rc = db.user_db.reset_email(dGET['key'][0])
        if rc == EG.EVENTS_SUCCESS:
            success = 1
        if rc == EG.EVENTS_ERROR:
            dRender['error_message'] = "We do not have anything that matches this new email address and activation key"
            dRender['error_class'] = "error_box"

    filein = open( '../templates/website.html' )
    src = Template( filein.read() )

    if success == 0:
        activate_content = _render(dRender)
    else:
        activate_content = _render_success()

    header = controller.header.render(request)
    css_includes = "<link rel=\"stylesheet\" type=\"text/css\" href=\"" + EG.DOCUMENT_ROOT + "css/user/reset_email.css\">"
    js_includes = ""
    d = {
           'content':activate_content,
           'header':header,
           'css_includes':css_includes,
           'js_includes':js_includes,
           'DOCUMENT_ROOT' : EG.DOCUMENT_ROOT,
           'title':"Reset Email"}

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

    filein = open( '../templates/user/reset_email.html' )
    src = Template( filein.read() )
    content = src.safe_substitute(d)
    return content


def _render_success():
    filein = open( '../templates/user/reset_email_success.html' )
    src = Template( filein.read() )
    content = src.safe_substitute({})
    return content

