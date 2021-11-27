from myspiders.ruia import JsonField, Item, Spider
from myspiders.ruia.plugins.ua_random import middleware
from utils.string_util import random_digits
from config import CONFIG
from config import DocumentUrl
from myspiders.tools.tools_request import get_random_user_agent
from myspiders.ruia.plugins.ua_random import middleware
from constants.bank_dict import BankDict


branch_list = [
    {'branchId': '703220', 'city': '南京'},
    {'branchId': '703260', 'city': '合肥'},
    {'branchId': '703400', 'city': '福州'},
    {'branchId': '711020', 'city': '卡中心'},
    {'branchId': '711100', 'city': '北京'},
    {'branchId': '721100', 'city': '大连'},
    {'branchId': '722100', 'city': '沈阳'},
    {'branchId': '723000', 'city': '天津'},
    {'branchId': '724100', 'city': '石家庄'},
    {'branchId': '725100', 'city': '西安'},
    {'branchId': '726100', 'city': '太原'},
    {'branchId': '727100', 'city': '呼和浩特'},
    {'branchId': '728100', 'city': '南昌'},
    {'branchId': '729100', 'city': '南宁'},
    {'branchId': '730100', 'city': '昆明'},
    {'branchId': '731109', 'city': '上海'},
    {'branchId': '732300', 'city': '苏州'},
    {'branchId': '733600', 'city': '宁波'},
    {'branchId': '733990', 'city': '杭州'},
    {'branchId': '734200', 'city': '厦门'},
    {'branchId': '737001', 'city': '青岛'},
    {'branchId': '737200', 'city': '济南'},
    {'branchId': '738100', 'city': '武汉'},
    {'branchId': '739109', 'city': '郑州'},
    {'branchId': '740110', 'city': '长沙'},
    {'branchId': '741100', 'city': '成都'},
    {'branchId': '742109', 'city': '重庆'},
    {'branchId': '744000', 'city': '广州'},
    {'branchId': '744100', 'city': '深圳'},
    {'branchId': '744809', 'city': '东莞'},
    {'branchId': '745100', 'city': '哈尔滨'},
    {'branchId': '746100', 'city': '兰州'},
    {'branchId': '747109', 'city': '贵阳'},
    {'branchId': '748100', 'city': '长春'},
    {'branchId': '750100', 'city': '乌鲁木齐'},
    {'branchId': '754000', 'city': '海口'},
    {'branchId': '758000', 'city': '银川'},
    {'branchId': '759000', 'city': '西宁'},
    {'branchId': '768100', 'city': '拉萨'}
]


def get_fetch_params(page_index: int, page_size: int):
    form_datas = [
        {
            'currType': '',                     # 币   种， 01：人民币， 02：美元， 03：英镑， 04：欧元， 05：港币， 06：其他
            'dayDeadline': '',                  # 产品期限， 00：无固定期限，01：30天以下，02：31天到90天，03：91天到180天，04：181天到365天，05：365天以上
            'riskLevel': '',                    # 风险等级， 00：无风险， 01：低风险， 02：较低风险， 03：中等风险， 04：较高风险， 05：高风险
            'firstAmt': '',                     # 购买起点， 01：0至5万， 02：5至10万， 03：10至20万， 04：20万以上
            'branchId': '701100',
            'prodState': '',                    # 产品状态， 01：可购买， 02：即将发售  04：不能购买
            'openAttr': '',                     # 开放性质， 01：开放式， 02：封闭式
            'breakEvenAttr': '',                # 保本性质， 01：保本， 02：不保本
            'endInterestDate': '',              # 产品到期日， 譬如20190910，代表2019年9月10日
            'finaQrycondi': '',                 # 根据输入的产品代码或名称进行模糊搜索
            'totuseAmt': '01',                  # 销售额度， 01：显示全部产品， 02：仅显示有剩余额度的产品
            'orderField': 'ipo_start_date',     # 排序标准， ppo_incomerate：预期年化收益率， ipo_start_date：募集期， risk_level：风险等级， prod_name：产品名称， day_prddeadline：产品期限， first_amt：购买起点
            'orderType': 'desc',                # 降序升序， desc:降序排列， asc:升序排列
            'currentPage': str(page_index),
            'pageSize': str(page_size),
            'tcstNo': '',
            'userId': '',
            'pwdControlFlag': '0',
            'responseFormat': 'JSON',
            'random': random_digits(4)
        }
    ]
    return form_datas


