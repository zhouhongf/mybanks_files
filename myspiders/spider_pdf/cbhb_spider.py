from myspiders.ruia import Spider
from myspiders.ruia.plugins.ua_random import middleware
from config import DocumentUrl
from config import CONFIG
import re
import os
from bs4 import BeautifulSoup
from urllib.parse import urlencode, urlparse, urljoin, quote
import farmhash


class CbhbWorker(Spider):
    name = 'CbhbWorker'
    bank_name = '渤海银行'
    bank_domain = 'http://www.cbhb.com.cn/'

    start_urls = [
        'http://www.cbhb.com.cn/bhbank/S101/lingshouyinhangfuwu/lcfw/rxcp/index.htm',
        'http://www.cbhb.com.cn/bhbank/S101/lingshouyinhangfuwu/lcfw/thdxlc/index.htm'
    ]
    print('================已运行%s==================' % name)
    manual_url_prefix = 'http://www.cbhb.com.cn/bhbank/S101/attach/'
    html_type = CONFIG.HTML_TYPE['manual']

    async def parse(self, response):
        text = await response.text()
        if text:
            soup = BeautifulSoup(text, 'lxml')
            list_a = soup.find_all(name='a', href=re.compile(r'\.pdf'))
            code_set = set()
            for one in list_a:
                link = one.get('href')
                if link:
                    url_words = os.path.split(link)
                    filename = url_words[-1]

                    code = filename.split('.')[0]
                    code_suffix = code[-2:]
                    if code_suffix == 'cl' or code_suffix == 'dq':
                        code = code[:-2]
                    code_set.add(code)

            for code in code_set:
                data = {
                    'referencable': '较高',
                    'bank_level': '股份银行',
                    '_id': self.bank_name + '=' + code,
                    'code': code,
                    'manual_url': self.manual_url_prefix + code
                }
                self.save_list_manual_db(data)

    def save_list_manual_db(self, data):
        result = self.mongo.do_insert_one(self.collection_list, {'_id': data['_id']}, data)
        if result:
            manual = DocumentUrl(ukey=data['_id'], url=data['manual_url'], html_type=self.html_type)
            manual_data = manual.do_dict_data()
            self.mongo.do_insert_one(self.collection_file, {'_id': data['_id']}, manual_data)


def start():
    CbhbWorker.start(middleware=middleware)
    pass
