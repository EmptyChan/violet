# -*- coding: utf-8 -*- 
"""
 Created with IntelliJ IDEA.
 Description:
 User: jinhuichen
 Date: 3/19/2018 2:53 PM 
 Description: 
"""
import time
from mrq.context import log
from mrq.task import Task


class CrawlTask(Task):

    def run(self, params):
        log.info("adding", params)
        res = params.get("a", 0) + params.get("b", 0)

        if params.get("sleep", 0):
            log.info("sleeping", params.get("sleep", 0))
            time.sleep(params.get("sleep", 0))

        return res