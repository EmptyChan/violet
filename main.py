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
from fetchman.pipeline.pipe_item import CrawlArgs
from processors.tuliu_processor import Tuliu_Processor
from mrq.job import queue_job
# from tasks.spider_task import no_queue_task

if __name__ == '__main__':
    # res = no_queue_task({"processor": Tuliu_Processor.__name__})
    # 启动初始化任务
    res = queue_job(CRAWLER_TASK, CrawlArgs(Tuliu_Processor)(), queue=CRAWLER)
    print(res)