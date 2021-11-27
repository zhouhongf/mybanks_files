import time
from myspiders.ruia import JsonField, Item, Spider
from myspiders.ruia.plugins.ua_random import middleware


class CmbcItem(Item):
    referencable = JsonField(default='唯一')
    bank_level = JsonField(default='股份银行')
    create_time = JsonField(default=time.strftime('%Y-%m-%d %H:%M:%S'))

    _id = JsonField(json_select='PrdCode')

    code = JsonField(json_select='PrdCode')
    code_register = JsonField(json_select='ContractFile')
    name = JsonField(json_select='PrdName')
    risk = JsonField(json_select='RiskLevel')
    currency = JsonField(json_select='CurrTypeName')
    term = JsonField(json_select='LiveTime')
    term_looped = JsonField(json_select='PrdFeature')

    amount_buy_min = JsonField(json_select='PfirstAmt')
    amount_buy_max = JsonField(json_select='PmaxAmt')
    amount_per_buy = JsonField(json_select='PsubUnit')
    amount_size_max = JsonField(default=None)
    amount_size_min = JsonField(default=None)

    sale_ways = JsonField(json_select='ChannelsName')

    rate_min = JsonField(json_select='IncomeRateStart')
    rate_max = JsonField(json_select='IncomeRateEnd')

    date_open = JsonField(json_select='IpoStartDate')
    date_close = JsonField(json_select='IpoEndDate')
    date_start = JsonField(json_select='StartDate')
    date_end = JsonField(json_select='EndDate')

    custodian = JsonField(json_select=None)
    fee_rate = JsonField(json_select=None)
    fee_types = JsonField(json_select=None)
    invest_on = JsonField(json_select=None)
    loan_rule = JsonField(json_select=None)
    sale_agents = JsonField(json_select=None)
    sale_areas = JsonField(json_select=None)

    raise_type = JsonField(json_select='ClientGroupsName')
    fixed_type = JsonField(json_select='IncomeTypeName')
    promise_type = JsonField(json_select='FundModeName')
    rate_type = JsonField(json_select='PrdAttrName')
    redeem_type = JsonField(json_select='ProdTypeName')

    async def clean__id(self, value):
        return '民生银行=' + value

    async def clean_sale_ways(self, value):
        return value.replace(';', ',')


class CmbcWorker(Spider):
    name = 'CmbcWorker'
    bank_name = '民生银行'
    bank_domain = 'http://www.cmbc.com.cn/'

    start_urls = ['https://www.mszxyh.com/peweb/DBFinanceQuotaInfo.do']
    form_data = [{'QryType': '0'}]
    print('================已初始化%s==================' % name)
    manual_detail_url = 'https://www.mszxyh.com/peweb/DBFinancePrdDetailInfo.do'

    async def parse(self, response):
        list_code = []
        jsondata = await response.json()
        if jsondata:
            list_data = jsondata['List']
            if list_data:
                for one in list_data:
                    code = one['PrdCode']
                    back = self.collection_list.find_one({'_id': self.bank_name + '=' + code})
                    if not back:
                        list_code.append(code)

        for code in list_code:
            form_data_manual = {'PrdCode': code}
            self.headers.update({'Referer': 'https://www.mszxyh.com/peweb/static/dBankMain.html?pid=index'})
            yield self.request(url=self.manual_detail_url, form_data=form_data_manual, callback=self.parse_manual)

    async def parse_manual(self, response):
        jsondata = await response.json()
        if jsondata:
            async for item in CmbcItem.get_json(jsondata=jsondata):
                yield item

    async def process_item(self, item: Item):
        data = item.results
        self.mongo.do_insert_one(self.collection_list,  {'_id': data['_id']}, data)


def start():
    # CmbcWorker.start(middleware=middleware)
    pass
