from flask import Flask, render_template
from flask_restful import Resource, Api, reqparse

import os
import hmac
import hashlib
import binascii
import functools
import sys
import argparse

app = Flask(__name__)
api = Api(app)

key = os.urandom(64)
version = "v1"
title = "zucleus"

register_parser = reqparse.RequestParser()
register_parser.add_argument('email')

verify_parser = reqparse.RequestParser()
verify_parser.add_argument('cookie', location='cookies')

users = {}

def sign(msg):
    h = hmac.HMAC(key=key, digestmod=hashlib.sha256)
    return h.hexdigest()

def authorized(inner):
    @functools.wraps(inner)
    def wrapped(*args, **kwargs):
        args = verify_parser.parse_args()
        cookie = args.cookie
        user = users.get(cookie)
        if not user:
            return {'message': 'bad cookie'}
        return inner(*args, **kwargs, cookie=cookie)
    return wrapped

def endpoint(name):
    def register_class(inner):
        f_name = '/api/{}{}'.format(version, name)
        api.add_resource(inner, f_name)
        return inner
    return register_class

# API ENDPOINTS

@endpoint('/')
class Root(Resource):
    def get(self):
        return {'message': 'root'}

@endpoint('/register')
class Register(Resource):
    def post(self):
        args = register_parser.parse_args()
        email = args.email
        cookie = sign(email)
        users[cookie] = {"email": email}
        return {'cookie': cookie}

@endpoint('/verify')
class Verify(Resource):
    @authorized
    def post(self, **kwargs):
        return {'message': 'success'}

@endpoint('/whoami')
class Whoami(Resource):
    @authorized
    def post(self, **kwargs):
        cookie = kwargs.get('cookie')
        user = users.get(cookie)
        return {'message': user.get("email")}

@endpoint('/docs')
class Docs(Resource):
    @authorized
    def get(self, **kwargs):
        return {'message': 'docs'}

@endpoint('/users')
class Users(Resource):
    @authorized
    def get(self, **kwargs):
        return {'message': users.values()}

# FRONTEND ENDPOINTS

@app.route('/')
def index():
    kwargs = {"title": title.capitalize()}
    return render_template('index.html', **kwargs)

# MAIN

def parse_args(default_port):
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action="store_true")
    parser.add_argument(
            'port',
            nargs='?',
            default=default_port,
            type=int)
    return parser.parse_args()

def main():
    default_port = 5000
    args = parse_args(default_port)
    port = args.port
    debug = args.debug
    if port > 65535 or port < 1:
        port = default_port

    try:
        app.run(debug=debug, port=port)
    except PermissionError:
        print('Permission denied opening port {}'.format(port))
    except OSError:
        print('Port already in use: {}'.format(port))
