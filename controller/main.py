#!/usr/bin/env python3

from string import Template

import os, sys
sys.path.append('../')
from utils.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.wsgi import SharedDataMiddleware
import utils.event_globals as EG
import controller.user
import controller.events
import controller.index
import controller.terms
import controller.find_matching_cities
import controller.feedback
import controller.about

class EventsDispatcher(object):
    def __init__(self):
        self.url_map = Map([
            Rule('/', endpoint='index'),
            Rule('/find_matching_cities', endpoint='find_matching_cities'),
            Rule('/feedback', endpoint='feedback'),
            Rule('/user/<path:url_path>', endpoint='user'),
            Rule('/events', endpoint='events'),
            Rule('/events/<path:url_path>', endpoint='events'),
            Rule('/terms', endpoint='terms'),
            Rule('/about', endpoint='about'),
        ])

    def on_user(self, request, url_path):
        return controller.user.dispatch(request, url_path)

    def on_events(self, request, url_path=None):
        return controller.events.dispatch(request, url_path)

    def on_index(self, request):
        return controller.index.render(request)

    def on_activate(self, request):
        return CUA.render(request)

    def on_login(self, request, path):
        return CULI.render(request)

    def on_logout(self, request):
        return CULO.render(request)

    def on_profile(self, request):
        return CUP.render(request)

    def on_register(self, request):
        return CUR.render(request)

    def on_terms(self, request):
        return controller.terms.render(request)

    def on_about(self, request):
        return controller.about.render(request)

    def on_find_matching_cities(self, request):
        return controller.find_matching_cities.render(request)

    def on_feedback(self, request):
        return controller.feedback.render(request)

    def on_forgot_password(self, request):
        return CUF.render(request)

    def on_recovery(self, request):
        return CUREC.render(request)

    def on_update_email(self, request):
        return CUU.render(request)

    def on_reset_email(self, request):
        return CURE.render(request)

    def error_404(self, request):
        return controller.error_404.render(request)

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, 'on_' + endpoint)(request, **values)
        except NotFound as e:
            return self.error_404(request)
        except HTTPException as e:
            return e

    def wsgi_app(self, environ, start_response):
        try:
            os.environ['SITE_SUB_DOMAIN'] = environ['SITE_SUB_DOMAIN']
        except KeyError:
            os.environ['SITE_SUB_DOMAIN'] = os.environ['USER']

        request = Request(environ)
        response = self.dispatch_request(request)

        # Save off cookie if necessary
        if request.client_session.should_save:
            session_data = request.client_session.serialize()
            response.set_cookie(EG.SESSION_COOKIE_NAME, session_data, httponly=True)
        if request.client_session.delete:
            response.delete_cookie(EG.SESSION_COOKIE_NAME)

        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

def create_app(with_media=True):
    app = EventsDispatcher()
    if with_media:
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
            EG.DOCUMENT_ROOT:  os.path.join(os.path.dirname(__file__), EG.DOCUMENT_ROOT)
        })
    return app

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    EG.DOCUMENT_ROOT = os.environ['HOME'] + '/events/documents' + EG.DOCUMENT_ROOT
    app = create_app()
    run_simple('172.31.10.0', 5000, app, use_debugger=True, use_reloader=True)
else:
    application = create_app()

