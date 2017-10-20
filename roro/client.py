"""The rorodata client
"""
import base64
import firefly
from . import auth

class Client(firefly.Client):
    def prepare_headers(self):
        login = self.get_token()
        if not login:
            return {}

        both = "{}:{}".format(login['email'], login['password']).encode('utf-8')
        basic_auth = base64.b64encode(both).decode("ascii")
        return {
            'Authorization': 'Basic {}'.format(basic_auth)
        }

    def get_token(self):
        """Returns the saved auth token.

        The auth token is read from the netrc file.
        """
        return auth.get_saved_login()