class CiticbankWorker(Spider):
    name = 'CiticbankWorker'
    bank_name = '中信银行'
    bank_domain = 'https://etrade.citicbank.com/'
    headers = {'Referer': 'https://etrade.citicbank.com/portalweb/html/finList.html'}

    print('================已运行%s==================' % name)
    manual_url_prefix = 'https://etrade.citicbank.com/portalweb/findoc/%s00.html'
    html_type = CONFIG.HTML_TYPE['manual']

    page_index = 1
    page_size = 50
    page_item_less = 10
    form_data = get_fetch_params(page_index, page_size)
    start_urls = ["https://etrade.citicbank.com/portalweb/fd/getFinaList.htm"]

    risk_transfer = BankDict.list_risk

    def save_list_manual_db(self, jsondata):
        insert_number = 0
        list_data = jsondata['content']['resultList']
        for one in list_data:
            data = {
                'referencable': '高',
                '_id': self.bank_name + '=' + one['prdNo'],
                'code': one['prdNo'],
                'name': one['prdName'],
                'risk': self.risk_transfer[one['riskLevel']],
                'amount_buy_min': one['firstAmt'],
                'date_open': one['ipoBeginDate'],
                'date_close': one['ipoEndDate'],
                'date_start': one['beginIntereastDate'],
                'date_end': one['endIntereastDate'],
                'currency': one['currType'],
                'term': one['dayDeadLine'],
                'rate_min': '',
                'rate_max': '',
            }

            amount_buy_min = data['amount_buy_min']
            if amount_buy_min and '万' in amount_buy_min:
                data['amount_buy_min'] = float(amount_buy_min.replace('万', '0000'))

            currency = data['currency']
            if int(currency) == 1:
                data['currency'] = '人民币'
            elif int(currency) == 14:
                data['currency'] = '美元'

            incomerate = one['incomerate']
            lastIncomeRate = one['lastIncomeRate']
            if incomerate and lastIncomeRate:
                if float(incomerate) > float(lastIncomeRate):
                    data['rate_min'] = float(incomerate)
                    data['rate_max'] = float(incomerate)
                    data['rate_type'] = '预期收益型'
                else:
                    data['rate_min'] = float(lastIncomeRate)
                    data['rate_max'] = float(lastIncomeRate)
                    data['rate_type'] = '净值型'
            elif incomerate and lastIncomeRate is None:
                data['rate_min'] = float(incomerate)
                data['rate_max'] = float(incomerate)
                data['rate_type'] = '预期收益型'
            elif lastIncomeRate and incomerate is None:
                data['rate_min'] = float(lastIncomeRate)
                data['rate_max'] = float(lastIncomeRate)
                data['rate_type'] = '净值型'

            manual_url = self.manual_url_prefix % data['code']
            manual = DocumentUrl(ukey=data['_id'], url=manual_url, html_type=self.html_type)
            manual_data = manual.do_dict_data()
            self.mongo.do_insert_one(self.collection_file, {'_id': data['_id']}, manual_data)

            back = self.mongo.do_insert_one(self.collection_list, {'_id': data['_id']}, data)
            if back:
                insert_number += 1
        return insert_number

    # 每次首先试探第一页，将page_size由默认的8，设置为50
    # 返回数据存入Mongo数据库，如果这50条全部都是新增，则继续爬取
    async def parse(self, response):
        jsondata = await response.json(content_type='text/html')
        insert_number = self.save_list_manual_db(jsondata)

        # 允许有4个数目的差别，仍旧可以再请求下一页
        if insert_number > self.page_size - self.page_item_less:
            self.page_index += 1
            form_data = get_fetch_params(self.page_index, self.page_size)[0]
            yield self.request(url=self.start_urls[0], form_data=form_data, callback=self.parse)


def start():
    # CiticbankWorker.start(middleware=middleware)
    pass
