#!/usr/bin/env python3

from string import Template
from cgi import parse_qs, escape
from utils.wrappers import Request, Response
from werkzeug.utils import redirect
import controller.header
import utils.event_globals as EG
import models
import db.feedback_db
import db.user_db

def render(request):
    environ = request.environ
    dRender = {}
    success = 0
    feedback = models.Feedback()
    u = models.User()
    session = request.client_session

    # Make sure we're not already logged in
    try:
        session['id']
        u = models.User(_id=session['id'])
        db.user_db.get_user(u)
        feedback.submitter_id = u.id
    except KeyError:
        feedback.submitter_id = "Anonymous"

    # get POST
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0

    request_body = environ['wsgi.input'].read(request_body_size)
    dPOST = parse_qs(request_body)

    if b'comment_type' in dPOST and b'comment' in dPOST:
            feedback.comment_type = dPOST[b'comment_type'][0].decode()
            feedback.comment = dPOST[b'comment'][0].decode()
            success = 1
   

    if success == 1:
        if db.feedback_db.create_feedback(feedback) == EG.EVENTS_SUCCESS:
            feedback_content = _render_success()
        else:
            success = 0
            dRender['error_message'] = "We're sorry. There was an error storing your feedback. Please try again."
            dRender['error_class'] = "error_box"
            dRender['comment'] = feedback.comment


    if success == 0:
        feedback_content = _render(dRender)

    filein = open( '../templates/website.html' )
    src = Template( filein.read() )
    header = controller.header.render(request)
    css_includes = "<link rel=\"stylesheet\" type=\"text/css\" href=\"" + EG.DOCUMENT_ROOT + "css/feedback.css\">"
    js_includes = ""
    d = {
           'content':feedback_content,
           'header':header,
           'css_includes':css_includes,
           'js_includes':js_includes,
           'DOCUMENT_ROOT' : EG.DOCUMENT_ROOT,
           'title':"Feedback"}

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

    filein = open( '../templates/feedback.html' )
    src = Template( filein.read() )
    content = src.safe_substitute(d)

    return content


def _render_success():
    filein = open( '../templates/feedback_success.html' )
    src = Template( filein.read() )
    content = src.safe_substitute({})

    return content


if __name__ == "__main__":
    print( _render({}) )
