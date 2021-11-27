from myspiders.ruia import JsonField, Item, Spider, Request, HtmlField
from myspiders.ruia.plugins.ua_random import middleware
from utils.string_util import random_digits
import json
from database.backends import MongoDatabase
from config import CONFIG
import os

import asyncio
import lzma


spider_start_urls = ["https://etrade.citicbank.com/portalweb/fd/getFinaList.htm"]
page_size = 10

bank_name = '中信银行'
index_key = 'code'
manual_is_file = False

manual_name = bank_name + '-MANUAL'
mongo = MongoDatabase()
db = mongo.db()
collection_list = db[bank_name]
collection_manual = db[manual_name]

file_path = os.path.join(CONFIG.DATA_DIR, bank_name)
os.makedirs(file_path, exist_ok=True)

manual_url_prefix = 'https://etrade.citicbank.com/portalweb/findoc/%s00.html'



def get_fetch_params(page_index):
    page_index = page_index + 1
    form_data = [
        {
            'currType': '',                         # 币   种， 01：人民币， 02：美元， 03：英镑， 04：欧元， 05：港币， 06：其他
            'dayDeadline': '',                      # 产品期限， 00：无固定期限，01：30天以下，02：31天到90天，03：91天到180天，04：181天到365天，05：365天以上
            'riskLevel': '',                        # 风险等级， 00：无风险， 01：低风险， 02：较低风险， 03：中等风险， 04：较高风险， 05：高风险
            'firstAmt': '',                         # 购买起点， 01：0至5万， 02：5至10万， 03：10至20万， 04：20万以上
            'branchId': '701100',
            'prodState': '',                        # 产品状态， 01：可购买， 02：即将发售  04：不能购买
            'openAttr': '',                         # 开放性质， 01：开放式， 02：封闭式
            'breakEvenAttr': '',                    # 保本性质， 01：保本， 02：不保本
            'endInterestDate': '',                  # 产品到期日， 譬如20190910，代表2019年9月10日
            'finaQrycondi': '',                     # 根据输入的产品代码或名称进行模糊搜索
            'totuseAmt': '01',                      # 销售额度， 01：显示全部产品， 02：仅显示有剩余额度的产品
            'orderField': 'ipo_start_date',         # 排序标准， ppo_incomerate：预期年化收益率， ipo_start_date：募集期， risk_level：风险等级， prod_name：产品名称， day_prddeadline：产品期限， first_amt：购买起点
            'orderType': 'desc',                    # 降序升序， desc:降序排列， asc:升序排列
            'currentPage': i,
            'pageSize': page_size,
            'tcstNo': '',
            'userId': '',
            'pwdControlFlag': '0',
            'responseFormat': 'JSON',
            'random': random_digits(4),
        } for i in range(1, page_index)
    ]
    return form_data


class CiticbankItem(Item):
    target_item = JsonField(json_select='content>resultList')
    code = JsonField(json_select='prdNo')
    name = JsonField(json_select='prdName')
    risk = JsonField(json_select='riskLevel')
    amount_start = JsonField(json_select='firstAmt')
    date_open = JsonField(json_select='ipoBeginDate')
    date_close = JsonField(json_select='ipoEndDate')
    date_start = JsonField(json_select='beginIntereastDate')
    date_end = JsonField(json_select='endIntereastDate')
    currency = JsonField(json_select='currType')
    term = JsonField(json_select='dayDeadLine')
    prod_type = JsonField(json_select='prdType')
    rate_last = JsonField(json_select='lastIncomeRate')
    rate_min = JsonField(json_select='incomerate')
    rate_max = JsonField(json_select='incomerate')

    async def clean_currency(self, currency):
        currency_code = int(currency)
        if currency_code == 1:
            currency = '人民币'
        elif currency_code == 2:
            currency = '美元'
        elif currency_code == 3:
            currency = '英镑'
        elif currency_code == 4:
            currency = '欧元'
        elif currency_code == 5:
            currency = '港币'
        else:
            currency = '其他'
        return currency


class CiticbankInit(Spider):
    name = 'CiticbankInit'
    start_urls = spider_start_urls
    form_data = get_fetch_params(118)

    async def parse(self, response):
        content = await response.text()
        jsondata = json.loads(content)
        yield self.parse_item(jsondata)

    async def parse_item(self, content):
        # jsondata = content['content']['resultList']
        # print('parse_item()方法获得jsondata是：%s' % jsondata)
        async for item in CiticbankItem.get_json(jsondata=content):
            yield item

    async def process_item(self, item: CiticbankItem):
        data = item.results
        condition = {index_key: data[index_key]}
        mongo.do_insert_one(collection_list, condition, data)


