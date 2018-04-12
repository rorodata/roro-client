"""
roro
----

The client interface to the rorodata platform.

Install
~~~~~~~

It can be installed using pip.

..code:: bash

    $ pip install roro

Links
~~~~~

* `Documentation <https://rorodata.com/docs/>`_
* `Github <https://github.com/rorodata/roro-client>`_
"""

from setuptools import setup, find_packages
import os.path
import sys
import re

PY2 = (sys.version_info.major == 2)

def get_version():
    """Returns the package version taken from version.py.
    """
    root = os.path.dirname(__file__)
    version_path = os.path.join(root, "roro/__init__.py")
    text = open(version_path).read()
    rx = re.compile("^__version__ = '(.*)'", re.M)
    m = rx.search(text)
    version = m.group(1)
    return version

install_requires = [
    'firefly-python>=0.1.9',
    'click>=6.7',
    'tabulate>=0.7.7',
    'PyYAML>=3.12',
    'joblib>=0.11',
]

if PY2:
    install_requires.append('pathlib>=1.0.1')
    install_requires.append('backports.tempfile')

__version__ = get_version()

setup(
    name='roro',
    version=__version__,
    author='rorodata',
    author_email='rorodata.team@gmail.com',
    description='The client interface to the rorodata platform',
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    entry_points='''
        [console_scripts]
        roro = roro.cli:cli
    ''',
)
