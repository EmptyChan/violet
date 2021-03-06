#!/usr/bin/env python
# -*- coding: utf-8 -*-
from constants.pipeline_name import CONSOLE_PIPELINE
from fetchman.utils.reqser import request_to_dict
from fetchman.spider.spider_core import SpiderCore
from fetchman.processor.base_processor import BaseProcessor
from fetchman.downloader.http.spider_request import Request
from fetchman.utils.decorator import check
from fetchman.pipeline.pipe_item import PipeItem, Violet
# import pickle
from bs4 import BeautifulSoup as bs
import hashlib
import time
import random


# 爬取土流网解析器
class Tuliu_Processor(BaseProcessor):
    spider_id = 'tuliu_spider'
    allowed_domains = ['tuliu.com']

    # 推入初始request
    @classmethod
    def init_start_requests(cls):
        cls.start_requests.extend([Request(url='http://www.tuliu.com/news/list-c165/%s.html' % page, priority=0,
                                           meta={'newsCateId': '20171102111907007'}) for page in range(1, 2)])
        # cls.start_requests.extend([Request(url='http://www.tuliu.com/news/list-c163/%s.html' % page, priority=0,
        #                                    meta={'newsCateId': '20171102111907007'}) for page in range(1, 30)]

    @check
    def process(self, response):
        soup = bs(response.m_response.content, 'lxml')

        tuliu_div_list = soup.select('div.news_list_list ul li.list_box')
        detail_processor = Tuliu_Detail_Processor()
        for tuliu_div in tuliu_div_list[:3]:
            if tuliu_div.select('a img'):
                detail_url = tuliu_div.select('a')[0]['href']
                img_url = tuliu_div.select('a img')[0]['src']
                name = tuliu_div.select('h1.category_title nobr.l')[0].text.strip()
                createTime = tuliu_div.select('h1.category_title nobr.r')[0].text.replace('发布时间 ', '').strip()
                shortDes = tuliu_div.select('div')[0].text.replace('[查看全文]', '')

                md5 = hashlib.md5()
                rand_name = str(time.time()) + str(random.random())
                md5.update(rand_name.encode("utf8"))
                img_name = md5.hexdigest() + '.jpg'

                request = Request(url=detail_url, priority=1)
                request.meta['name'] = name
                request.meta['createTime'] = createTime
                request.meta['shortDes'] = shortDes
                request.meta['img_name'] = img_name
                request.meta['newsCateId'] = response.request.meta['newsCateId']
                d = request_to_dict(request, detail_processor)
                yield Violet(Tuliu_Detail_Processor, d)


class Tuliu_Detail_Processor(BaseProcessor):
    spider_id = 'tuliu_detail_spider'
    allowed_domains = ['tuliu.com']

    # 获取新闻详情并丢入DataBasePipeline
    @check
    def process(self, response):
        soup = bs(response.m_response.content, 'lxml')
        result = dict()
        result['newsProductId'] = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        result['newsCateId'] = response.request.meta['newsCateId']
        result['name'] = response.request.meta['name']
        result['imageUrl'] = response.request.meta['img_name']
        result['newsCateId'] = response.request.meta['newsCateId']
        result['shortDes'] = response.request.meta['shortDes']
        result['createTime'] = response.request.meta['createTime']
        result['newsFromWebUrl'] = response.request.url
        span_list = soup.select('div.article-header p.text-gray-9 span')
        for span in span_list:
            if '来源：' in span.text:
                result['newsFrom'] = span.text.replace('来源：', '').strip()
                break
            else:
                result['newsFrom'] = '互联网'
        longDes = soup.select('div.article-content')[0]

        result['longDes'] = str(longDes)

        yield PipeItem([CONSOLE_PIPELINE], result)


if __name__ == '__main__':
    # 生成爬虫对象，设置pipeline，启动爬虫
    SpiderCore(Tuliu_Processor(), time_sleep=1) \
        .start()
