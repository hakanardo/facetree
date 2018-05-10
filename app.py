import shelve
from io import BytesIO
from threading import Condition
from time import time
from uuid import uuid4

from werkzeug.security import generate_password_hash, check_password_hash
import connexion
from flask_cors import CORS
import os
from base64 import b64encode
import string
import random
from utils import send_mail

from PIL import Image
Image.MAX_IMAGE_PIXELS = None

##################################################################################
#  Indexes
##################################################################################

live_records = {}
history = []
history_condition = Condition()

def update_indexes(record):
    # history
    with history_condition:
        record['version'] = str(int(time() * 1000)) # To make sure history becomes sorted by version
        history.append(record)
        history_condition.notify_all()

    # live_records
    id = record['id']
    old = live_records.get(id)
    if old is None:
        live_records[id] = record
    else:
        if record['version'] >= old['version']:
            if record['type'] == '__DELETED__':
                del live_records[id]
            else:
                live_records[id] = record


##################################################################################
#  Databases
##################################################################################

users = shelve.open("db/users")
active_tokens = shelve.open("db/active_tokens")
records = shelve.open("db/records")

for _, rec in sorted(records.items()):
    update_indexes(rec)

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
    if 'version' in record:
        record['prev_version'] = record['version']
    record['author'] = user['email']
    update_indexes(record)
    key = record['version'] + ':' + record['id']
    records[key] = record
    records.sync()
    return record

def get_record(id, version):
    key = version + ':' + id
    if key not in records:
        return 'Not found', 404
    return records[key]

def get_latest_record(id):
    if id not in live_records:
        return 'Not found', 404
    return live_records[id]

def list_live_records(user):
    return [rec for rec in live_records.values()]

def delete_record(user, id):
    record = get_latest_record(id)
    record = {'id': record['id'], 'version': record['version'], 'type': '__DELETED__'}
    post_record(user, record)
    return "Deleted"

def get_record_history(before, limit):
    if before == 'NOW':
        before = len(history)
    else:
        before = int(before)
    nxt = max(before - int(limit), 0)
    res = {'records': history[nxt:before][::-1]}
    if nxt > 0:
        res['before'] = str(nxt)
    return res

def get_record_updates(since):
    if since == 'NOW':
        since = len(history)
    else:
        since = int(since)
    if len(history) <= since:
        with history_condition:
            if len(history) <= since:
                history_condition.wait(100)
    recs = history[since:]
    return {'records': recs, 'since': str(since + len(recs))}


##################################################################################
# Images
##################################################################################

def post_image(image):
    if not isinstance(image, Image.Image):
        if len(image) == 0:
            return "No (or empty) image provided.", 400
        try:
            Image.open(BytesIO(image))
        except OSError:
            return "Image format not recogniced.", 400
    id = str(uuid4())
    dn = "db/images/%s" % id
    if os.path.exists(dn):
        return post_image(image) # Retry
    os.mkdir(dn)
    fn = os.path.join(dn, "original.jpg")
    if isinstance(image, Image.Image):
        image.save(fn)
    else:
        with open(fn, "wb") as fd:
            fd.write(image)
    return {'id': id}

def image_crop(id, box):
    img = Image.open("db/images/%s/original.jpg" % (id))
    img = img.crop((box["left"], box["upper"], box["right"], box["lower"]))
    return post_image(img)

image_sizes = {"thumb": 256, "full": 1024}
def get_image(id, width):
    if width in image_sizes:
        width = image_sizes[width]
    fn = "db/images/%s/%s.jpg" % (id, width)
    if not os.path.exists(fn):
        img = Image.open("db/images/%s/original.jpg" % (id))
        w, h = img.size
        width = int(width)
        img = img.resize((width, int(h * width / w)))
        img.save(fn)
    with open(fn, "rb") as fd:
        return fd.read()



##################################################################################
# App
##################################################################################

app = connexion.App(__name__, port=8000)
app.add_api('swagger.yaml')
CORS(app.app)

if __name__ == '__main__':
    app.run()

