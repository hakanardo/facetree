import shelve
from time import time
from uuid import uuid4

from werkzeug.security import generate_password_hash, check_password_hash
import connexion
import os
from base64 import b64encode
import string
import random
from utils import send_mail

##################################################################################
#  Indexes
##################################################################################

live_records = {}

def update_live_records(key):
    id, version = key.split(':')
    old_key = live_records.get(id)
    if old_key is None:
        live_records[id] = key
    else:
        _, old_version = old_key.split(':')
        if version > old_version:
            live_records[id] = key

##################################################################################
#  Databases
##################################################################################

users = shelve.open("db/users")
active_tokens = shelve.open("db/active_tokens")
records = shelve.open("db/records")

for key in records.keys():
    update_live_records(key)

# FIXME: Remove expired tokens
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
    message = """
    Hej,
    Du har blivit inbjuden till Petri foto-släktträd på:

        https://facetree.ardoe.net

    Logga in som %s med lösenord %s

        Välkommen!
    """ % (email, password)
    send_mail(email, 'Inbjudan till Petri foto-släktträd', message)
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
# Records
##################################################################################

def post_record(user, record):
    if 'id' in record:
        if len(record['id']) != 36 or ':' in record['id']:
            return 'Id should be 36 chars long and cant contain ":"', 400
    else:
        record['id'] = str(uuid4())
    record['version'] = str(int(time()*1000))
    record['author'] = user['individual']
    key = record['id'] + ':' + record['version']
    records[key] = record
    update_live_records(key)
    records.sync()
    return record

def get_record(id, version):
    key = id + ':' + version
    if key not in records:
        return 'Not found', 404
    return records[key]

def get_latest_record(id):
    if id not in live_records:
        return 'Not found', 404
    return records[live_records[id]]

def list_live_records(user):
    return [records[key] for key in live_records.values()]

def delete_record():
    pass

def get_image():
    pass

def put_image():
    pass

def get_record_updates():
    pass

app = connexion.App(__name__, port=8000)
app.add_api('swagger.yaml')

if __name__ == '__main__':
    app.run()

