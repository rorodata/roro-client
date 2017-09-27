import os
import sys
import stat
from netrc import netrc as _netrc
import firefly
from . import config
from .helpers import get_host_name, PY2

def login(email, password):
    token = just_login(email, password)
    save_token(email, token)

def just_login(email, password):
    client = firefly.Client(config.SERVER_URL)
    token = client.login(email=email, password=password)
    return token

def whoami():
    client = firefly.Client(config.SERVER_URL)
    return client.whoami()

def get_saved_login():
    create_netrc_if_not_exists()
    rc = netrc()

    hostname = get_host_name(config.SERVER_URL)
    if hostname in rc.hosts:
        login, _, password = rc.hosts[hostname]
        return {
            "email": login,
            "password": password
        }

def save_token(email, token):
    netrc_file = create_netrc_if_not_exists()
    rc = netrc()
    with open(netrc_file, 'w') as f:
        host_name = get_host_name(config.SERVER_URL)
        if PY2:
            email = email.encode('utf-8')
            token = token.encode('utf-8')
        rc.hosts[host_name] = (email, None, token)
        f.write(str(rc))

def create_netrc_if_not_exists():
    prefix = '.' if os.name != 'nt' else '_'
    netrc_file = os.path.join(os.path.expanduser('~'), prefix+'netrc')
    # theese flags works both on windows and linux according to this stackoverflow
    # https://stackoverflow.com/questions/27500067/chmod-issue-to-change-file-permission-using-python#27500153
    if not os.path.exists(netrc_file):
        with open(netrc_file, 'w'):
            pass
        os.chmod(netrc_file, stat.S_IREAD|stat.S_IWRITE)
    return netrc_file

class netrc(_netrc):
    """Extended the netrc from standard library to fix an issue.

    See https://github.com/python/cpython/pull/2491
    """
    def __init__(self, file=None):
        # The stdlib netrc doesn't find the right netrc file by default
        # work-around to fix that
        if file is None:
            file = self.find_default_file()
        _netrc.__init__(self, file=file)

    def find_default_file(self):
        filename = "_netrc" if sys.platform == 'win32' else ".netrc"
        p = os.path.join(os.path.expanduser('~'), filename)
        return str(p)

    def __repr__(self):
        """Dump the class data in the format of a .netrc file."""
        rep = ""
        for host in self.hosts.keys():
            attrs = self.hosts[host]
            rep = rep + "machine "+ host + "\n\tlogin " + attrs[0] + "\n"
            if attrs[1]:
                rep = rep + "account " + attrs[1]
            rep = rep + "\tpassword " + attrs[2] + "\n"
        for macro in self.macros.keys():
            rep = rep + "macdef " + macro + "\n"
            for line in self.macros[macro]:
                rep = rep + line
            rep = rep + "\n"
        return rep
