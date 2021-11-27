from myspiders.ruia import JsonField, HtmlField, AttrField, TextField, RegexField, Item, Spider, Request
from myspiders.ruia.plugins.ua_random import middleware
from urllib.parse import urlencode, urlparse, urljoin, quote
from config import CONFIG
from config import DocumentUrl
import re


def get_fetch_params_all(page_count: int):
    form_data = [
        {
            'dse_operationName': 'per_FinanceCurProAllInfoElementP3NSOp',
            'pageFlag_turn': '2',
            'nowPageNum_turn': str(index),
            'structCode': '1',
        } for index in range(2, page_count+1)
    ]
    first_page = {
        'dse_operationName': 'per_FinanceCurProAllInfoElementP3NSOp',
        'pageFlag_turn': '0',
        'nowPageNum_turn': '1',
        'structCode': '1',
    }
    form_data.insert(0, first_page)
    return form_data


def get_fetch_params(page_count: int):
    form_data = [
        {
            'dse_operationName': 'per_FinanceCurProListP3NSOp',
            'financeQueryCondition': '$$$$$$$2$%s$11|ALL$1' % str(index),
            'useFinanceSolrFlag': '1',
            'orderclick': '0',
            'menuLabel': '11|ALL',
            'pageFlag_turn': '2',
            'nowPageNum_turn': str(index),
            'Area_code': '1100',
            'structCode': '1',
        } for index in range(2, page_count+1)
    ]
    first_page = {
        'dse_operationName': 'per_FinanceCurProListP3NSOp',
        'financeQueryCondition': '$$$$$$$1$1$11|ALL$1',
        'useFinanceSolrFlag': '1',
        'orderclick': '0',
        'menuLabel': '11|ALL',
        'pageFlag_turn': '1',
        'nowPageNum_turn': '1',
        'Area_code': '1100',
        'structCode': '1',
    }
    form_data.insert(0, first_page)
    return form_data



# Item类中，类属性，其子类无法继承使用
# 不同于Spider类，在初始化实例时，会将类变量，都添加进实例变量的构造方法中，以供子类使用
class IcbcItemPrimary(Item):
    pattern_code = re.compile(r'open_protocolSubmit\(\'(.+)\',\'(.+)\',\'.*\'\)')
    pattern_risk = re.compile(r'setContentsText\("(.*)"\)')

    target_item = HtmlField(css_select='#datatableModel .ebdp-pc4promote-circularcontainer-wrapper')

    code = AttrField(css_select='.ebdp-pc4promote-circularcontainer-head .ebdp-pc4promote-circularcontainer-title-ellipsis a', attr='href')
    raise_period = TextField(css_select='.ebdp-pc4promote-circularcontainer-head .ebdp-pc4promote-circularcontainer-head-center')

    rate_type = TextField(css_select='.ebdp-pc4promote-circularcontainer-content table tr td:first-child div div:first-child')
    rate_min = TextField(css_select='.ebdp-pc4promote-circularcontainer-content table tr td:first-child div div:last-child')
    rate_max = TextField(css_select='.ebdp-pc4promote-circularcontainer-content table tr td:first-child div div:last-child')

    amount_buy_min = TextField(css_select='.ebdp-pc4promote-circularcontainer-content table tr td:nth-child(2) div div:last-child')
    term = TextField(css_select='.ebdp-pc4promote-circularcontainer-content table tr td:nth-child(3) div div:last-child')

    # get_fetch_params()方法时使用
    risk = TextField(css_select='.ebdp-pc4promote-circularcontainer-content table tr td:nth-child(4) div div:last-child')

    async def clean_code(self, code):
        results = self.pattern_code.search(code)
        if results:
            code = results.group(1)
            name = results.group(2)
            self.results['_id'] = code
            self.results['name'] = name
        else:
            self.results['_id'] = ''
            self.results['name'] = ''
        return code


