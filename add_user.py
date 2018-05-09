from werkzeug.security import generate_password_hash

from app import  users

def add_user(email, password):
    users[email] = {'email': email, 'individual': '', 'password': generate_password_hash(password)}

if __name__ == '__main__':
    import sys
    add_user(*sys.argv[1:])