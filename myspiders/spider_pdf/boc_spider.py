from myspiders.ruia import JsonField, HtmlField, AttrField, TextField, RegexField, Item, Spider, Request
from myspiders.ruia.plugins.ua_random import middleware
from urllib.parse import urlencode, urlparse, urljoin, quote
import json
from config import CONFIG
import time
import os
import re


class BocItem(Item):
    target_item = HtmlField(css_select='.main .news ul.list li')

    title = TextField(css_select='a')
    url = AttrField(css_select='a', attr='href')
    html_type = JsonField(default=CONFIG.HTML_TYPE['manual'])
    create_time = JsonField(default=time.strftime('%Y-%m-%d %H:%M:%S'))
    crawl_status = JsonField(default='undo')


def get_fetch_urls(start_url_prefix: str, page_count: int):
    param_prefix = 'index_%s.html'
    params = [(param_prefix % index) for index in range(1, page_count)]
    params.insert(0, 'index.html')
    start_urls = [(start_url_prefix + one) for one in params]
    return start_urls


# 通过使用日期正则表达式，来分割出内容
pattern_date_in_title = re.compile(r'(.+)(20[0-9]{2}年[01]?[0-9]月[0-3]?[0-9]日)(.+)')
pattern_code_in_title = re.compile(r'([-a-zA-Z0-9]+)[\u4E00-\u9FA5\s]+')
pattern_term_in_title = re.compile(r'([0-9]+)天')
pattern_rate_in_title = re.compile(r'([0-9]+\.?[0-9]*)[%％]')


class BocWorker(Spider):
    name = 'BocWorker'
    bank_name = '中国银行'
    # https://www.boc.cn/fimarkets/cs8/fd6/index_49.html
    start_url_prefix = 'https://www.boc.cn/fimarkets/cs8/fd6/'

    print('================已初始化%s==================' % name)
    page_count = 50
    start_urls = get_fetch_urls(start_url_prefix, page_count)

    async def parse(self, response):
        html = await response.text()
        async for item in BocItem.get_items(html=html):
            yield item

    def make_item_by_regex(self, title):
        one = pattern_date_in_title.fullmatch(title)
        data = {'_id': '', 'code': '', 'name': '', 'date_open': '', 'term': '', 'rate_min': '', 'rate_max': ''}
        if one:
            head = one.group(1)
            data['date_open'] = one.group(2)
            tail = one.group(3)

            two = pattern_code_in_title.search(head)
            if two:
                code = two.group(1)
                name = head.replace(code, '')
                data['code'] = code
                data['name'] = name
                data['_id'] = self.bank_name + '=' + code

            three = pattern_term_in_title.search(tail)
            if three:
                data['term'] = three.group(1)

            four = pattern_rate_in_title.findall(tail)
            if four:
                if len(four) == 1:
                    rate = float(four[0]) / 100
                    data['rate_max'] = round(rate, 6)
                    data['rate_min'] = round(rate, 6)
                elif len(four) == 2:
                    rate_one = float(four[0]) / 100
                    rate_two = float(four[1]) / 100
                    max_num = max(rate_one, rate_two)
                    min_num = min(rate_one, rate_two)
                    data['rate_max'] = round(max_num, 6)
                    data['rate_min'] = round(min_num, 6)

            return data
        else:
            print('==================================================特殊情况：', title)
            return None

    async def process_item(self, item: Item):
        data = item.results
        one = self.make_item_by_regex(data['title'])
        if one:
            self.mongo.do_insert_one(self.collection_list, {'_id': one['_id']}, one)

            data.pop('title')
            data['_id'] = one['_id']
            self.mongo.do_insert_one(self.collection_file, {'_id': data['_id']}, data)


def start():
    # BocWorker.start(middleware=middleware)
    pass





