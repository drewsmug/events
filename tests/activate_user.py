#!/usr/bin/env python3

import sys
sys.path.append('../')
import db.user_db
import models

if len(sys.argv) <= 2:
    print('No email and/or activation parameters provided')
    print(sys.argv[0] + " <email> <activation_code>")
    sys.exit(-1)

user_email = sys.argv[1]
activation_key = sys.argv[2]

print("Using email=" + user_email + ", activation_key=" + activation_key)

u = models.User(email=user_email)
db.user_db.get_user(u)
rc = db.user_db.activate_user(u, activation_key)

print("rc = " + str(rc))
