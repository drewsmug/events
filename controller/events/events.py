#!/usr/bin/env python3

from string import Template
from utils.wrappers import Request, Response
import controller.events.search
import utils.event_globals as EG

def render(request):
    filein = open( '../templates/website.html' )
    src = Template( filein.read() )

    events_content = _render()
    header = controller.header.render(request)
    css_includes = "<link rel=\"stylesheet\" type=\"text/css\" href=\"" + EG.DOCUMENT_ROOT + "css/event/events.css\">"
    css_includes += "\n\t<link rel=\"stylesheet\" type=\"text/css\" href=\"" + EG.DOCUMENT_ROOT + "css/event/search.css\">"
    js_includes = "<script src=\"" + EG.DOCUMENT_ROOT + "js/find_matching_cities.js\"></script>"
    d = {
           'content':events_content,
           'header':header,
           'css_includes':css_includes,
           'js_includes':js_includes,
           'DOCUMENT_ROOT' : EG.DOCUMENT_ROOT,
           'title':"Events"}

    site_content = src.safe_substitute(d)
    return Response(site_content, mimetype='text/html')

def _render():
    search = controller.events.search.render()
    d = {'search':search}

    filein = open( '../templates/events/events.html' )
    src = Template( filein.read() )
    content = src.safe_substitute(d)

    return content

