from config import CONFIG
import time
import os
import re
from myspiders.ruia import JsonField, HtmlField, AttrField, TextField, RegexField, Item, Spider, Request
from urllib.parse import urlencode, urlparse, urljoin, quote
from myspiders.ruia.plugins.ua_random import middleware
from myspiders.tools.tools_request import request_html_by_aiohttp
from config import DocumentUrl
from bs4 import BeautifulSoup


label_transfer = {
    '产品名称': 'name',
    '产品代码': 'code',
    '币种': 'currency',
    '风险等级': 'risk',
    '起点金额': 'amount_buy_min',
    '递增金额': 'amount_per_buy',
    '销售地区': 'sale_areas',
    '发行机构': 'sale_agents',
    '最新年化收益率': 'rate_max',
    '参考年化收益率': 'rate_max',
    '年化收益率': 'rate_max',
    '业绩比较基准': 'rate_max',
    '投资期限': 'term',
    '认购起日': 'date_open',
    '认购止日': 'date_close',
    '适用客户群': 'clients'
}


class BankcommWorker(Spider):
    name = 'BankcommWorker'
    bank_name = '交通银行'
    bank_domain = 'http://www.bankcomm.com/'

    print('================已初始化%s==================' % name)
    begin_url = 'http://www.bankcomm.com/BankCommSite/jyjr/cn/lcpd/queryFundInfoListNew.do'
    next_url = 'http://www.bankcomm.com/BankCommSite/jyjr/cn/lcpd/queryFundInfoNew.do?code='
    manual_url_prefix = 'http://www.bankcomm.com/BankCommSite/upload/wmbooks/%s.pdf'
    html_type = CONFIG.HTML_TYPE['manual']

    async def start_manual(self):
        code_list = []
        html = await request_html_by_aiohttp(url=self.begin_url)
        soup = BeautifulSoup(html, 'lxml')
        list_ul = soup.find_all(name='ul', attrs={'class': 'lc-item-list'})
        if list_ul:
            for ul in list_ul:
                li = ul.find_all(name='li', id=True)
                if li:
                    for one in li:
                        code = one.get('id').strip()
                        code_list.append(code)

        for code in code_list:
            url = self.next_url + code
            yield self.request(url=url, callback=self.parse, metadata={'code': code})

    async def parse(self, response):
        code = response.metadata['code']
        ukey = self.bank_name + '=' + code

        html = await response.text()
        soup = BeautifulSoup(html, 'lxml')
        pdf_a = soup.find(href=re.compile(r'\.pdf'))
        if pdf_a:
            pdf_url = pdf_a.get('href')
            if not pdf_url.startswith('http://'):
                pdf_url = urljoin(self.bank_domain, pdf_url)
        else:
            pdf_url = self.manual_url_prefix % code

        manual = DocumentUrl(ukey=ukey, url=pdf_url, html_type=self.html_type)
        manual_data = manual.do_dict_data()
        self.mongo.do_insert_one(self.collection_file, {'_id': ukey}, manual_data)

        box = soup.find(class_='change-box atv')
        list_tr = box.find_all(name='tr')
        if list_tr:
            wealth_data = {
                '_id': ukey,
                'referenceable': '高',
                'name': '',
                'code': '',
                'currency': '',
                'risk': '',
                'amount_buy_min': '',
                'amount_per_buy': '',
                'sale_areas': '',
                'sale_agents': '',
                'rate_max': '',
                'term': '',
                'date_open': '',
                'date_close': '',
                'clients': ''
            }
            print('解析ukey:', ukey)
            for one in list_tr:
                label = one.find(name='th')
                value = one.find(name='td')
                if label and value:
                    label = label.text.strip()
                    value = value.text.strip()

                    label_new = label_transfer[label]
                    wealth_data[label_new] = value

            wealth_data = self.value_transfer(wealth_data)
            # 保存获取到的理财列表信息
            self.mongo.do_insert_one(self.collection_list, {'_id': wealth_data['_id']}, wealth_data)

    def value_transfer(self, wealth_data: dict):
        risk = wealth_data['risk']
        amount_buy_min = wealth_data['amount_buy_min']
        amount_per_buy = wealth_data['amount_per_buy']
        term = wealth_data['term']
        rate_max = wealth_data['rate_max']

        pattern_num = re.compile(r'\d')
        result = pattern_num.search(risk)
        if result:
            risk_new = result.group(0)
            wealth_data['risk'] = int(risk_new)

        if '万元' in amount_buy_min:
            amount_buy_min_new = amount_buy_min.replace('万元', '0000')
            wealth_data['amount_buy_min'] = amount_buy_min_new

        if '元' in amount_per_buy:
            amount_per_buy_new = amount_per_buy.replace('元', '')
            wealth_data['amount_per_buy'] = amount_per_buy_new

        if '天' in term:
            term_new = term.replace('天', '')
            wealth_data['term'] = term_new

        pattern_rate = re.compile(r'([0-9]+\.?[0-9]*)[%％]')
        res = pattern_rate.findall(rate_max)
        if res:
            rate_max_new = ''
            for one in res:
                num = round(float(one) / 100, 6)
                rate_max_new += str(num) + ','
            wealth_data['rate_max'] = rate_max_new

        return wealth_data


def start():
    # BankcommWorker.start(middleware=middleware)
    pass
