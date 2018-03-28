#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fetchman.utils import FetchManLogger


class ItemPipelineMeta(type):
    def __new__(cls, name, bases, attrs):
        if name == 'ItemPipeline':
            return super().__new__(cls, name, bases, attrs)
        attrs['logger'] = FetchManLogger.init_logger(name)
        return super().__new__(cls, name, bases, attrs)


class ItemPipeline(metaclass=ItemPipelineMeta):
    def process_item(self, item):
        raise NotImplementedError