class IcbcItemAll(Item):
    pattern_code = re.compile(r'open_protocolSubmit\(\'(.+)\',\'(.+)\',\'.*\'\)')
    pattern_risk = re.compile(r'setContentsText\("(.*)"\)')

    target_item = HtmlField(css_select='#datatableModel .ebdp-pc4promote-circularcontainer-wrapper')

    code = AttrField(css_select='.ebdp-pc4promote-circularcontainer-head .ebdp-pc4promote-circularcontainer-title-ellipsis a', attr='href')
    raise_period = TextField(css_select='.ebdp-pc4promote-circularcontainer-head .ebdp-pc4promote-circularcontainer-head-center')

    rate_type = TextField(css_select='.ebdp-pc4promote-circularcontainer-content table tr td:first-child div div:first-child')
    rate_min = TextField(css_select='.ebdp-pc4promote-circularcontainer-content table tr td:first-child div div:last-child')
    rate_max = TextField(css_select='.ebdp-pc4promote-circularcontainer-content table tr td:first-child div div:last-child')

    amount_buy_min = TextField(css_select='.ebdp-pc4promote-circularcontainer-content table tr td:nth-child(2) div div:last-child')
    term = TextField(css_select='.ebdp-pc4promote-circularcontainer-content table tr td:nth-child(3) div div:last-child')

    # get_fetch_params_all()方法时使用
    risk = HtmlField(css_select='.ebdp-pc4promote-circularcontainer-content table tr td:nth-child(4) script')

    async def clean_code(self, code):
        results = self.pattern_code.search(code)
        if results:
            code = results.group(1)
            name = results.group(2)
            self.results['_id'] = code
            self.results['name'] = name
        else:
            self.results['_id'] = ''
            self.results['name'] = ''
        return code

    # get_fetch_params_all()方法时使用
    async def clean_risk(self, risk):
         result = self.pattern_risk.search(risk)
         if result:
             risk = result.group(1)
         return risk


class IcbcWorker(Spider):
    name = 'IcbcWorker'
    bank_name = '工商银行'

    print('================已初始化%s==================' % name)
    # page_count = CONFIG.CRAWL_PAGE_COUNT
    page_count = 73
    # page_size = 15
    start_urls = ['https://mybank.icbc.com.cn/servlet/ICBCBaseReqServletNoSession']
    # form_data = get_fetch_params(page_count)
    # form_data = get_fetch_params_all(page_count)

    manual_url_prefix = 'https://image.mybank.icbc.com.cn/picture/Perfinancingproduct/%s.pdf'
    html_type = CONFIG.HTML_TYPE['manual']

    async def process_item(self, item: Item):
        data = item.results
        if data['_id']:
            self.mongo.do_insert_one(self.collection_list,  {'_id': data['_id']}, data)
            self.save_manual_url(data)

    def save_manual_url(self, data):
        code = data['code']
        ukey = self.bank_name + '=' + code
        url = self.manual_url_prefix % str(code)
        manual_url = DocumentUrl(ukey=ukey, url=url, html_type=self.html_type)
        manual_url_data = manual_url.do_dict_data()
        self.mongo.do_insert_one(self.collection_file, {'_id': ukey}, manual_url_data)


class IcbcWorkerPrimary(IcbcWorker):
    name = 'IcbcWorkerPrimary'

    print('================已初始化%s==================' % name)
    page_count = 18
    form_data = get_fetch_params(page_count)

    async def parse(self, response):
        html = await response.text()
        async for item in IcbcItemPrimary.get_items(html=html):
            yield item


class IcbcWorkerAll(IcbcWorker):
    name = 'IcbcWorkerAll'

    print('================已初始化%s==================' % name)
    page_count = 73
    form_data = get_fetch_params_all(page_count)

    async def parse(self, response):
        html = await response.text()
        async for item in IcbcItemAll.get_items(html=html):
            yield item


def start():
    #IcbcWorkerPrimary.start(middleware=middleware)
    #IcbcWorkerAll.start(middleware=middleware)
    pass





