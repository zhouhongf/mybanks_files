import math
import json
from config import CONFIG
import time
import os
import re
import traceback
import farmhash
from myspiders.ruia import JsonField, HtmlField, AttrField, TextField, RegexField, Item, Spider, Request
from urllib.parse import urlencode, urlparse, urljoin, quote
from myspiders.tools.tools_request import get_random_user_agent
from config import DocumentUrl
from bs4 import BeautifulSoup


branch_code_name = [
    {"code": "340", "name": "安徽省"},
    {"code": "110", "name": "北京市"},
    {"code": "500", "name": "重庆市"},
    {"code": "212", "name": "大连市"},
    {"code": "350", "name": "福建省"},
    {"code": "440", "name": "广东省"},
    {"code": "450", "name": "广西省"},
    {"code": "620", "name": "甘肃省"},
    {"code": "520", "name": "贵州省"},
    {"code": "460", "name": "海南省"},
    {"code": "130", "name": "河北省"},
    {"code": "410", "name": "河南省"},
    {"code": "230", "name": "黑龙江"},
    {"code": "420", "name": "湖北省"},
    {"code": "430", "name": "湖南省"},
    {"code": "220", "name": "吉林省"},
    {"code": "320", "name": "江苏省"},
    {"code": "360", "name": "江西省"},
    {"code": "210", "name": "辽宁省"},
    {"code": "150", "name": "内蒙古"},
    {"code": "331", "name": "宁波市"},
    {"code": "640", "name": "宁夏区"},
    {"code": "371", "name": "青岛市"},
    {"code": "630", "name": "青海省"},
    {"code": "370", "name": "山东省"},
    {"code": "140", "name": "山西省"},
    {"code": "610", "name": "陕西省"},
    {"code": "310", "name": "上海市"},
    {"code": "510", "name": "四川省"},
    {"code": "442", "name": "深圳市"},
    {"code": "322", "name": "苏州市"},
    {"code": "120", "name": "天津市"},
    {"code": "351", "name": "厦门市"},
    {"code": "540", "name": "西藏区"},
    {"code": "650", "name": "新疆区"},
    {"code": "530", "name": "云南省"},
    {"code": "330", "name": "浙江省"}
]
#  各省份分行ID
branch_codes = [
    '340', '110', '500', '212', '350',
    '440', '450', '620', '520', '460',
    '130', '410', '230', '420', '430',
    '220', '320', '360', '210', '150',
    '331', '640', '371', '630', '370',
    '140', '610', '310', '510', '442',
    '322', '120', '351', '540', '650',
    '530', '330'
]

# 1 净值型, 0 非净值型
is_net_values = ['0', '1']

pattern_http_url = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')


class CcbItem(Item):
    target_item = JsonField(json_select='ProdList')
    # 可信度，可被引用的程度，五级分类，由低到高：低、较低、中、较高、高
    referenceable = JsonField(default='高')
    crawl_status = JsonField(default='undo')

    _id = JsonField(json_select='code')
    code = JsonField(json_select='code')
    name = JsonField(json_select='name')

    term = JsonField(json_select='investPeriod')
    risk = JsonField(json_select='riskLevel')
    amount_buy_min = JsonField(json_select='purFloorAmt')
    amount_per_buy = JsonField(json_select='purStepAmt')

    rate_min = JsonField(json_select='yieldRate')
    rate_max = JsonField(json_select='yieldRate')

    date_open = JsonField(json_select='collBgnDate')
    date_close = JsonField(json_select='collEndDate')
    date_start = JsonField(json_select='investBgnDate')
    date_end = JsonField(json_select='investEndDate')

    sale_ways = JsonField(json_select='channel')
    sale_areas = JsonField(json_select='provinceId')

    rate_type = JsonField(json_select='isNetvalPro')
    redeem_type = JsonField(json_select='proMode')
    promise_type = JsonField(json_select='yieldSpec')

    code_register = JsonField()
    currency = JsonField(json_select='currencyType')

    manual_url = JsonField(json_select='instructionUrl')
    notice_url = JsonField(json_select='pubNoticeUrl')

    async def clean__id(self, value):
        return '建设银行=' + value

    async def clean_risk(self, value):
        if value is not None:
            return int(value)
        else:
            return None

    async def clean_rate_min(self, value):
        if value is not None:
            return round(value/100, 6)
        else:
            return None

    async def clean_rate_max(self, value):
        if value is not None:
            return round(value/100, 6)
        else:
            return None

    async def clean_currency(self, value):
        if value == '01':
            return '人民币'
        elif value == "12":
            return '英镑'
        elif value == '13':
            return '港币'
        elif value == '14':
            return '美元'
        elif value == '15':
            return '瑞士法郎'
        elif value == '27':
            return '日元'
        elif value == '28':
            return '加元'
        elif value == '29':
            return '澳元'
        elif value == '33':
            return '欧元'
        else:
            return None

    async def clean_sale_areas(self, value):
        if value is None:
            return '全国'
        else:
            value_back = ''
            if isinstance(value, str):
                value_list = value.split(',')
                for code in value_list:
                    for one in branch_code_name:
                        if code == one['code']:
                            value_back += one['name']
            return value_back

    async def clean_rate_type(self, value):
        if value == '0':
            return '非净值型'
        elif value == '1':
            return '净值型'
        else:
            return None

    async def clean_redeem_type(self, value):
        if value == '0':
            return '封闭式'
        elif value == '1':
            return '开发式'
        else:
            return None

    async def clean_promise_type(self, value):
        if value == '0':
            return '非保本'
        elif value == '1':
            return '保本'
        else:
            return None

    async def clean_manual_url(self, value):
        res = pattern_http_url.search(value)
        if res:
            return res.group(0)
        else:
            return None

    async def clean_notice_url(self, value):
        res = pattern_http_url.search(value)
        if res:
            return res.group(0)
        else:
            return None


