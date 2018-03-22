# -*- coding: utf-8 -*- 
"""
 Created with IntelliJ IDEA.
 Description:
 User: jinhuichen
 Date: 3/19/2018 2:53 PM 
 Description: 
"""
from constants.pipeline_name import PIPEINE_MAP
from fetchman.utils.reqser import request_from_dict

from fetchman.spider.spider_core import SpiderCore
from fetchman.utils.decorator import timeit
from mrq.context import log
from mrq.task import Task
from common_utils import load_class


class CrawlTask(Task):

    @timeit
    def run(self, params):
        log.info("crawl..........%s")
        # {'processor': item.processor, 'request': item.request}
        processor = params.get('processor', None)
        request = params.get('request', None)
        if processor is not None:
            clazz = load_class('processors', processor)
            processor_instance = clazz()
            if request is not None:
                request = request_from_dict(request, processor_instance)
                # print(request)
                processor_instance.set_start_requests([request])
            SpiderCore(processor_instance, time_sleep=1).start()
            print('****************complete')


class PipelineTask(Task):

    @timeit
    def run(self, params):
        log.info("pipeline..........")
        # {'processor': item.processor, 'request': item.request}
        pipeline = params.get('pipeline', None)
        result = params.get('result', None)
        if pipeline is not None:
            clazz = PIPEINE_MAP.get(pipeline)
            clazz().process_item(result)
            print('--------------------complete')


if __name__ == '__main__':
    clazz = load_class('processors', 'Tuliu_Detail_Processor')
    print(clazz)