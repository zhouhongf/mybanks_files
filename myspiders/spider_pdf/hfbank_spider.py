from myspiders.ruia import Spider
from myspiders.ruia.plugins.ua_random import middleware
from config import DocumentUrl
from config import CONFIG
import re
import os
from bs4 import BeautifulSoup
from urllib.parse import urlencode, urlparse, urljoin, quote
import farmhash
from constants.bank_dict import BankDict


def get_fetch_formdata(page_index: int, page_size: int):
    form_data = {
        'ptType': 'lcpt',
        'order': 'false',
        'nameValue': 'RsgStrtDt',
        'search': '',
        'TypeNo': '0,1,2',
        'Status': '',
        'Limit': '',
        'RiskLevel': '',
        'CurrType': '',
        'pageStartCount': str(page_index * page_size),
        'pagecount': str(page_size)
    }
    return form_data


class HfbankWorker(Spider):
    name = 'HfbankWorker'
    bank_name = '恒丰银行'
    bank_domain = 'http://www.hfbank.com.cn/'

    start_urls = ['http://www.hfbank.com.cn/ucms/hfyh/jsp/gryw/lc_lb.jsp']
    page_size = 8
    form_data = [get_fetch_formdata(0, page_size)]

    headers = {'Referer': 'http://www.hfbank.com.cn/gryw/cfgl/lc/rmlctj/index.shtml'}

    html_type = CONFIG.HTML_TYPE['manual']
    manual_url_prefix = 'https://mbsn.hfbank.com.cn/ebank/finace_desc?downloadFile=%s_1.htm'
    print('================已运行%s==================' % name)
    risk_transfer = BankDict.list_risk

    pattern_num = re.compile(r'[0-9]+\.?[0-9]*')
    pattern_rate_type = re.compile(r'\(([\u4e00-\u9fa5]+)\)')
    pattern_term = re.compile(r'([0-9]+)个?([天日月年])')
    pattern_date = re.compile(r'[0-9]{2,4}\-[0-9]{1,2}\-[0-9]{1,2}')

    async def parse(self, response):
        text = await response.text()
        if text:
            soup = BeautifulSoup(text, 'lxml')
            list_div = soup.find_all(name='div', class_='financialist-article')
            for one in list_div:
                data = self.parse_each_one(one)
                self.save_list_manual_db(data)

            if not response.metadata:
                total_num = soup.find(id='totalNum')
                if total_num:
                    page_count = total_num.get('value')
                    if int(page_count) > 1:
                        for i in range(1, int(page_count)):
                            url = self.start_urls[0]
                            form_data = get_fetch_formdata(i, self.page_size)
                            yield self.request(url=url, form_data=form_data, callback=self.parse, metadata={'page_index': i})

    def parse_each_one(self, one):
        data = {
            'referencable': '较高',
            'bank_level': '股份银行',
            'name': None,
            'code': None,
            'manual_url': None,
            'promise_type': None,
            'fixed_type': None,
            'risk': None,
            'rate_type': None,
            'rate_min': None,
            'rate_max': None,
            'term': None,
            'amount_buy_min': None,
            'date_start': None,
            'date_end': None
        }

        code = one.select_one('h3 a span').text.strip()
        label_code = one.select_one('h3 a').text.strip()
        name = label_code.replace(code, '')
        data['code'] = code
        data['name'] = name
        data['manual_url'] = self.manual_url_prefix % code

        risk = one.select_one('h3 div span').text.strip()
        label_risk = one.select_one('h3 div').text.strip()
        prd_types = label_risk.replace(risk, '')
        data['risk'] = self.risk_transfer[risk]
        data['promise_type'] = '非保本' if '非保本' in prd_types else '保本'
        data['fixed_type'] = '浮动收益' if '浮动收益' in prd_types else '固定收益'

        rate_type = one.select_one('table.con tr td').text.strip()
        data['rate_type'] = '净值型' if '净值' in rate_type else '预期收益型'

        part_two = one.select_one('table.con tr:last-child')
        rate = part_two.select_one('td.bot span').text.strip()
        term = part_two.select_one('td.bot:nth-child(2) span').text.strip()
        amount_buy_min = part_two.select_one('td.bot:last-child').text.strip()

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

        list_rate = self.pattern_num.findall(rate)
        if list_rate:
            if '%' in rate or '％' in rate:
                data['rate_min'] = round(float(list_rate[0]) / 100, 6)
                data['rate_max'] = round(float(list_rate[-1]) / 100, 6)
            else:
                data['rate_min'] = float(list_rate[0])
                data['rate_max'] = float(list_rate[-1])

        res_num = re.compile(r'\d+').search(amount_buy_min)
        if res_num:
            num = res_num.group(0)
            data['amount_buy_min'] = float(num) * 10000 if '万' in amount_buy_min else float(num)

        list_p = one.select('div.date p')
        for p in list_p:
            word = p.text.strip()
            word = re.sub(r'\s+', '', word)
            if '起息日' in word:
                date_start = self.pattern_date.search(word)
                if date_start:
                    data['date_start'] = date_start.group(0)
            if '到期日' in word:
                date_end = self.pattern_date.search(word)
                if date_end:
                    data['date_end'] = date_end.group(0)

        data['_id'] = self.bank_name + '=' + data['code']
        return data

    def save_list_manual_db(self, data):
        result = self.mongo.do_insert_one(self.collection_list, {'_id': data['_id']}, data)
        if result:
            manual = DocumentUrl(ukey=data['_id'], url=data['manual_url'], html_type=self.html_type)
            manual_data = manual.do_dict_data()
            self.mongo.do_insert_one(self.collection_file, {'_id': data['_id']}, manual_data)


def start():
    # HfbankWorker.start(middleware=middleware)
    pass
