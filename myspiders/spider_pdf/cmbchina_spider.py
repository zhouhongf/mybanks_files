from myspiders.ruia import JsonField, AttrField, Item, Spider
from myspiders.ruia.plugins.ua_random import middleware
from urllib.parse import urlencode, urlparse
from config import CONFIG
import random
import demjson
from config import DocumentUrl


def get_fetch_urls(start_url_prefix: str, page_index: int, page_size: int):
    params = {
        'op': 'search',
        'type': 'm',
        'pageindex': str(page_index),
        'salestatus': '',                           # A可购买， B即将发售
        'baoben': '',                               # Y保本， N不保本
        'currency': '',                             # 10人民币，32美元，43英镑，35欧元，65日元，21港币，39加元，87瑞郎，29澳元，69新元
        'term': '',                                 # 1：7天含以下，2：8天-14天（含），3：15天-30天（含），4：31天-90天（含），5：91天-180天（含），6：181天-365天（含），7：365天以上
        'keyword': '',                              # 产品关键词
        'series': '01',                             # 01：不限，010017：私人银行单一资产系列，010012：私人银行家业常青系列，010016：私人银行多元配置系列，010015：私人银行专享联动系列，010013：私行债券套利系列，010011：A009 结构性存款系列，010001：海外寻宝系列，010002：焦点联动系列，010003：日日金系列，010004：新股申购系列，010005：安心回报系列，010006：稳健收益型外币系列，010007：招银进宝系列，010008：A股掘金系列，010009：私人银行系列
        'risk': '',                                 # R1(谨慎型)，R2(稳健型)，R3(平衡型)，R4(进取型)，R5(激进型)
        'city': '',
        'date': '',
        'pagesize': str(page_size),
        'orderby': 'ord1',                          # ord1发售时间（降序），ord2发售时间（升序），ord3收益率（降序），ord4收益率（升序）, ord5风险级别（降序），ord6风险级别（升序）, ord7产品到期日（降序）,ord8产品到期日（升序），ord9理财期限（降序），ord10理财期限（升序）
        't': str(random.random()),
        'citycode': '',                             # 同行政区号，如0512苏州，0025南京
    }
    start_url = start_url_prefix + urlencode(params)
    return start_url


class CmbchinaWorker(Spider):
    name = 'CmbchinaWorker'
    bank_name = '招商银行'
    bank_domain = 'http://www.cmbchina.com/'
    headers = {'Referer': 'http://www.cmbchina.com/cfweb/Personal/Default.aspx'}

    print('================已运行%s==================' % name)
    page_index = 1
    page_size = 80
    page_item_less = 10
    start_url_prefix = 'http://www.cmbchina.com/cfweb/svrajax/product.ashx?'
    start_urls = [get_fetch_urls(start_url_prefix, page_index, page_size)]

    risk_transfer = {
        'R1(谨慎型)': 1,
        'R2(稳健型)': 2,
        'R3(平衡型)': 3,
        'R4(进取型)': 4,
        'R5(激进型)': 5
    }

    def save_list_db(self, jsondata):
        insert_number = 0
        list_data = jsondata['list']
        for one in list_data:
            data = {
                'referencable': '较高',
                '_id': self.bank_name + '=' + one['PrdCode'],
                'code': one['PrdCode'],
                'name': one['PrdName'],
                'code_register': one['REGCode'],
                'risk': '',
                'amount_buy_min': one['InitMoney'],
                'amount_per_buy': one['IncresingMoney'],
                'date_open': one['BeginDate'],
                'date_close': one['EndDate'],
                'date_start': '',
                'date_end': one['ExpireDate'],
                'currency': one['Currency'],
                'term': one['FinDate'],
                'rate_min': one['NetValue'],
                'rate_max': one['NetValue'],
                'sale_ways': one['SaleChannelName'],
                'sale_areas': one['AreaCode']
            }

            risk = one['Risk']
            if risk:
                data['risk'] = self.risk_transfer[risk]

            term = data['term']
            if term and '天' in term:
                data['term'] = term.replace('天', '')
            sale_ways = data['sale_ways']
            if sale_ways:
                data['sale_ways'] = sale_ways.replace('|', ',')

            back = self.mongo.do_insert_one(self.collection_list, {'_id': data['_id']}, data)
            if back:
                insert_number += 1
        return insert_number

    async def parse(self, response):
        content = await response.text()
        jsondata = demjson.decode(content[1:-1])

        insert_number = self.save_list_db(jsondata)
        # 允许有10个数目的差别，仍旧可以再请求下一页
        if insert_number > self.page_size - self.page_item_less:
            self.page_index += 1
            start_url = get_fetch_urls(self.start_url_prefix, self.page_index, self.page_size)
            yield self.request(url=start_url, callback=self.parse)


class CmbchinaPDFItem(Item):
    url = AttrField(css_select='#ctl00_cphBody_info_PDF', attr='onclick')

    async def clean_url(self, link):
        links = link.split('=')
        url = links[-1].strip()
        url = url[1:-1]
        if url.endswith('.pdf') or url.endswith('.doc') or url.endswith('.docx'):
            return url
        else:
            return None


class CmbchinaPDFSupplementItem(Item):
    url = AttrField(css_select='#content_panel a', attr='href')

    async def clean_url(self, url):
        if url.endswith('.pdf') or url.endswith('.doc') or url.endswith('.docx'):
            return url
        else:
            return None


class CmbchinaMoreWorker(Spider):
    name = 'CmbchinaMoreWorker'
    bank_name = '招商银行'
    bank_domain = 'http://www.cmbchina.com/'

    print('================已运行%s==================' % name)
    manual_url_prefix = 'https://mobile.cmbchina.com/IEntrustFinance/FinanceProduct/FP_PrdInstruction.aspx?Code='
    manual_url_prefix_supplement = 'http://www.cmbchina.com/cfweb/Personal/productdetail.aspx?code=%s&type=prodexplain'
    html_type = CONFIG.HTML_TYPE['manual']

    async def start_manual(self):
        list_code_need = []
        list_code = self.collection_list.find({}, {'code': True})
        if list_code:
            for one in list_code:
                ukey = one['_id']
                code = one['code']
                back = self.collection_file.find_one({'_id': ukey})
                if not back:
                    list_code_need.append(code)

        if list_code_need:
            print('需要爬取的code有：', list_code_need)
            for code in list_code_need:
                url = self.manual_url_prefix + code
                yield self.request(url=url, callback=self.parse, metadata={'code': code})

    async def parse(self, response):
        code = response.metadata['code']
        html = await response.text()
        item = await CmbchinaPDFItem.get_item(html=html)
        url = item.results['url']
        if url:
            item.results['_id'] = self.bank_name + '=' + code
            yield item
        else:
            url_new = self.manual_url_prefix_supplement % code
            yield self.request(url=url_new, callback=self.parse_supplement, metadata={'code': code})

    async def parse_supplement(self, response):
        code = response.metadata['code']
        html = await response.text()
        item = await CmbchinaPDFSupplementItem.get_item(html=html)
        url = item.results['url']
        if url:
            item.results['_id'] = self.bank_name + '=' + code
            yield item

    async def process_item(self, item: Item):
        data = item.results
        manual = DocumentUrl(ukey=data['_id'], url=data['url'], html_type=self.html_type)
        manual_data = manual.do_dict_data()
        self.mongo.do_insert_one(self.collection_file, {'_id': data['_id']}, manual_data)


def start():
    # CmbchinaWorker.start(middleware=middleware)
    # CmbchinaMoreWorker.start(middleware=middleware)
    pass
