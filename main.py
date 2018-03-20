# -*- coding: utf-8 -*- 
"""
 Created with IntelliJ IDEA.
 Description:
 User: jinhuichen
 Date: 3/19/2018 11:35 AM 
 Description: 
"""
from constants.task_name import CRAWLER_TASK
from constants.queue_name import CRAWLER
from processors.tuliu_processor import Tuliu_Processor
from mrq.job import queue_job


if __name__ == '__main__':
    res = queue_job(CRAWLER_TASK, {"processor": Tuliu_Processor.__name__}, queue=CRAWLER)
    print(res)