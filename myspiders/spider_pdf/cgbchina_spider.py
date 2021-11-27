from myspiders.ruia import Spider
from myspiders.ruia.plugins.ua_random import middleware
from config import DocumentUrl
from config import CONFIG
import re
import os
from bs4 import BeautifulSoup
from urllib.parse import urlencode, urlparse, urljoin, quote
import farmhash


class CgbchinaWorker(Spider):
    name = 'CgbchinaWorker'
    bank_name = '广发银行'
    bank_domain = 'http://www.cgbchina.com.cn/'
    start_urls = ['http://www.cgbchina.com.cn/Channel/16684283?nav=1', 'http://www.cgbchina.com.cn/Channel/16684283?nav=2']
    html_type = CONFIG.HTML_TYPE['manual']
    print('================已运行%s==================' % name)
    manual_url_prefix = 'http://www.cgbchina.com.cn/jsp/pdf/0-%s.pdf'

    pattern_num = re.compile(r'[0-9]+\.?[0-9]*')
    pattern_rate_type = re.compile(r'\(([\u4e00-\u9fa5]+)\)')
    pattern_term = re.compile(r'([0-9]+)个?([天日月年])')
    pattern_date = re.compile(r'[0-9]{2,4}\-[0-9]{1,2}\-[0-9]{1,2}')

    async def parse(self, response):
        text = await response.text()
        if text:
            soup = BeautifulSoup(text, 'lxml')
            table = soup.find(id='product_tab')
            list_tr = table.find_all(name='tr')
            for i in range(1, len(list_tr)):
                one = list_tr[i]
                list_td = one.find_all(name='td')

                data = {
                    'referencable': '较高',
                    'bank_level': '股份银行',
                    'name': list_td[0].text.strip(),
                    'code': None,
                    'manual_url': None,
                    'currency': list_td[1].text.strip(),
                    'term': None,
                    'amount_buy_min': float(list_td[3].text.strip()),
                    'rate_type': None,
                    'rate_min': None,
                    'rate_max': None,
                    'risk': None,
                    'date_start': None,
                    'date_end': None
                }

                url = list_td[0].find(name='a').get('href')
                params = urlparse(url).query.split('&')
                for one in params:
                    if one.startswith('pno='):
                        code = one.split('=')[1]
                        data['code'] = code
                        data['manual_url'] = self.manual_url_prefix % code
                        break

                term = list_td[2].text.strip()
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

                rate = list_td[4].text.strip()
                rate_type = self.pattern_rate_type.search(rate)
                if rate_type:
                    data['rate_type'] = rate_type.group(1)

                list_rate = self.pattern_num.findall(rate)
                if list_rate:
                    if '%' in rate or '％' in rate:
                        data['rate_min'] = round(float(list_rate[0]) / 100, 6)
                        data['rate_max'] = round(float(list_rate[-1]) / 100, 6)
                    else:
                        data['rate_min'] = float(list_rate[0])
                        data['rate_max'] = float(list_rate[-1])

                risk = list_td[5].text.strip()
                risk_num = re.compile(r'\d').search(risk)
                if risk_num:
                    data['risk'] = int(risk_num.group(0))

                term = list_td[6].text.strip()
                list_date = self.pattern_date.findall(term)
                if list_date:
                    data['date_start'] = list_date[0]
                    data['date_end'] = list_date[-1]

                if data['code']:
                    data['_id'] = self.bank_name + '=' + data['code']
                    self.save_list_manual_db(data)

    def save_list_manual_db(self, data):
        result = self.mongo.do_insert_one(self.collection_list, {'_id': data['_id']}, data)
        if result:
            manual = DocumentUrl(ukey=data['_id'], url=data['manual_url'], html_type=self.html_type)
            manual_data = manual.do_dict_data()
            self.mongo.do_insert_one(self.collection_file, {'_id': data['_id']}, manual_data)


def start():
    # CgbchinaWorker.start(middleware=middleware)
    pass
