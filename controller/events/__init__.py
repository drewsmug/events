from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from . import events
from . import event_add
import controller.error_404

url_map = Map([
                Rule('/events', endpoint='events'),
                Rule('/events/add', endpoint='event_add'),
              ])

def dispatch(request, path):
    adapter = url_map.bind_to_environ(request.environ)
    try:
        endpoint, values = adapter.match()
        return getattr(controller.events, 'on_' + endpoint)(request, **values)
    except NotFound as e:
        return error_404(request)
    except HTTPException as e:
        return e

def on_events(request):
    return events.render(request)

def on_event_add(request):
    return event_add.render(request)

def error_404(request):
    return controller.error_404.render(request)
