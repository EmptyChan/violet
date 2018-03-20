# -*- coding: utf-8 -*- 
"""
 Created with IntelliJ IDEA.
 Description:
 User: jinhuichen
 Date: 3/20/2018 3:43 PM 
 Description: 
"""
import os
from importlib import import_module


def load_class(package, clazz, path=None):
    if path is not None:
        module = import_module('{path}'.format(path=path))
        return getattr(module, clazz)
    parent = import_module(package)
    # print(parent.__path__)
    path = os.path.join(parent.__path__[0])
    files = os.listdir(path)
    for file in files:
        if file == '__init__.py':
            continue
        name, *_ = file.split('_', 1)
        if str(name).lower() in clazz.lower():
            module = import_module('{package}.{module}'.format(package=package, module=file.replace('.py', '')))
            return getattr(module, clazz)
    return None