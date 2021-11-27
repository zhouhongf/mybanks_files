from myspiders.ruia import Spider
from myspiders.ruia.plugins.ua_random import middleware
from config import DocumentUrl
from config import CONFIG
import re
import os
from bs4 import BeautifulSoup
from urllib.parse import urlencode, urlparse, urljoin, quote
import farmhash


def get_fetch_formdata(page_index: int):
    one = {
        'codeOrName': '',
        'TZBZMC': '',
        'SFZS': 'Y',    # 是否在售
        'qxrUp': 'Y',
        'qxrDown': '',
        'dqrUp': '',
        'dqrDown': '',
        'qdjeUp': '',
        'qdjeDown': '',
        'qxUp': '',
        'qxDown': '',
        'yqnhsylUp': '',
        'yqnhsylDown': '',
        'page': str(page_index),
        'pageSize': '12'
    }
    one = urlencode(one)

    label = 'channelIds[]'
    label_values = ['yxl94', 'ygelc79', 'hqb30', 'dhb2', 'cjh', 'gylc70', 'Ajh67', 'Ajh84', '901776', 'Bjh91', 'Ejh99', 'Tjh70', 'tcjh96', 'ts43', 'ygjylhzhMOM25', 'yxyg87', 'zcpzjh64',
                    'wjyh1', 'smjjb9', 'ty90', 'tx16', 'ghjx6', 'ygxgt59', 'wbtcjh3', 'wbBjh77', 'wbTjh28', 'sycfxl', 'cfTjh', 'jgdhb', 'tydhb', 'jgxck', 'jgyxl', 'tyyxl', 'dgBTAcp',
                    '27637097', '27637101', '27637105', '27637109', '27637113', '27637117', '27637121', '27637125', '27637129', '27637133', 'gyxj32', 'yghxl', 'ygcxl', 'ygjxl', 'ygbxl',
                    'ygqxl', 'yglxl', 'ygzxl', 'ygttg']
    two = ''
    for value in label_values:
        data = {label: value}
        two += '&' + urlencode(data)

    return '&' + one + two


class CebbankWorker(Spider):
    name = 'CebbankWorker'
    bank_name = '光大银行'
    bank_domain = 'http://www.cebbank.com/'

    headers = {'Referer': 'http://www.cebbank.com/site/gryw/yglc/lccp49/index.html'}
    html_type = CONFIG.HTML_TYPE['manual']
    print('================已运行%s==================' % name)
    begin_url = 'http://www.cebbank.com/eportal/ui?moduleId=12073&struts.portlet.action=/app/yglcAction!listProduct.action'

    pattern_link = re.compile(r'/site/gryw/yglc/lccpsj/.+/index\.html')
    pattern_code = re.compile(r'\(([0-9a-zA-Z]+)\)')

    async def start_manual(self):
        form_data = get_fetch_formdata(1)
        url = self.begin_url + form_data
        yield self.request(url=url, method='POST', callback=self.parse)

    async def parse(self, response):
        text = await response.text()
        if text:
            soup = BeautifulSoup(text, 'lxml')
            list_a = soup.find_all(name='a', href=self.pattern_link)
            for a in list_a:
                name = a.get('title')
                url = a.get('href')
                if url and not url.startswith('http://'):
                    url = urljoin('http://www.cebbank.com/site/gryw/yglc/lccp49/index.html', url)
                    yield self.request(url=url, callback=self.parse_table, metadata={'name': name.strip()})

            if not response.metadata:
                span_total_page = soup.find(id='totalpage')
                if span_total_page:
                    total_page = int(span_total_page.text)
                    if total_page > 1:
                        for page_index in range(2, total_page + 1):
                            form_data = get_fetch_formdata(page_index)
                            url = self.begin_url + form_data
                            yield self.request(url=url, method='POST', callback=self.parse, metadata={'page_index': page_index})

    async def parse_table(self, response):
        name = response.metadata['name']

        url_old = response.url
        url_path = urlparse(url_old).path
        url_prefix = os.path.split(url_path)[0]
        pattern_pdf = re.compile(url_prefix + r'/.+\.pdf')

        text = await response.text()
        if text:
            soup = BeautifulSoup(text, 'lxml')

            code = ''
            result = self.pattern_code.search(name)
            if result:
                code = result.group(1)

            if not code:
                input_code = soup.find(id='cpCode')
                code = input_code.get('value')

            if code:
                ukey = self.bank_name + '=' + code
                # body = soup.select_one('#main_con .lccp_xq_tit')
                # print('获取信息的部分：', body)
                input_currency = soup.find(id='tzbzmc')
                currency = input_currency.get('value')

                input_amount_buy_min = soup.find(id='qgje')
                amount_buy_min = input_amount_buy_min.get('value')

                input_rate_type = soup.find(id='sfzqxcpmc')
                rate_type = input_rate_type.get('value')

                a = soup.find(href=pattern_pdf)
                if a:
                    url = a.get('href')
                    if url and not url.startswith('http://'):
                        url = urljoin(url_old, url)

                    data = {
                        'referencable': '中',
                        'bank_level': '股份银行',
                        '_id': ukey,
                        'code': code,
                        'manual_url': url,
                        'name': name,
                        'currency': currency,
                        'amount_buy_min': amount_buy_min,
                        'rate_type': rate_type
                    }
                    self.save_list_manual_db(data)

                else:
                    manual_body = soup.select_one('#main_con .cpsms_nr .sms_nr')
                    list_p = manual_body.find_all(name='p')
                    # 如果p标签大于20个，则将manual_body直接保存进数据库
                    if list_p and len(list_p) > 20:
                        self.save_html_file(ukey, str(manual_body))
                        print('已保存进MySQL：', ukey)

    def save_list_manual_db(self, data):
        result = self.mongo.do_insert_one(self.collection_list, {'_id': data['_id']}, data)
        if result:
            manual = DocumentUrl(ukey=data['_id'], url=data['manual_url'], html_type=self.html_type)
            manual_data = manual.do_dict_data()
            self.mongo.do_insert_one(self.collection_file, {'_id': data['_id']}, manual_data)

    def save_html_file(self, ukey, content):
        ukeyhash = farmhash.hash64(ukey)
        table_name = 'crawler_manual'
        d = self.mysql_db.table_has(table_name, 'ukeyhash', ukeyhash)
        if d:
            print('================在数据库中找到的d的内容是：', d)
            if d['ukey'] != ukey:
                print('farmhash collision: %s <=> %s' % (ukey, d['ukey']))
            return

        bank_name = ukey.split('=')[0]
        content_type = 'html'
        status = 'undo'

        one_data = {'ukeyhash': ukeyhash, 'ukey': ukey, 'bank_name': bank_name, 'content': content, 'content_type': content_type, 'status': status}
        self.mysql_db.table_insert(table_name, one_data)


def start():
    # CebbankWorker.start(middleware=middleware)
    pass
