from myspiders.ruia import Spider
from myspiders.ruia.plugins.ua_random import middleware
import json
from config import DocumentUrl
from config import CONFIG
import time
import re
import math


def get_fetch_params(page_index: int, page_size: int):
    form_data = {
        'tableIndex': 'table01',
        'dataType': '01',
        'tplId': 'tpl01',
        'pageNum': str(page_index),
        'pageSize': str(page_size),
        'channelCode': 'C0002',
        'access_source': 'PC',
    }
    return form_data


class PinganWorker(Spider):
    name = 'PinganWorker'
    bank_name = '平安银行'
    bank_domain = 'https://ebank.pingan.com.cn/'

    page_size = 20
    start_urls = ['https://ebank.pingan.com.cn/rmb/brop/pop/cust/brop_pop_shelf_service.qrySuperviseProductList']
    form_data = [get_fetch_params(1, page_size)]
    headers = {'Referer': 'https://ebank.pingan.com.cn/aum/common/sales_list/index.html?initPage=true'}

    html_type = CONFIG.HTML_TYPE['manual']
    print('================已运行%s==================' % name)
    start_url_supplement_prefix = 'https://bank.pingan.com.cn/rmb/bron/ibank/cust/bron-ibank-pd/fund/bootpage/queryPrdAttachedFile.do?prdCode=%s&prdType=01&access_source=PC'
    supplement_referer_prefix = 'https://bank.pingan.com.cn/m/aum/common/prdInformation/index.html?initPage=true&prdCode=%s&prdType=01'
    pattern_rate = re.compile(r'([0-9]+\.?[0-9]*)[%％]')

    # rate_transfer = {'FF': '非保本浮动收益', 'BG': '保本固定收益', 'BF': '保本浮动收益'}
    currency_transfer = {
        'RMB': '人民币', 156: '人民币',
        'HKD': '港币', 344: '港币',
        'USD': '美元', 840: '美元',
        'GBP': '英镑', 826: '英镑',
        'EUR': '欧元', 978: '欧元',
        'JPY': '日元', 392: '日元',
        'CAD': '加拿大元', 124: '加拿大元',
        'CHF': '瑞士法郎', 756: '瑞士法郎',
        'AUD': '澳大利亚元', '036': '澳大利亚元',
        'SGD': '新加坡元', 702: '新加坡元'
    }

    def makeup_list_data(self, one):
        data = {
            'referencable': '高',
            'bank_level': '股份银行',
            'sale_client': '个人',
            '_id': self.bank_name + '=' + one['prdCode'],
            'code': one['prdCode'],
            'name': one['prdName'],
            'risk': one['riskLevel'],
            'amount_buy_min': one['minAmount'],
            'code_register': None,
            'promise_type': None,
            'fixed_type': None,
            'manual_url': None,
            'currency': None,
            'rate_type': None,
            'rate_min': None,
            'rate_max': None
        }
        if 'productNo' in one.keys():
            data['code_register'] = one['productNo']

        rate_type = one['rateType']
        data['promise_type'] = '非保本' if rate_type == 'FF' else '保本'
        data['fixed_type'] = '固定收益' if rate_type == 'BG' else '浮动收益'
        return data

    async def parse(self, response):
        jsondata = await response.json()
        if jsondata:
            total_size = jsondata['data']['totalSize']
            list_data = jsondata['data']['list']
            for one in list_data:
                data = self.makeup_list_data(one)

                referer = self.supplement_referer_prefix % data['code']
                url = self.start_url_supplement_prefix % data['code']
                self.headers.update({'Referer': referer})
                yield self.request(url=url, callback=self.parse_supplement, metadata={'list_one': data})

            if not response.metadata:
                url = self.start_urls[0]
                page_count = math.ceil(int(total_size) / self.page_size)
                print('总共%s条记录，共%s页' % (total_size, page_count))
                if page_count > 1:
                    for page_index in range(2, page_count + 1):
                        form_data = get_fetch_params(page_index, self.page_size)
                        yield self.request(url=url, form_data=form_data, callback=self.parse, metadata={'pageNum': page_index})

    async def parse_supplement(self, response):
        list_one = response.metadata['list_one']
        jsondata = await response.json()
        if jsondata:
            list_file = jsondata['data']['instructionFileList']
            for one in list_file:
                attach_type = one['attachType']
                prd_code = one['prdCode']
                if attach_type == '3' and prd_code == list_one['code']:
                    list_one['manual_url'] = one['url']
                    break

            prd_info = jsondata['data']['prdInfo']
            rate_range = prd_info['indexContent']
            rate_type = prd_info['indexName']
            currency = prd_info['currency']

            list_one['currency'] = self.currency_transfer[currency]
            list_one['rate_type'] = rate_type

            results = self.pattern_rate.findall(rate_range)
            if results:
                list.sort(results)
                list_one['rate_min'] = results[0]
                list_one['rate_max'] = results[-1]

            self.save_list_manual_db(list_one)

    def save_list_manual_db(self, data):
        result = self.mongo.do_insert_one(self.collection_list, {'_id': data['_id']}, data)
        if result:
            manual = DocumentUrl(ukey=data['_id'], url=data['manual_url'], html_type=self.html_type)
            manual_data = manual.do_dict_data()
            self.mongo.do_insert_one(self.collection_file, {'_id': data['_id']}, manual_data)


def start():
    # PinganWorker.start(middleware=middleware)
    pass
