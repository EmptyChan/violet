""" MRQ """
from gevent import monkey
monkey.patch_all()
import os

import sys

from mrq.context import set_current_config

from_file = {}
config_file = os.path.join(os.getcwd(), "mrq-config.py")
sys.path.insert(0, os.path.dirname(config_file))
config_module = __import__(os.path.basename(config_file.replace(".py", "")))
sys.path.pop(0)
for k, v in config_module.__dict__.items():

    # We only keep variables starting with an uppercase character.
    if k[0].isupper():
        from_file[k.lower()] = v
set_current_config(from_file)