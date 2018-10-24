from zucleus.client.zuclient import Zuc
import sys

def main():
    if not sys.argv[1:]:
        port = 5000
    else:
        try:
            port = int(sys.argv[1])
        except ValueError:
            port = 5000
        if port > 65535:
            port = 5000

    url = f"http://localhost:{port}/api/v1"
    Z = Zuc(url)
    email = "jared.nishikawa@gmail.com"
    try:
        Z.register(email)
    except Exception as e:
        print(e)
        sys.exit(1)

    r = Z.root()
    print(r)

    v = Z.verify()
    print(v)

    w = Z.whoami()
    print(w)

    d = Z.docs()
    print(d)



