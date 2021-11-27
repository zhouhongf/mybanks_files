from config import CONFIG
import time
from myspiders.ruia import JsonField, HtmlField, AttrField, TextField, RegexField, Item, Spider, Request
from urllib.parse import urlencode, urlparse, urljoin, quote
from myspiders.ruia.plugins.ua_random import middleware
from myspiders.tools.tools_request import get_random_user_agent
from config import DocumentUrl


def get_fetch_url(start_url_prefix: str, page_start_number: int, page_size: int):
    params = {
        'turnPageBeginPos': str(page_start_number),
        'turnPageShowNum': str(page_size),
        'currentBusinessCode': '00681011',
        'responseFormat': 'JSON',
        'channel': '1101',
        'version': 'stanver',
        '_': str(int(time.time() * 1000))
    }
    url = start_url_prefix + urlencode(params)
    return url


class PsbcWorker(Spider):
    name = 'PsbcWorker'
    bank_name = '邮储银行'
    bank_domain = 'http://www.psbc.com/'

    print('================已初始化%s==================' % name)
    start_url_prefix = 'https://pbank.psbc.com/perbank/protalFinancialProductQuery.do?'
    manual_url_prefix = 'http://www.psbc.com/data/tosend/resource/upload/%s.pdf'
    html_type = CONFIG.HTML_TYPE['manual']
    page_start_number = 1
    page_size = 50
    start_urls = [get_fetch_url(start_url_prefix, page_start_number, page_size)]
    headers = {'Referer': 'https://pbank.psbc.com/perbank/financialProductInfoQuery.gate'}

    def save_list_manual_db(self, jsondata):
        insert_number = 0
        list_data = jsondata['iFinancialList']
        for one in list_data:
            data = {
                '_id': self.bank_name + '=' + one['financeCode'],
                'code': one['financeCode'],
                'name': one['financeName'],
                'register_code': one['financeRegistCode'],
                'risk': one['riskLevel']
            }

            manual_url = self.manual_url_prefix % data['code']
            manual = DocumentUrl(ukey=data['_id'], url=manual_url, html_type=self.html_type)
            manual_data = manual.do_dict_data()
            self.mongo.do_insert_one(self.collection_file, {'_id': data['_id']}, manual_data)

            back = self.mongo.do_insert_one(self.collection_list, {'_id': data['_id']}, data)
            if back:
                insert_number += 1
        return insert_number

    # 每次首先试探第一页，将page_size由默认的8，设置为50
    # 返回数据存入Mongo数据库，如果这50条全部都是新增，则继续爬取
    async def parse(self, response):
        jsondata = await response.json(content_type='text/html')
        insert_number = self.save_list_manual_db(jsondata)

        if insert_number == self.page_size:
            self.page_start_number += self.page_size
            url = get_fetch_url(self.start_url_prefix, self.page_start_number, self.page_size)

            yield self.request(url=url, callback=self.parse)


def start():
    # PsbcWorker.start(middleware=middleware)
    pass
