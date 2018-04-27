from werkzeug.security import generate_password_hash, check_password_hash
import connexion
import os
from base64 import b64encode

users = {'hakan@debian.org': {'password': generate_password_hash('pass')}}
active_tokens = {}

def login_password(credentials):
    uid = credentials['email']
    if uid in users:
        if check_password_hash(users[uid]['password'], credentials['password']):
            token = b64encode(os.urandom(32))[:-1].decode('utf-8')
            active_tokens[token] = uid
            return {'token': token}
    return 'Unauthorized', 401

def list_live_records():
    pass

def get_latest_record():
    pass

def get_record():
    pass

def put_record():
    pass

def delete_record():
    pass

def token_info():
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

