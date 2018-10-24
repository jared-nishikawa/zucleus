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
        api.add_resource(inner, name)
        return inner
    return register_class

# API ENDPOINTS

@endpoint('/api/{}/'.format(version))
class Root(Resource):
    def get(self):
        return {'message': 'root'}

@endpoint('/api/{}/register'.format(version))
class Register(Resource):
    def post(self):
        args = register_parser.parse_args()
        email = args.email
        cookie = sign(email)
        users[cookie] = {"email": email}
        return {'cookie': cookie}

@endpoint('/api/{}/verify'.format(version))
class Verify(Resource):
    @authorized
    def post(self, **kwargs):
        return {'message': 'success'}

@endpoint('/api/{}/whoami'.format(version))
class Whoami(Resource):
    @authorized
    def post(self, **kwargs):
        cookie = kwargs.get('cookie')
        user = users.get(cookie)
        return {'message': user.get("email")}

@endpoint('/api/{}/docs'.format(version))
class Docs(Resource):
    @authorized
    def get(self, **kwargs):
        return {'message': 'docs'}

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
        print(f"Permission denied opening port {port}")
    except OSError:
        print(f"Port already in use: {port}")
