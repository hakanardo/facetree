from flask.json import dumps as json_dumps
import requests

class dbImport:
    """database API routines for importing data into database"""
    def __init__(self, serverUrl='http://0.0.0.0:8000', prefix='v1', auth=None):
        if not auth: raise Exception("No user data provided")
        path = "%s/%s/users/login/password" % (serverUrl, prefix)
        self.url = "%s/%s" % (serverUrl, prefix)
        r = requests.post(path, json = auth)
        assert r.status_code == 200
        self.auth = r.json()['token']
        self.authHeader = {"Authorization": "Bearer " + self.auth}

    def create_record(self, data):
        path = "%s/records" % (self.url)
        r = requests.post(path, json = data, headers=self.authHeader)
        assert r.status_code == 200
        return r.json()['id']

    def save_image(self, imageData):
        path = "%s/images" % (self.url)
        hdr = {"Content-Type": "image/jpeg"}
        hdr.update(self.authHeader)
        r = requests.post(path, data = imageData, headers=hdr)
        assert r.status_code == 200
        return r.json()['id']

    def crop_image(self, id, x1, y1, x2, y2):
        path = "%s/images/%s/crop" % (self.url, id)
        r = requests.post(path, json = {"left": x1, "lower": y1, "right": x2, "upper": y2},
                          headers=self.authHeader)
        assert r.status_code == 200
        return r.json()['id']

    def get_records(self):
        path = "%s/records" % (self.url)
        r = requests.get(path, headers=self.authHeader)
        assert r.status_code == 200
        return r

    def get_record(self, id):
        path = "%s/records/%s" % (self.url, id)
        r = requests.get(path, headers=self.authHeader)
        assert r.status_code == 200
        return r.json()


# print(dbImport(auth={"email": "hakan@debian.org", "password": "7tsLKBZo"}).save_image(open("junk/hakan.jpg", "br").read()))
