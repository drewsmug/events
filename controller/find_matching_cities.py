#!/usr/bin/env python3

from string import Template
from cgi import parse_qs, escape
from utils.wrappers import Request, Response
import controller.header
import db.city_db
import utils.event_globals as EG

def render(request):
    environ = request.environ
    site_content = ""

    # get POST
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0

    request_body = environ['wsgi.input'].read(request_body_size)
    dPOST = parse_qs(request_body)

    if b'city' in dPOST:
        pcity = dPOST[b'city'][0].decode()
        results = db.city_db.get_city(pcity, 10)
        if results:
            site_content = format_results(results)

    return Response(site_content, mimetype='text/html')

def format_results(results):
    if results.count() == 0:
        return ""

    content = '<ul id="list_of_cities">'
    for result in results:
        city_string = result['name'] + ", " + result['state']
        content += '<li onclick="insert_city_from_dropdown('
        content += "'" + city_string + "'"
        content += ')">'
        content += result['name']
        content += ", "
        content += result['state']
        content += '</li>'

    content += "</ul>"

    return content

