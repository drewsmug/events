#!/usr/bin/env python3

from string import Template
from utils.wrappers import Request, Response
import controller.events.search as CES
import controller.header
import utils.event_globals as EG

def render(request):
    filein = open( '../templates/website.html' )
    src = Template( filein.read() )

    index_content = _render()
    header = controller.header.render(request)
    css_includes = "<link rel=\"stylesheet\" type=\"text/css\" href=\"" + EG.DOCUMENT_ROOT + "css/event/search.css\">"
    css_includes += "\n\t<link rel=\"stylesheet\" type=\"text/css\" href=\"" + EG.DOCUMENT_ROOT + "css/index.css\">"
    js_includes = "<script src=\"" + EG.DOCUMENT_ROOT + "js/find_matching_cities.js\"></script>"
    d = {
           'content':index_content,
           'header':header,
           'css_includes':css_includes,
           'js_includes':js_includes,
           'DOCUMENT_ROOT' : EG.DOCUMENT_ROOT,
           'title':EG.EVENTS_SITE_NAME}

    site_content = src.safe_substitute(d)
    return Response(site_content, mimetype='text/html')

def _render():
    search =CES.render()
    d = {'search':search,'site_name':EG.EVENTS_SITE_NAME}

    filein = open( '../templates/index.html' )
    src = Template( filein.read() )
    content = src.safe_substitute(d)

    #return "Hello Andy"
    return content

