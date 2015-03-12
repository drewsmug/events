#!/usr/bin/env python3

from string import Template
from cgi import parse_qs, escape
from utils.wrappers import Request, Response
from werkzeug.utils import redirect
from datetime import datetime, date, time
import controller.header
import models
import db.event_db
import utils.event_globals as EG

def render(request):
    environ = request.environ
    dRender = {}
    response_body = ""
    session = request.client_session

    # Make sure we're already logged in
    try:
        session['id']
    except KeyError:
        return redirect('/user/login')

    u = models.User(_id=session['id'])
    db.user_db.get_user(u)
    event_info = models.Event(creator_id=session['id'])

    # get POST
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0

    request_body = environ['wsgi.input'].read(request_body_size)
    dPOST = parse_qs(request_body)


    # Check POST for hidden
    if b'page' in dPOST:
        start_minute = int(dPOST[b'start_minute'][0].decode())
        start_hour = int(dPOST[b'start_hour'][0].decode()) - 1
        start_meridiem = str(dPOST[b'start_meridiem'][0].decode())
        if start_meridiem == "pm":
            start_hour += 12
        end_minute = int(dPOST[b'end_minute'][0].decode())
        end_hour = int(dPOST[b'end_hour'][0].decode()) - 1
        end_meridiem = str(dPOST[b'end_meridiem'][0].decode())
        if end_meridiem == "pm":
            end_hour += 12

        year = int(dPOST[b'year'][0].decode())
        month = int(dPOST[b'month'][0].decode())
        day = int(dPOST[b'day'][0].decode())

        ISOdate = date(year, month, day)
        start_time = time(start_hour, start_minute)
        end_time = time(end_hour, end_minute)
        start_ISO_date = datetime.combine(ISOdate, start_time)
        end_ISO_date = datetime.combine(ISOdate, end_time)

        event_info.title = str(dPOST[b'title'][0].decode())
        event_info.start_time = start_ISO_date
        event_info.end_time = end_ISO_date
        event_info.city = dPOST[b'city'][0].decode()
        event_info.description = str(dPOST[b'description'][0].decode())
        if b'address1' in dPOST:
            event_info.address1= str(dPOST[b'address1'][0].decode())
        if b'address2' in dPOST:
            event_info.address2= str(dPOST[b'address2'][0].decode())
        if b'zip' in dPOST:
            event_info.zip = int(dPOST[b'zip'][0].decode())
        if b'url' in dPOST:
            event_info.website = str(dPOST[b'url'][0].decode())

        # Temp Catagory
        #event_info.categories["music", "food"]
        event_info.categories.append("music")
        event_info.categories.append("food")

        db.event_db.create_event(event_info)

   
    event_content = _render(dRender)

    filein = open( '../templates/website.html' )
    src = Template( filein.read() )
    header = controller.header.render(request)
    css_includes = "<link rel=\"stylesheet\" type=\"text/css\" href=\"" + EG.DOCUMENT_ROOT + "css/event/event_add.css\">"
    js_includes = "<script src=\"" + EG.DOCUMENT_ROOT + "js/find_matching_cities.js\"></script>"
    d = {
           'content':event_content,
           'header':header,
           'css_includes':css_includes,
           'js_includes':js_includes,
           'DOCUMENT_ROOT' : EG.DOCUMENT_ROOT,
           'title':"Create an Event"}

    site_content = src.safe_substitute(d)
    return Response(site_content, mimetype='text/html')

def _render(HEADER):
    d = {
            'site_name':EG.EVENTS_SITE_NAME,
            'error_class':"",
            'error_message':"",
            'title':"",
            'address1':"",
            'address2':"",
            'city':"",
            'zip':"",
            'url':""}

    d.update(HEADER)

    filein = open( '../templates/events/event_add.html' )
    src = Template( filein.read() )
    content = src.safe_substitute(d)

    return content


def _render_success():
    filein = open( '../templates/user/register_success.html' )
    src = Template( filein.read() )
    content = src.safe_substitute({})
    return content