class CiticbankExplorer(Spider):
    name = 'CiticbankExplorer'
    print('================已运行%s==================' % name)
    list_news = set()

    def start_manual(self):
        url = spider_start_urls[0]
        page_index = 1
        while page_index > 0:
            print('【执行CiticbankExplorer中的start_manual()方法, 爬取第%s页】' % str(page_index))
            form_data = get_fetch_params(page_index)[0]
            yield self.request(url=url, form_data=form_data, callback=self.parse)
            if len(self.list_news) > 0 and (len(self.list_news) % page_size == 0):
                page_index += 1
            else:
                page_index = 0

    async def parse(self, response):
        content = await response.text()
        jsondata = json.loads(content)
        async for item in CiticbankItem.get_json(jsondata=jsondata):
            yield item

        if len(self.list_news) == 0:
            await asyncio.sleep(5)
            differs = ''
            start_urls = [(manual_url_prefix % code) for code in differs]
            await CiticbankSoldier.async_start(start_urls=start_urls, middleware=middleware, cancel_tasks=False)

    async def process_item(self, item: CiticbankItem):
        data = item.results
        print('来到process_item方法: %s' % data)
        condition = {index_key: data[index_key]}
        result = mongo.do_insert_one(collection_list, condition, data)
        if result:
            self.list_news.add(data[index_key])


class CiticbankSoldier(Spider):
    name = 'CiticbankSoldier'
    print('================已运行%s==================' % name)

    async def parse(self, response):
        html = response.html
        if isinstance(html, str):
            html = html.encode('utf-8')
        html_lzma = lzma.compress(html)
        print(html_lzma)
        html_back = lzma.decompress(html_lzma)
        print(str(html_back, 'utf-8'))



def start():
    CiticbankExplorer.start(middleware=middleware)



if __name__ == '__main__':
    CiticbankExplorer.start()




from myspiders.ruia import HtmlField, AttrField, Item, Spider, Request
from myspiders.ruia.plugins.ua_random import middleware
from database.backends import MongoDatabase
from config import CONFIG
import time
from urllib.parse import quote, urljoin
import os
from myspiders.tools.tools_spider import suffix_check


lua_init = '''
function main(splash, args)
    local myheaders = {}
    myheaders['User-Agent']='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'
    splash.images_enabled=false
    assert(splash:go{'%s', headers=myheaders})
    assert(splash:wait(2))
    return {
        html = splash:html(),
        cookies = splash:get_cookies(),
    }
end'''


class JsbchinaOneItem(Item):
    target_item = HtmlField(css_select='#myTab0_Content2 ul a')  # etree的cssselect会匹配所有符合条件的a
    link = AttrField(css_select='a', attr='href')

    async def clean_link(self, one):
        if one.startswith('//'):
            one.replace('//', '/')
            print('有link存在双斜杠，现修正为：%s' % one)
        link = urljoin('http://www.jsbchina.cn', one)
        return link


class JsbchinaTwoItem(Item):
    link = AttrField(css_select='#myTab0_Content0 a', attr='href')

    async def clean_link(self, one):
        if one.startswith('//'):
            one.replace('//', '/')
            print('有link存在双斜杠，现修正为：%s' % one)
        link = urljoin('http://www.jsbchina.cn', one)
        return link


class JsbchinaExplorer(Spider):
    name = 'JsbchinaExplorer'
    bank_name = '江苏银行'
    page_count = CONFIG.CRAWL_PAGE_COUNT
    # page_count = 171

    html_type = CONFIG.HTML_TYPE['manual']
    splash_url = 'http://localhost:8050/execute?lua_source='
    init_url = 'http://www.jsbchina.cn/CN/gryw/ptzlc/lc/grlccpxx/index.html?flag=2'
    next_urls = ['http://www.jsbchina.cn/CN/gryw/ptzlc/lc/grlccpxx/index_%s.html?flag=2' % num for num in range(2, int(page_count) + 1)]
    next_urls.insert(0, init_url)

    mongo = MongoDatabase()
    mongo_db = mongo.db()
    collection_list = mongo_db[bank_name]
    collection_url = mongo_db['MANUAL_URL']
    collection_ukey = mongo_db['BANK_UKEY']
    mongo.do_insert_one(collection_ukey, {'_id': bank_name}, {'_id': bank_name, 'ukey': 'bank_name=code'})
    print('================已运行%s==================' % name)

    def start_manual(self):
        for one in self.next_urls:
            lua = lua_init % one
            url = self.splash_url + quote(lua)
            yield Request(url=url, callback=self.parse)

    async def parse(self, response):
        jsondata = await response.json()
        html = jsondata['html']

        list_link = []
        async for item in JsbchinaOneItem.get_items(html=html):
            data = item.results
            lua = lua_init % data['link']
            url = self.splash_url + quote(lua)
            list_link.append(url)

        async for resp in self.multiple_request(list_link):
            jsondata = await resp.json()
            html = jsondata['html']
            item = await JsbchinaTwoItem.get_item(html=html)
            yield item

    async def process_item(self, item: Item):
        print('传入进来的item是：%s' % item)
        url = item.results['link']

        file_name = os.path.split(url)[-1]
        code = file_name.split('.')[0]

        suffix = os.path.splitext(url)[-1]
        if suffix in suffix_check:
            ukey = self.bank_name + '=' + code
            if url:
                data_url = {
                    '_id': ukey,
                    'url': url,
                    'html_type': self.html_type,
                    'create_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'crawl_status': 'undo'
                }
                self.mongo.do_insert_one(self.collection_url, {'_id': ukey}, data_url)
        else:
            print('产品说明书 特殊链接，请注意：%s' % url)



