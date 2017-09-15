"""The rorodata client
"""
import base64
import firefly
from . import auth

class Client(firefly.Client):
    def prepare_headers(self):
        login = auth.get_saved_login()
        if not login:
            return {}

        both = "{}:{}".format(login['email'], login['password']).encode('utf-8')
        basic_auth = base64.b64encode(both).decode("ascii")
        return {
            'Authorization': 'Basic {}'.format(basic_auth)
        }

