from time import sleep

import connexion

def login_password():
    pass

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

