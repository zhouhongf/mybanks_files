from myspiders.ruia import Spider
from myspiders.ruia.plugins.ua_random import middleware
import json
from config import DocumentUrl
from config import CONFIG
import time
import re
import demjson
from constants.bank_dict import BankDict


class CibWorker(Spider):
    name = 'CibWorker'
    bank_name = '兴业银行'
    bank_domain = 'https://www.cib.com.cn/'
    start_urls = [
        'https://www.cib.com.cn/cn/personal/wealth-management/xxcx/table',
        'http://directbank.cib.com.cn/hall/show/fin/finlist!ajaxPage.do?dataSet.nd=%s&dataSet.rows=3000&dataSet.page=1' % (int(time.time() * 1000))
    ]
    print('================已运行%s==================' % name)

    pattern_one = re.compile(r'yhlcdb=(\[(\s.+)+\s]);')
    pattern_two = re.compile(r'\[.+\]')
    labels = ['name', 'code', 'code_register', 'prd_type', 'issuer', 'risk', 'client', 'area']
    risk_transfer = BankDict.list_risk

    manual_url_prefix = 'http://directbank.cib.com.cn/hall/show/agrement/queryAgrement.do?name=licai&prodCode='
    html_type = CONFIG.HTML_TYPE['manual']

    pattern_rate = re.compile(r'[0-9]+\.?[0-9]*')

    async def parse(self, response):
        text = await response.text()
        index = text.find('yhlcdb=')
        if index != -1:
            print('开始解析表格=============================')
            first = self.pattern_one.search(text)
            if first:
                content = first.group(1)
                second = self.pattern_two.findall(content)
                if second:
                    for one in second:
                        value = demjson.decode(one)
                        dict_data = dict(zip(self.labels, value))
                        data = {
                            'code': dict_data['code'],
                            'code_register': dict_data['code_register'],
                            'name': dict_data['name'],
                            'risk': dict_data['risk'],
                            'sale_areas': dict_data['area'],
                            'amount_buy_min': None,
                            'currency': None,
                            'rate_type': None,
                            'term': None,
                            'rate_min': 0,
                            'rate_max': 0,
                        }
                        self.save_list_manual_db(data)
        else:
            jsondata = json.loads(text)
            list_data = jsondata['rows']
            for one in list_data:
                data = {
                    'code': one['finCode'],
                    'code_register': None,
                    'name': one['finName'],
                    'risk': one['prodRRName'],
                    'sale_areas': None,
                    'amount_buy_min': one['minAmt'],
                    'currency': one['currencyName'],
                    'rate_type': one['returnTypeName'],
                    'term': one['timeLimit'],
                    'rate_min': one['referenceIncome'],
                    'rate_max': one['returnRate'],
                }
                self.save_list_manual_db(data)

    def save_list_manual_db(self, data):
        risk = data['risk']
        pattern_num = re.compile(r'\d+')
        res = pattern_num.search(risk)
        if res:
            risk_num = int(res.group(0))
        else:
            risk_num = self.risk_transfer[risk]
        data['risk'] = risk_num

        data['_id'] = self.bank_name + '=' + data['code']
        data['referencable'] = '中'

        rate_min = data['rate_min']
        rate_max = data['rate_max']
        if rate_min == '-1' or rate_min == '详见协议书':
            data['rate_min'] = 0
        if rate_max == '-1' or rate_max == '详见协议书':
            data['rate_max'] = 0

        rate_type = data['rate_type']
        if rate_type == '参考净收益率':
            if self.pattern_rate.fullmatch(rate_min):
                data['rate_min'] = round(float(rate_min) / 100, 6)
            if self.pattern_rate.fullmatch(rate_max):
                data['rate_max'] = round(float(rate_max) / 100, 6)

        result = self.mongo.do_insert_one(self.collection_list, {'_id': data['_id']}, data)
        if result:
            url = self.manual_url_prefix + data['code']
            manual = DocumentUrl(ukey=data['_id'], url=url, html_type=self.html_type)
            manual_data = manual.do_dict_data()
            self.mongo.do_insert_one(self.collection_file, {'_id': data['_id']}, manual_data)


def start():
    # CibWorker.start(middleware=middleware)
    pass
