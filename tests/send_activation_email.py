#!/usr/bin/env python3

import sys
sys.path.append('../')
sys.path.append('./')
import db.user_db
import models

if len(sys.argv) <= 1:
    print('No email parameter provided')
    sys.exit(-1)

user_email = sys.argv[1]
u = models.User(email=user_email)
db.user_db.get_user(u)
db.user_db.create_deactivated_entry(u)
