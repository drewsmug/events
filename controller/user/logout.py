#!/usr/bin/env python3

from utils.wrappers import Request, Response
from werkzeug.utils import redirect

def render(request):
    request.client_session.delete = True
    return redirect('/events')

