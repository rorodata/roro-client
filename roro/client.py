"""The rorodata client
"""
import base64
import firefly
from . import auth

class Client(firefly.Client):
    """Client to roro-server.

    This extends the firefly.Client to support custom Authorization header.
    This is done using a special AuthProvider class, which provides get_auth
    method that returns the saved login details.

    The ``AUTH_PROVIDER`` field which maintains the class of AuthProvider. It
    can be changed to provide alternative implementations of AuthProvider.
    """
    AUTH_PROVIDER = auth.NetrcAuthProvider

    def __init__(self, *args, **kwargs):
        firefly.Client.__init__(self, *args, **kwargs)
        self.auth_provider = self.AUTH_PROVIDER()

    def prepare_headers(self):
        login = self.auth_provider.get_auth()
        if not login:
            return {}

        both = "{}:{}".format(login['email'], login['password']).encode('utf-8')
        basic_auth = base64.b64encode(both).decode("ascii")
        return {
            'Authorization': 'Basic {}'.format(basic_auth)
        }
