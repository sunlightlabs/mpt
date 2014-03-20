#!/usr/bin/env python

import argparse

import bcrypt
import mongo


class User(object):

    def __init__(self, user_id):
        self.id = user_id
        self.authenticated = False
        self.active = False
        self.anonymous = True

    def __str__(self):
        return self.id

    def __repr__(self):
        return '<User: %s>' % self.id

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return self.id is None

    def get_id(self):
        return self.id

    @property
    def is_admin(self):
        return self.is_authenticated() and self.is_active() and not self.is_anonymous()


def add_user(username, password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    db = mongo.connect()
    doc = {
        'username': username,
        'password_hash': hashed,
        'active': True,
    }
    db.users.insert(doc)

def deactivate_user(username):
    db = mongo.connect()
    db.users.update({'username': username}, {'$set': {'active': False}})

def get_user(username, password=None):
    db = mongo.connect()
    doc = db.users.find_one({'username': username})
    if doc:
        user = User(doc['username'])
        user.active = doc.get('active', False)
        if password and valid_password(username, password):
            user.authenticated = True
        return user

def get_users():
    db = mongo.connect()
    return [User(u['username'], is_active=u.get('active', False)) for u in db.users.find()]

def remove_user(username):
    db = mongo.connect()
    db.users.remove({'username': username})

def update_password(username, password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    db = mongo.connect()
    db.users.update({'username': username}, {'$set': {'password_hash': hashed}})

def valid_password(username, password):
    db = mongo.connect()
    user = db.users.find_one({'username': username})
    if user:
        current_hash = user['password_hash'].encode('utf-8')
        return bcrypt.hashpw(password.encode('utf-8'), current_hash) == current_hash


if __name__ == '__main__':

    def add_handler(args):
        print "Adding %s" % args.username
        add_user(args.username, args.password)

    def check_handler(args):
        validity = 'valid' if valid_password(args.username, args.password) else 'INVALID'
        print "Password for %s is %s" % (args.username, validity)

    def list_handler(args):
        users = get_users()
        if users:
            for user in get_users():
                print "%s" % user.id
        else:
            print "*** No users found ***"

    def remove_handler(args):
        remove_user(args.username)

    def update_handler(args):
        update_password(args.username, args.password)

    handlers = {
        'add': add_handler,
        'check': check_handler,
        'list': list_handler,
        'remove': remove_handler,
        'update': update_handler,
    }

    parser = argparse.ArgumentParser(description='Manage users', prog='users.py')

    subparsers = parser.add_subparsers()

    parser_list = subparsers.add_parser('list', help='list users')
    parser_list.set_defaults(action='list')

    parser_add = subparsers.add_parser('add', help='add a user')
    parser_add.add_argument('username')
    parser_add.add_argument('password')
    parser_add.set_defaults(action='add')

    parser_update = subparsers.add_parser('update', help='update password')
    parser_update.add_argument('username')
    parser_update.add_argument('password')
    parser_update.set_defaults(action='update')

    parser_check = subparsers.add_parser('check', help='check password')
    parser_check.add_argument('username')
    parser_check.add_argument('password')
    parser_check.set_defaults(action='check')

    parser_remove = subparsers.add_parser('remove', help='remove user')
    parser_remove.add_argument('username')
    parser_remove.set_defaults(action='remove')

    args = parser.parse_args()

    handler = handlers.get(args.action)
    if handler:
        handler(args)
