def application(environ, start_response):
    """"Simplest possible application object"""
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return ['Hello, World! This is event.wsgi Python 3 WSGI in public_html\n']
