from myspiders.ruia import Spider
from myspiders.ruia.plugins.ua_random import middleware
from config import DocumentUrl
from config import CONFIG
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin


class CzbankWorker(Spider):
    name = 'CzbankWorker'
    bank_name = '浙商银行'
    bank_domain = 'http://www.czbank.com/'

    start_urls = ['http://www.czbank.com/cn/fin_kno/xxcxpt1/lccpxxcx1/']

    html_type = CONFIG.HTML_TYPE['manual']
    print('================已运行%s==================' % name)

    async def parse(self, response):
        text = await response.text()
        if text:
            soup = BeautifulSoup(text, 'lxml')
            target = soup.find(title=re.compile(r'在售产品（发行时间：.+）'))
            link = target.get('href')
            if not link.startswith('http://'):
                url_old = response.url
                url_full = urljoin(url_old, link)
                yield self.request(url=url_full, callback=self.parse_table)

    async def parse_table(self, response):
        text = await response.text()
        url_old = response.url
        if text:
            soup = BeautifulSoup(text, 'lxml')
            list_pdf = soup.find_all(href=re.compile(r'\.pdf'))
            for one in list_pdf:
                code = one.text.strip()
                url = one.get('href')
                if not url.startswith('http://'):
                    url = urljoin(url_old, url)

                data = {
                    'referencable': '高',
                    'bank_level': '股份银行',
                    '_id': self.bank_name + '=' + code,
                    'code': code,
                    'manual_url': url
                }
                self.save_list_manual_db(data)

    def save_list_manual_db(self, data):
        result = self.mongo.do_insert_one(self.collection_list, {'_id': data['_id']}, data)
        if result:
            manual = DocumentUrl(ukey=data['_id'], url=data['manual_url'], html_type=self.html_type)
            manual_data = manual.do_dict_data()
            self.mongo.do_insert_one(self.collection_file, {'_id': data['_id']}, manual_data)


def start():
    # CzbankWorker.start(middleware=middleware)
    pass
