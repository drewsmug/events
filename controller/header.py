#!/usr/bin/evn python3

from string import Template
import utils.event_globals as EG
import models
import db.user_db

def render(request):
    session = request.client_session
    role = EG.USER_ROLE_GUEST

    try:
        session['id']
        u = models.User(_id=session['id'])
        db.user_db.get_user(u)
        role = u.role
    except Exception:
        pass


    filein = open( '../templates/header/header.html' )

    if role == EG.USER_ROLE_GUEST:
        account = open( '../templates/header/account_guest.html' ).read()
        events = open( '../templates/header/events_guest.html' ).read()
    else:
        account = open( '../templates/header/account_user.html' ).read()
        events = open( '../templates/header/events_user.html' ).read()



    d = {
           'site_name':EG.EVENTS_SITE_NAME,
           'account':account,
           'events':events
        }

    src = Template( filein.read() )
    content = src.safe_substitute(d)
    return content

