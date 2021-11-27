from myspiders.ruia import Spider
from myspiders.ruia.plugins.ua_random import middleware
from config import DocumentUrl
from config import CONFIG
import re
import os
from bs4 import BeautifulSoup
from urllib.parse import urlencode, urlparse, urljoin, quote
import farmhash


class HxbWorker(Spider):
    name = 'HxbWorker'
    bank_name = '华夏银行'
    bank_domain = 'http://www.hxb.com.cn/'
    start_urls = ['http://www.hxb.com.cn/grjr/lylc/zzfsdlccpxx/index.shtml']
    headers = {'Referer': 'http://www.hxb.com.cn/index.shtml'}
    html_type = CONFIG.HTML_TYPE['manual']
    print('================已运行%s==================' % name)

    pattern_num = re.compile(r'[0-9]+\.?[0-9]*')
    pattern_term = re.compile(r'([0-9]+)个?([天日月年])')
    pattern_date = re.compile(r'[0-9]{2,4}\.[0-9]{1,2}\.[0-9]{1,2}')

    async def parse(self, response):
        text = await response.text()
        if text:
            soup = BeautifulSoup(text, 'lxml')
            data_list = soup.find_all(name='ol')
            for one in data_list:
                box_right = one.select('ul li')
                a = one.find(href=re.compile(r'\.pdf'))
                if a:
                    data = {
                        'referencable': '较高',
                        'bank_level': '股份银行',
                        'name': one.select_one('p.box_title').text.strip(),
                        'rate_type': one.select_one('div.box_lf p:nth-child(2)').text.strip(),
                        'manual_url': None,
                        'rate_min': None,
                        'rate_max': None,
                        'date_start': None,
                        'date_end': None,
                        'term': None,
                        'amount_buy_min': None,
                        'sale_ways': None
                    }

                    url = a.get('href')
                    if url and not url.startswith('http://'):
                        data['manual_url'] = urljoin(self.bank_domain, url)

                    rate = one.select_one('p.box_num').text.strip()
                    list_rate = self.pattern_num.findall(rate)
                    if list_rate:
                        if '%' in rate or '％' in rate:
                            data['rate_min'] = round(float(list_rate[0]) / 100, 6)
                            data['rate_max'] = round(float(list_rate[-1]) / 100, 6)
                        else:
                            data['rate_min'] = float(list_rate[0])
                            data['rate_max'] = float(list_rate[-1])

                    period = box_right[1].text.strip()
                    list_date = self.pattern_date.findall(period)
                    if list_date:
                        data['date_start'] = list_date[0].replace('.', '-')
                        data['date_end'] = list_date[-1].replace('.', '-')

                    term = box_right[0].text.strip()
                    res_term = self.pattern_term.search(term)
                    if res_term:
                        term_num = res_term.group(1)
                        term_unit = res_term.group(2)
                        if term_unit == '年':
                            data['term'] = round(float(term_num) * 365, 6)
                        elif term_unit == '月':
                            data['term'] = round(float(term_num) * 30, 6)
                        else:
                            data['term'] = float(term_num)
                    else:
                        data['term'] = term

                    amount_label = box_right[2].text.strip()
                    amount_label_num = self.pattern_num.search(amount_label)
                    if amount_label_num:
                        num = amount_label_num.group(0)
                        if '万' in amount_label:
                            num = num + '0000'
                        data['amount_buy_min'] = float(num)

                    sale_ways = box_right[3].select_one('span:last-child').text.strip()
                    data['sale_ways'] = re.sub(r'\s+', ',', sale_ways)

                    data['_id'] = self.bank_name + '=' + data['name']
                    self.save_list_manual_db(data)

    def save_list_manual_db(self, data):
        result = self.mongo.do_insert_one(self.collection_list, {'_id': data['_id']}, data)
        if result:
            manual = DocumentUrl(ukey=data['_id'], url=data['manual_url'], html_type=self.html_type)
            manual_data = manual.do_dict_data()
            self.mongo.do_insert_one(self.collection_file, {'_id': data['_id']}, manual_data)


def start():
    # HxbWorker.start(middleware=middleware)
    pass
