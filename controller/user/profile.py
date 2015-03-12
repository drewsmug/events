#!/usr/bin/env python3

from string import Template
from cgi import parse_qs, escape
from utils.wrappers import Request, Response
from werkzeug.utils import redirect
import controller.header
import db.user_db
import models
import utils.event_globals as EG

def render(request):
    environ = request.environ   
    dRender = {'error_message':""}
    session = request.client_session

    # Make sure we are logged in
    try:
        session['id']
    except KeyError:
        return redirect('/user/login')

    u = models.User(_id=session['id'])
    db.user_db.get_user(u)

    # get POST
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0

    request_body = environ['wsgi.input'].read(request_body_size)
    dPOST = parse_qs(request_body)

    #if b'profile' in dPOST:
        # Validate email
    #if b'email' in dPOST:
    #    pemail = dPOST[b'email'][0].decode()
    #    if u.validate_email(pemail) == EG.EVENTS_SUCCESS:
    #        u.email = pemail
    #    else:
    #        dRender['error_message'] = "This email address is not valid"
    #        dRender['error_class'] = "error_box"
    if b'first_name' in dPOST:
        pfirst_name = dPOST[b'first_name'][0].decode()
        u.first_name = pfirst_name
    if b'last_name' in dPOST:
        plast_name = dPOST[b'last_name'][0].decode()
        u.last_name = plast_name


    # Update Password
    # Ensure all fields required to update the password are provided
    # There is probably a better way to do this
    if b'curr_password' in dPOST and (b'new_password' not in dPOST or b'new_password_confirm' not in dPOST):
        dRender['error_message'] = "To change your password you must 1) enter your current password 2) choose your new password and 3) confirm your new password"
        dRender['error_class'] = "error_box"
    if b'new_password' in dPOST and (b'curr_password' not in dPOST or b'new_password_confirm' not in dPOST):
        dRender['error_message'] = "To change your password you must 1) enter your current password 2) choose your new password and 3) confirm your new password"
        dRender['error_class'] = "error_box"
    if b'new_password_confirm' in dPOST and (b'new_password' not in dPOST or b'curr_password' not in dPOST):
        dRender['error_message'] = "To change your password you must 1) enter your current password 2) choose your new password and 3) confirm your new password"
        dRender['error_class'] = "error_box"

    # Validate curr password is accurate
    if len(dRender['error_message']) == 0 and b'curr_password' in dPOST:
        pcurr_password = dPOST[b'curr_password'][0].decode()
        if not u.password_matches(pcurr_password):
            #dRender['error_message'] = "You have entered an incorrect current password"
            dRender['error_message'] = "The current password you have entered is incorrect"
            dRender['error_class'] = "error_box"

    # Validate new password meets requirements
    if len(dRender['error_message']) == 0 and b'new_password' in dPOST:
        pnew_password = dPOST[b'new_password'][0].decode()
        if u.validate_password(pnew_password):
            u.password = pnew_password
            u.hash_my_password()
        else:
            dRender['error_message'] = "Your new password must be at least 8 characters long"
            dRender['error_class'] = "error_box"

    # Validate new password and confirmation match
    if len(dRender['error_message']) == 0 and b'new_password' in dPOST and dPOST[b'new_password'][0].decode() != dPOST[b'new_password_confirm'][0].decode():
        dRender['error_message'] = "Please check that your passwords match and try again"
        dRender['error_class'] = "error_box"

    # Every thing looks good. Save info
    if len(dRender['error_message']) == 0 and b'page' in dPOST:
        db.user_db.update_user(u)
        dRender['error_message'] = "Your new Account information has been saved"
        dRender['error_class'] = "success_box"


    #dRender['email'] = u.email
    dRender['first_name'] = u.first_name
    dRender['last_name'] = u.last_name


    filein = open( '../templates/website.html' )
    src = Template( filein.read() )

    profile_content = _render(dRender)
    header = controller.header.render(request)
    css_includes = "<link rel=\"stylesheet\" type=\"text/css\" href=\"" + EG.DOCUMENT_ROOT + "css/event/search.css\">"
    css_includes += "\n\t<link rel=\"stylesheet\" type=\"text/css\" href=\"" + EG.DOCUMENT_ROOT + "css/user/profile.css\">"
    js_includes = ""
    d = {
           'content':profile_content,
           'header':header,
           'css_includes':css_includes,
           'js_includes':js_includes,
           'DOCUMENT_ROOT' : EG.DOCUMENT_ROOT,
           'title':"Edit Account Profile"}

    site_content = src.safe_substitute(d)
    return Response(site_content, mimetype='text/html')

def _render(HEADER):
    d = {
            'site_name':EG.EVENTS_SITE_NAME,
            'error_class':"",
            'error_message':"",
            'first_name':"",
            'last_name':"",}

    d.update(HEADER)

    filein = open( '../templates/user/profile.html' )
    src = Template( filein.read() )
    content = src.safe_substitute(d)

    return content

