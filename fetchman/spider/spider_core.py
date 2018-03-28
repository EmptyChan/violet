#!/usr/bin/env python
# -*- coding: utf-8 -*-
import types

from mrq.job import queue_job

from fetchman.downloader.http.spider_request import Request
from fetchman.downloader.requests_downloader import RequestsDownLoader
from fetchman.pipeline.pipe_item import PipeItem, Violet, CrawlArgs, PipelineArgs
from fetchman.scheduler.queue import PriorityQueue
from fetchman.utils.httpobj import urlparse_cached
from fetchman.downloader.selenium_downloader import SeleniumDownLoader
from fetchman.settings import default_settings
from constants.queue_name import CRAWLER, PIPELINE
from constants.task_name import CRAWLER_TASK, PIPELINE_TASK
# import uuid
import re
import time
import traceback


def _priority_compare(r1, r2):
    return r2.priority - r1.priority


def _priority_compare_key(item):
    return item.priority


class SpiderCore(object):
    def __init__(self, processor=None, downloader=None, use_proxy=False, scheduler=None, batch_size=None,
                 time_sleep=None, test=False):
        # 用于测试,爬取成功第一个以后结束
        self.test = test
        self._processor = processor
        self._host_regex = self._get_host_regex()
        self._spider_status = 'stopped'
        # self._pipelines = {}
        self._time_sleep = time_sleep
        self._batch_size = 1
        if time_sleep:
            self._batch_size = 1
        else:
            if isinstance(downloader, SeleniumDownLoader):
                self._batch_size = default_settings.DRIVER_POOL_SIZE - 1
            else:
                if batch_size:
                    self._batch_size = batch_size
                else:
                    self._batch_size = 10
        self._spider_id = processor.spider_id
        self._process_count = 0

        if not downloader:
            self._downloader = RequestsDownLoader(use_proxy=use_proxy)
        elif isinstance(downloader, SeleniumDownLoader):
            self._downloader = downloader
            self._batch_size = default_settings.DRIVER_POOL_SIZE - 1
        else:
            self._downloader = downloader

        if not scheduler:
            self._queue = PriorityQueue(self._processor)
        else:
            self._queue = scheduler

    def create(self, processor):
        self._processor = processor
        return self

    def set_scheduler(self, scheduler):
        self._queue = scheduler
        return self

    def set_downloader(self, downloader):
        self._downloader = downloader
        if isinstance(downloader, SeleniumDownLoader):
                self._batch_size = default_settings.DRIVER_POOL_SIZE - 1
        return self

    def stop(self):
        if self._spider_status == 'stopped':
            self._processor.logger.info("STOP %s SUCCESS" % self._spider_id)
            return
        elif self._spider_status == 'stopping':
            while self._spider_status == 'stopping':
                pass
        elif self._spider_status == 'start':
            self._spider_status = 'stopping'
            while self._spider_status == 'stopping':
                pass

    def start(self):
        try:
            self._processor.logger.info("START %s SUCCESS" % self._spider_id)
            self._spider_status = 'start'
            self._queue = PriorityQueue(self._processor)
            # print(self._processor.spider_start_requests)
            if not self._processor.start_requests:
                self._processor.init_start_requests()
            print('START_REQUESTS COUNT ::: %s' % str(len(self._processor.start_requests)))
            for start_request in self._processor.start_requests:
                if self._should_follow(start_request):
                    start_request.duplicate_remove = False
                    self._queue.push(start_request)
                    self._processor.logger.info("start request:>>>>>>" + str(start_request))
            # 去除所有添加到queue的start_request， 防止污染后续的processor
            self._processor.start_requests.clear()
            for batch in self._batch_requests():
                if len(batch) > 0:
                    self._crawl(batch)
                    if self.test:
                        if self._process_count > 0:
                            return
                if self._spider_status == 'stopping':
                    break
            self._spider_status = 'stopped'
            self._processor.logger.info("STOP %s SUCCESS" % self._spider_id)
        except Exception:
            self._processor.logger.info("%s -- Exception -- Stopped -- %s" % (self._spider_id, traceback.format_exc()))
            self._spider_status = 'stopped'

    def restart(self):
        self._queue = PriorityQueue(self._processor)
        self._queue.clear()
        self.start()

    def _batch_requests(self):
        batch = []
        count = 0
        retry = 0
        try:
            while True:
                count += 1
                if len(batch) >= self._batch_size or count >= self._batch_size:
                    batch.sort(key=_priority_compare_key, reverse=True)
                    yield batch
                    batch = []
                    count = 0
                temp_request = self._queue.pop()
                queue_count = len(self._queue)
                if temp_request is not None:
                    if not temp_request.callback:
                        temp_request.callback = self._processor.process
                    batch.append(temp_request)
                elif len(batch) == 0 and queue_count == 0:  # 等待几次，看队列中是否还有
                    time.sleep(self._time_sleep)
                    retry += 1
                    if retry >= 3:
                        return []
        except KeyboardInterrupt:
            pass

    def _crawl(self, batch):
        responses = self._downloader.download(batch)
        if self._time_sleep:
            time.sleep(self._time_sleep)
        for response in responses:
            self._processor.logger.info(response)
            callback = response.request.callback(response)
            if isinstance(callback, types.GeneratorType):
                pipe = self._queue.get_pipe()
                for item in callback:
                    if isinstance(item, Request):
                        # logger.info("push request to queue..." + str(item))
                        if self._should_follow(item):
                            self._queue.push_pipe(item, pipe)
                    elif isinstance(item, PipeItem):
                        # 如果返回对象是pipeItem，则用对应的pipeline处理
                        self._process_count += 1
                        for pipe_name in item.pipe_names:
                            queue_job(PIPELINE_TASK, PipelineArgs(pipe_name, item.result),
                                      queue=PIPELINE)
                        if self.test:
                            if self._process_count > 0:
                                return
                    elif isinstance(item, Violet):  # 如果返回的是tuple，即详情页的processor和详情页的请求信息
                        queue_job(CRAWLER_TASK, CrawlArgs(item.processor, item.request), queue=CRAWLER)
                    else:
                        raise Exception('not return correct value!!!')
                pipe.execute()
            elif isinstance(callback, Request):
                # logger.info("push request to queue..." + str(back))
                if self._should_follow(callback):
                    self._queue.push(callback)
            elif isinstance(callback, PipeItem):
                # 如果返回对象是pipeItem，则用对应的pipeline处理
                self._process_count += 1
                for pipe_name in callback.pipe_names:
                    queue_job(PIPELINE_TASK, PipelineArgs(pipe_name, callback.result), queue=PIPELINE)
            elif isinstance(callback, Violet):  # 如果返回的是tuple，即详情页的processor和详情页的请求信息
                queue_job(CRAWLER_TASK, CrawlArgs(item.processor, item.request), queue=CRAWLER)
            else:
                # # 如果返回对象不是pipeItem，则默认用每个pipeline处理
                raise Exception('not return correct value!!!')

    def _should_follow(self, request):
        regex = self._host_regex
        # hostname can be None for wrong urls (like javascript links)
        host = urlparse_cached(request).hostname or ''
        return bool(regex.search(host))

    def _get_host_regex(self):
        """Override this method to implement a different offsite policy"""
        allowed_domains = getattr(self._processor, 'allowed_domains', None)
        if not allowed_domains:
            return re.compile('')  # allow all by default
        regex = r'^(.*\.)?(%s)$' % '|'.join(re.escape(d) for d in allowed_domains if d is not None)
        return re.compile(regex)
