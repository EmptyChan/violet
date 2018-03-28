#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from collections import namedtuple

from fetchman.processor.base_processor import BaseProcessor


class PipeItem(object):
    def __init__(self, pipe_names=None, result=None):
        if pipe_names is None:
            pipe_names = []
        self.pipe_names = pipe_names
        self.result = result

    def __call__(self, *args, **kwargs):
        return self.__dict__


class CrawlArgs(object):
    def __init__(self, processor, request=None):
        if issubclass(processor, BaseProcessor):
            processor = processor.__name__
        self._processor = processor
        self._request = request

    def __call__(self, *args, **kwargs):
        result = {
            'processor': self._processor,
            'request': self._request
        }
        if self._request is None:
            del result['request']
        return result

    def __str__(self):
        result = {
            'processor': self._processor,
            'request': self._request
        }
        if self._request is None:
            del result['request']
        content = json.dumps(result, ensure_ascii=False)
        return content

    __repr__ = __str__


class PipelineArgs(object):
    def __init__(self, pipeline, result):
        self._pipeline = pipeline
        self._result = result

    def __call__(self, *args, **kwargs):
        return {
            'pipeline': self._pipeline,
            'result': self._result
        }

    def __str__(self):
        content = json.dumps({
            'pipeline': self._pipeline,
            'result': self._result
        }, ensure_ascii=False)
        return content

    __repr__ = __str__


Violet = namedtuple('Violet', ['processor', 'request'])
