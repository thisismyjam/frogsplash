import os
from setuptools import setup

setup(name = 'frogsplash',
      version = '0.1',
      description = 'A minimal logstash subset in Python',
      author = 'Andreas Jansson',
      author_email = 'andreas@jansson.me.uk',
      packages = ['frogsplash', 'grok'],
      install_requires = [
        'regex',
        'argparse',
        'pyinotify',
        'pyes',
        ],
      entry_points = {
        'console_scripts': [
            'frogsplash = frogsplash.frogsplash:main'
            ]
        },
      package_data = {'': ['patterns/*']},
      )
