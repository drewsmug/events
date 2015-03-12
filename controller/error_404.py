#!/usr/bin/env python3

from string import Template
from utils.wrappers import Request, Response
import utils.event_globals as EG

def render(request):
    site_content = _render()

    return Response(site_content, mimetype='text/html')

def _render():
    d = {'css_includes':"",
         'js_includes':"",
         'title':"Error 404",
         'DOCUMENT_ROOT':EG.DOCUMENT_ROOT}
    filein = open( '../templates/error_404.html' )
    src = Template( filein.read() )
    content = src.safe_substitute(d)

    #return "my error"
    return content

