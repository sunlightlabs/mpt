import os
import urlparse
import pymongo

_db = None

def connect():

    global _db

    if _db is None:

        url = os.environ.get('MONGOHQ_URL')
        u = urlparse.urlparse(url)

        _db = pymongo.Connection(url)[u.path[1:]]

        if u.username and u.password:
            _db.authenticate(u.username, u.password)

    return _db
