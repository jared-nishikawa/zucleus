import requests
import functools
import json

def httpmethod(inner):
    @functools.wraps(inner)
    def wrapped(*args, **kwargs):
        resp = inner(*args, **kwargs)
        resp.raise_for_status()
        try:
            decoded = resp.json()
        except json.decoder.JSONDecodeError as e:
            print(e)
            return resp.content
        return decoded
    return wrapped

class Zuc:
    def __init__(self, url):
        self.url = url
        self.session = requests.Session()

    def root(self):
        route = "/"
        return self._get(route)

    def register(self, email):
        route = "/register"
        resp = self._post(route, json={"email": email})
        cookie = resp['cookie']
        self.session.cookies.update({"cookie": cookie})

    def verify(self):
        route = "/verify"
        return self._post(route)

    def whoami(self):
        route = "/whoami"
        return self._post(route)

    def docs(self):
        route = "/docs"
        return self._get(route)

    @httpmethod
    def _post(self, route, json={}):
        return self.session.post(
                self.url + route,
                json=json)

    @httpmethod
    def _get(self, route):
        return self.session.get(
                self.url + route)


