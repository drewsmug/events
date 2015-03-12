#!/usr/bin/env python3

from string import Template
from utils.wrappers import Request, Response
import controller.header
import utils.event_globals as EG

def render(request):
    filein = open( '../templates/website.html' )
    src = Template( filein.read() )

    terms_content = _render()
    header = controller.header.render(request)
    css_includes = "<link rel=\"stylesheet\" type=\"text/css\" href=\"" + EG.DOCUMENT_ROOT + "css/search.css\">"
    css_includes += "\n\t<link rel=\"stylesheet\" type=\"text/css\" href=\"" + EG.DOCUMENT_ROOT + "css/terms.css\">"
    js_includes = ""
    d = {
           'content':terms_content,
           'header':header,
           'css_includes':css_includes,
           'js_includes':js_includes,
           'DOCUMENT_ROOT' : EG.DOCUMENT_ROOT,
           'title':"Terms of Service"}

    site_content = src.safe_substitute(d)
    return Response(site_content, mimetype='text/html')

def _render():
    d = { 'site_name':EG.EVENTS_SITE_NAME }
    filein = open( '../templates/terms.html' )
    src = Template( filein.read() )
    content = src.safe_substitute(d)

    return content

