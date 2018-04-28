import shelve
from time import time

from werkzeug.security import generate_password_hash, check_password_hash
import connexion
import os
from base64 import b64encode
import string
import random

##################################################################################
#  Databases
##################################################################################

users = shelve.open("db/users")
active_tokens = shelve.open("db/active_tokens")

# FIXME: Remove expired tokens
# FIXME: Mail invites
# FIXME: Mode without auth for setting things up


##################################################################################
# User handling
##################################################################################

def login_password(credentials):
    uid = credentials['email']
    if uid in users:
        if check_password_hash(users[uid]['password'], credentials['password']):
            token = b64encode(os.urandom(32))[:-1].decode('utf-8')
            active_tokens[token] = {'uid': uid, 'expires': time() + 48*60*60}
            active_tokens.sync()
            return {'token': token}
    return 'Unauthorized', 401

def token_info(token):
    token_data = active_tokens.get(token)
    if token_data is not None:
        uid = token_data['uid']
        return {'uid': users[uid], 'scope': ['user']}

def user_invite(who):
    email = who['email']
    individual = who['individual']
    password = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(8))
    print(password)
    users[email] = {'email': email, 'individual': individual, 'password': generate_password_hash(password)}
    users.sync()
    return "Invitation sent"

def user_password(user, passwords):
    if not check_password_hash(user['password'], passwords['old']):
        return "Unauthorized", 401
    user['password'] = generate_password_hash(passwords['new'])
    users[user['email']] = user
    users.sync()
    return "Password changed"

##################################################################################

def list_live_records(user):
    print(user)

def get_latest_record():
    pass

def get_record():
    pass

def put_record():
    pass

def delete_record():
    pass

def get_image():
    pass

def put_image():
    pass

def get_record_updates():
    pass



if __name__ == '__main__':
    app = connexion.App(__name__, port=8000)
    app.add_api('swagger.yaml')
    app.run()

