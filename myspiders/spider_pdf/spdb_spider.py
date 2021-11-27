from myspiders.ruia import JsonField, Item, Spider, Request
from myspiders.ruia.plugins.ua_random import middleware
import json
from config import CONFIG
from config import DocumentUrl
import time
from urllib.parse import quote, urljoin
import re

# 产品类型 参数：
# 固定期限：   (product_type=3)*finance_limittime = %*(finance_currency = 01)*(finance_state='可购买')
# 现金管理类： (product_type=4)*finance_limittime = %*(finance_currency = 01)*(finance_state='可购买')
# 净值类：     (product_type=2)*finance_limittime = %*(finance_currency = 01)*(finance_state='可购买')
# 汇理财：                      finance_limittime = %*(finance_currency = 01)*(finance_state='可购买')
# 私行专属：   (product_type=0)*finance_limittime = %*(finance_currency = 01)*(finance_state='可购买')
# 专属产品：   (product_type=1)*finance_limittime = %*(finance_currency = 01)*(finance_state='可购买')
# 销售状态 参数：
# 即将发售：  (product_type=3)*finance_limittime = %*(finance_currency = 01)*(finance_state='即将发售')
# 可购买：    (product_type=3)*finance_limittime = %*(finance_currency = 01)*(finance_state='可购买')  默认
# 不可购买：  (product_type=3)*finance_limittime = %*(finance_currency = 01)*(finance_state='不可购买')
# 已过期：    (product_type=3)*finance_limittime = %*(finance_currency = 01)*(finance_state='已过期')

# 下载PDF文件 也需要cookies


class SpdbItem(Item):
    code = JsonField(json_select='finance_no')
    name = JsonField(json_select='finance_allname')
    risk = JsonField(json_select='finance_risklevel')
    amount_buy_min = JsonField(json_select='finance_indi_ipominamnt')
    term = JsonField(json_select='finance_limittime')
    rate_min = JsonField(json_select='finance_anticipate_rate')
    rate_max = JsonField(json_select='finance_anticipate_rate')
    manual_url = JsonField(json_select='product_attr')
    notice_url = JsonField(json_select='docpuburl')

    async def clean_manual_url(self, value):
        if not value.startswith('http://'):
            value = urljoin('https://per.spdb.com.cn/', value)
        return value

    async def clean_notice_url(self, value):
        if not value.startswith('http://'):
            value = urljoin('https://per.spdb.com.cn/', value)
        return value


def get_form_data_one(page_index, searchword):
    formdata = {
        "metadata": "finance_state|finance_no|finance_allname|finance_anticipate_rate|finance_limittime|finance_lmttime_info|finance_type|docpuburl|finance_ipo_enddate|finance_indi_ipominamnt|finance_indi_applminamnt|finance_risklevel|product_attr|finance_ipoapp_flag|finance_next_openday",
        "channelid": "266906",
        "page": str(page_index),
        "searchword": searchword,
    }
    return formdata


# 仅供爬取 汇理财 使用
def get_form_data_two(page_index, searchword):
    formdata = {
        "metadata": "finance_allname|finance_anticipate_rate|finance_limittime|finance_indi_ipominamnt|finance_type|finance_no|finance_state|docpuburl|finance_risklevel|product_attr",
        "channelid": "263468",
        "page": str(page_index),
        "searchword": searchword,
    }
    return formdata


lua_init = '''
function main(splash, args)
    local myheaders = {}
    myheaders['User-Agent']='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'
    assert(splash:go{'%s', headers=myheaders})
    assert(splash:wait(2))
    return {
        html = splash:html(),
        cookies = splash:get_cookies(),
    }
end'''


