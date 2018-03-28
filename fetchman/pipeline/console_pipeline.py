#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from fetchman.pipeline.base_pipeline import ItemPipeline
import json


class ConsolePipeline(ItemPipeline):
    def process_item(self, item):
        self.logger.info('enter')
        if sys.version_info < (3, 0):
            print(json.dumps(item).decode("unicode-escape"))
        else:
            print(json.dumps(item).encode('utf8').decode("unicode-escape"))
        self.logger.info('exit')