# queryForm.isNetvalPro, 1 净值型, 0 非净值型
# queryForm.provinceId，省份ID前3位
# queryForm.saleStatus, 销售状态 -1 在售 03 可预约 04 待售 05 已售完， 如不添加，则包含全部状态的理财产品
# queryForm.brand，  03 乾元 01 利得盈 02 建行财富 04 汇得盈 05 其他
# queryForm.yieldSpec: 0 非保本 1 保本
def get_fetch_params(page_start: int, page_count: int, province_id: str, is_net_value: str):
    form_data = [
        {
            'queryForm.isNetvalPro': is_net_value,
            'queryForm.provinceId': province_id,
            'queryForm.saleStatus': -1,
            'pageNo': index,
            'pageSize': 12
        } for index in range(page_start, page_count + 1)
    ]
    return form_data


class CcbWorker(Spider):
    name = 'CcbWorker'
    bank_name = '建设银行'

    headers = {'Referer': 'http://finance.ccb.com/cn/finance/product.html'}
    print('================已初始化%s==================' % name)
    begin_url = 'http://finance.ccb.com/cc_webtran/queryFinanceProdList.gsp'
    html_type = CONFIG.HTML_TYPE['manual']
    bank_domain = 'http://www.ccb.com/'

    # 根据各省份ID和是否是净值型，先获取第一页内容，得到各种类型下的总页数多少
    async def start_manual(self):
        for one in branch_codes:
            for two in is_net_values:
                form_datas = get_fetch_params(1, 1, one, two)
                for form_data in form_datas:
                    yield self.request(url=self.begin_url, form_data=form_data, callback=self.parse, metadata={'branch_code': one, 'is_net_value': two})

    async def parse(self, response):
        jsondata = await response.json(content_type='text/html')
        async for item in CcbItem.get_json(jsondata=jsondata):
            yield item

        # 在获取第一页，得到各种情况下的总页数后，再进一步获取剩余的页数内容
        if response.metadata:
            branch_code = response.metadata['branch_code']
            is_net_value = response.metadata['is_net_value']
            if branch_code and is_net_value:
                total_count = jsondata['totalCount']
                if total_count is not None:
                    page_count = math.ceil(total_count / 12)
                    if page_count > 1:
                        form_datas = get_fetch_params(2, page_count, branch_code, is_net_value)
                        for form_data in form_datas:
                            yield self.request(url=self.begin_url, form_data=form_data, callback=self.parse)

    async def process_item(self, item: Item):
        data = item.results
        manual_url = data['manual_url']
        # 如果解析出来的manual_url链接是以pdf结尾的，则直接保存到collection_file中，并且将该条数据标记为crawl_status为done
        if manual_url and manual_url.endswith('.pdf'):
            if not manual_url.startswith('http://'):
                manual_url = urljoin(self.bank_domain, manual_url)
                print('新添加的完整的Manual链接是：', manual_url)

            manual = DocumentUrl(ukey=data['_id'], url=manual_url, html_type=self.html_type)
            manual_data = manual.do_dict_data()
            self.mongo.do_insert_one(self.collection_file, {'_id': data['_id']}, manual_data)
            data['crawl_status'] = 'done'

        # 保存获取到的理财列表信息
        self.mongo.do_insert_one(self.collection_list, {'_id': data['_id']}, data)


class CcbWorkerMore(Spider):
    name = 'CcbWorkerMore'
    bank_name = '建设银行'

    print('================已初始化%s==================' % name)
    html_type = CONFIG.HTML_TYPE['manual']
    bank_domain = 'http://www.ccb.com/'

    # 从mongo中获取的建设银行的状态为undo的wealth_list的信息
    async def start_manual(self):
        results = self.collection_list.find({'crawl_status': 'undo'})
        if results:
            for one in results:
                manual_url = one['manual_url']
                if manual_url and manual_url.endswith('.html'):
                    yield self.request(url=manual_url, callback=self.parse, metadata={'one': one})

    async def parse(self, response):
        one = response.metadata['one']
        ukey = one['_id']

        # 在全部的a标签中寻找第一个PDF结尾的链接
        content = await response.text()
        soup = BeautifulSoup(content, 'lxml')
        list_a = soup.find_all(name='a')
        if list_a:
            target_url = ''
            for a in list_a:
                url = a.get('href')
                if url and url.endswith('.pdf'):
                    target_url = url
                    break

            # 如果存在pdf结尾的链接，则保存进MANUAL_URL表中，并且更新wealth_list表中该条数据的状态为done
            # 如果不存在，则在html页面上寻找.content.f14类标签，将其保存进数据库中
            if target_url:
                if not target_url.startswith('http://'):
                    target_url = urljoin(self.bank_domain, target_url)
                manual = DocumentUrl(ukey=ukey, url=target_url, html_type=self.html_type)
                manual_data = manual.do_dict_data()
                self.mongo.do_insert_one(self.collection_file, {'_id': ukey}, manual_data)

                one['crawl_status'] = 'done'
                self.collection_list.update_one({'_id': ukey}, {'$set': one})
            else:
                body = soup.select_one('.content.f14')
                if body:
                    self.save_html_file(ukey, str(body))
                    print('已保存进MySQL：', ukey)

                    one['crawl_status'] = 'done'
                    self.collection_list.update_one({'_id': ukey}, {'$set': one})

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
    # CcbWorker.start()
    # CcbWorkerMore.start()
    pass