class SpdbWorker(Spider):
    name = 'SpdbWorker'
    bank_name = '浦发银行'
    bank_domain = 'https://per.spdb.com.cn/'
    headers = {'Referer': 'https://per.spdb.com.cn/bank_financing/financial_product'}

    print('================已运行%s==================' % name)
    html_type = CONFIG.HTML_TYPE['manual']
    splash_url = 'http://localhost:8050/execute?lua_source='
    cookie_url = 'https://per.spdb.com.cn/bank_financing/financial_product'
    begin_url = 'https://per.spdb.com.cn/was5/web/search'

    # finance_state_list = ['可购买', '即将发售', '不可购买', '已过期']
    currency_dicts = {'01': '人民币', '14': '美元', '12': '英镑', '13': '港币'}
    product_type_dicts = {'0': '私行专属', '1': '专属产品', '2': '净值类', '3': '固定期限', '4': '现金管理类'}
    # product_type_special = '汇理财'

    def get_cookie_need(self, cookies):
        query_set = set()
        for cookie in cookies:
            name = cookie['name'].strip()
            value = cookie['value'].strip()
            if name == 'TSPD_101' or name == 'TS01d02f4c' or name == 'WASSESSION':
                query = name + '=' + value + ';'
                query_set.add(query)
            elif name.startswith('Hm_lvt_') or name.startswith('Hm_lpvt_'):
                query = name + '=' + value + ';'
                query_set.add(query)
        cookie_need = ''
        for query in query_set:
            cookie_need += query
        print('SpdbWorker提取出来的cookie是：', cookie_need)
        return cookie_need

    async def start_manual(self):
        lua = lua_init % self.cookie_url
        url = self.splash_url + quote(lua)
        yield Request(url=url, callback=self.parse_cookie)

    async def parse_cookie(self, response):
        jsondata = await response.json()
        cookies = jsondata['cookies']
        cookie_need = self.get_cookie_need(cookies)
        self.headers.update({'Cookie': cookie_need})

        list_formdata = []
        for product_type in self.product_type_dicts.keys():
            for currency in self.currency_dicts.keys():
                searchword = "(product_type=%s)*finance_limittime = %s*(finance_currency = %s)*(finance_state='可购买')" % (product_type, '%', currency)
                form_data = get_form_data_one(1, searchword)
                list_formdata.append(form_data)
        # 爬取汇理财
        for currency in self.currency_dicts.keys():
            searchword = "finance_limittime = %s*(finance_currency = %s)*(finance_state='可购买')" % ('%', currency)
            form_data = get_form_data_two(1, searchword)
            list_formdata.append(form_data)

        for form_data in list_formdata:
            yield self.request(url=self.begin_url, form_data=form_data, callback=self.parse, metadata={'form_data': form_data})

    async def parse(self, response):
        metadata = response.metadata
        form_data = metadata['form_data']
        if response.status == 200:
            text = await response.text()
            if text.strip():
                jsondata = json.loads(text.strip())
                if jsondata:
                    page_total = jsondata['pageTotal']
                    data_list = jsondata['rows']
                    yield self.save_data(form_data, data_list)

                    # 如果form_data中page参数是1，则表示是才请求完第一页，因此需要检查是否还有后面的页数，可以爬取
                    page_index_current = form_data['page']
                    if page_index_current == '1':
                        if page_total and int(page_total) > 1:
                            for page_index in range(2, int(page_total) + 1):
                                form_data['page'] = str(page_index)
                                yield self.request(url=self.begin_url, form_data=form_data, callback=self.parse, metadata={'form_data': form_data})

    async def save_data(self, form_data, data_list):
        currency = ''
        searchword = form_data['searchword']
        pattern = re.compile(r'finance_currency\s*=\s*(\d+)')
        result = pattern.search(searchword)
        if result:
            num = result.group(1)
            if num:
                if num == '01':
                    currency = '人民币'
                elif num == '12':
                    currency = '英镑'
                elif num == '13':
                    currency = '港币'
                elif num == '14':
                    currency = '美元'

        async for item in SpdbItem.get_json(jsondata=data_list):
            item.results['_id'] = self.bank_name + '=' + item.results['code']
            item.results['currency'] = currency
            yield item

    async def process_item(self, item: Item):
        data = item.results
        result = self.mongo.do_insert_one(self.collection_list,  {'_id': data['_id']}, data)
        # 存入数据库的manual_url与list保持一致，如果list返回表示新增数据，则manual_url也进行新增处理
        if result:
            manual = DocumentUrl(ukey=data['_id'], url=data['manual_url'], html_type=self.html_type)
            manual_data = manual.do_dict_data()
            self.mongo.do_insert_one(self.collection_file, {'_id': data['_id']}, manual_data)


def start():
    # SpdbWorker.start(middleware=middleware)
    pass
