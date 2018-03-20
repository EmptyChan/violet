#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import namedtuple


class pipeItem(object):
    def __init__(self, pipenames=[], result=None):
        self.pipenames = pipenames
        self.result = result

    def __call__(self, *args, **kwargs):
        return self.__dict__


Violet = namedtuple('Violet', ['processor', 'request'])
