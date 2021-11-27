from myspiders.ruia import JsonField, AttrField, RegexField, Item, Spider, Request
from myspiders.ruia.plugins.ua_random import middleware
from urllib.parse import urlencode, urlparse, urljoin, quote
import json
from database.backends import MongoDatabase
from config import CONFIG
import time
import demjson
import os
import re


# 日常爬取时，将w设置为“可售|||||||1||0||0”, 即只查询当前在售的理财产品即可，用不着全部爬取
# 如要全部爬取，则将w设置为“|||||||1||0||0”
def get_fetch_urls(url: str, page_count: int, page_size: int):
    start_url_prefix = url
    page_count += 1
    params = [
        {
            'i': index,
            's': page_size,
            'w': '可售|||||||1||0||0',
        } for index in range(1, page_count)
    ]
    start_urls = [(start_url_prefix + urlencode(one)) for one in params]
    return start_urls


class AbchinaItem(Item):
    target_item = JsonField(json_select='Data>Table')

    _id = JsonField(json_select='ProductNo')
    code = JsonField(json_select='ProductNo')
    name = JsonField(json_select='ProdName')

    amount_buy_min = JsonField(json_select='PurStarAmo')
    term = JsonField(json_select='ProdLimit')

    rate_min = JsonField(json_select='ProdProfit')
    rate_max = JsonField(json_select='ProdProfit')

    redeem_type = JsonField(json_select='ProdClass')
    product_type = JsonField(json_select='ProdYildType')

    sale_areas = JsonField(json_select='ProdArea')
    raise_period = JsonField(json_select='ProdSaleDate')

    code_register = JsonField()
    risk = JsonField()
    date_open = JsonField()
    date_close = JsonField()
    date_end = JsonField()
    currency = JsonField()


class AbchinaManualItem(Item):
    url = RegexField(re_select=r"(url|URL)=\'(.+)\'")

    html_type = JsonField(default=CONFIG.HTML_TYPE['manual'])
    create_time = JsonField(default=time.strftime('%Y-%m-%d %H:%M:%S'))
    crawl_status = JsonField(default='undo')

    async def clean_url(self, url_tuple):
        return url_tuple[-1]


class AbchinaWorker(Spider):
    name = 'AbchinaWorker'
    bank_name = '农业银行'

    start_url_prefix = 'http://ewealth.abchina.com/app/data/api/DataService/BoeProductOwnV2?'
    manual_url_prefix = 'http://ewealth.abchina.com/fs/intro_list/%s.htm'
    pattern_manual_url = r"(url|URL)=\'(.+)\'"

    print('================已运行%s==================' % name)
    page_count = 5
    page_size = 15     # 可以设置为10000设置更大
    start_urls = get_fetch_urls(start_url_prefix, page_count, page_size)

    list_ignore = ['ZHZG181009', 'ADRY140053A']

    async def parse(self, response):
        jsondata = await response.json()
        urls = []
        async for item in AbchinaItem.get_json(jsondata=jsondata):
            yield item
            data = item.results
            code = data['code']
            if code not in self.list_ignore:
                url = self.manual_url_prefix % str(code)
                urls.append(url)

        async for resp in self.multiple_request(urls):
            url_old = resp.url
            code_temp = os.path.split(url_old)[-1]
            code = code_temp.split('.')[0]

            html = await resp.text()
            item = await AbchinaManualItem.get_item(html=html)

            item.results['_id'] = self.bank_name + '=' + code
            url = item.results['url']
            file_url = urljoin(url_old, url)
            item.results['url'] = file_url
            yield item

    async def process_item(self, item: Item):
        data = item.results
        # print('data是：', data)
        if isinstance(item, AbchinaItem):
            self.mongo.do_insert_one(self.collection_list,  {'_id': data['_id']}, data)
        elif isinstance(item, AbchinaManualItem):
            url = data['url']
            if url:
                self.mongo.do_insert_one(self.collection_file, {'_id': data['_id']}, data)


def start():
    # AbchinaWorker.start(middleware=middleware)
    pass





