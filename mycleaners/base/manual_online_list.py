# 用来将Mongo数据库中爬取的各家银行的理财列表数据，补充合并至前面加工好的wealth当中去
from config.log import Logger
from config import CONFIG
import os
from mycleaners.base.wealth import Wealth
from database.backends import MongoDatabase
import re
from utils.nlp_util import transfer_to_yuan, percent_to_num, date_to_standard
from constants import BankDict


class ManualOnlineList(object):
    log_path = os.path.join(CONFIG.LOG_DIR, 'ManualOnlineList.log')
    log = Logger(log_path, level='warning').logger

    # 如果想要检查某个label, 首先要看看mongo数据库中该银行的collection中的标签，在labels_check中有没有，
    # 如果labels_check中，没有则在ManualOnlineList的子类的labels_check_config中，需要添加进去，
    # ManualOnlineList的_start()方法将按照labels_check和银行的collection中的标签的交集，遍历，执行extract_方法。
    labels_check = {
        'raise_period',
        'invest_period',
        'product_type',
        'amount_size',
        'name',
        # 'code',
        'code_register',
        'currency',
        'risk',
        'rate_max',
        'rate_min',
        'rate_type',
        'redeem_type',
        'fixed_type',
        'promise_type',
        'raise_type',
        'date_open',
        'date_close',
        'date_start',
        'date_end',
        'term',
        'term_looped',
        'amount_size_min',
        'amount_size_max',
        'amount_buy_min',
        'amount_buy_max',
        'amount_per_buy',
        'custodian',
        'fee_types',
        'fee_rate',
        'sale_areas',
        'sale_ways',
        'sale_agents',
        'invest_on',
        'loan_rule',
    }

    db = MongoDatabase().db()
    list_risk = BankDict.list_risk
    list_currency = BankDict.list_currency

    pattern_rate = re.compile(r'[0-9]+(\.[0-9]+)*[%％]')
    pattern_term = re.compile(r'([0-9，,]+)([天日月年])')
    pattern_rate_type = re.compile(r'业绩比较基准|业绩基准|预期收益率|实现年化收益|预期理财收益率|预期年化收益率|预期到期利率|净值型|结构性存款')


    def __init__(self, bank_name: str, dict_wealth: dict):
        self.bank_name = bank_name
        self.dict_wealth = dict_wealth
        self.collection_list = self.db[self.bank_name]
        config = getattr(self, 'labels_check_config', None)
        if config:
            if not isinstance(config, set):
                raise ValueError("labels_check_config must be type of set")
            self.labels_check.update(config)

    @classmethod
    def start(cls, bank_name: str, dict_wealth: dict):
        dict_wealth_in = cls(bank_name, dict_wealth)
        dict_wealth_out = dict_wealth_in._start()
        return dict_wealth_out

    def _start(self):
        dict_wealth_back = {}
        for code, wealth in self.dict_wealth.items():
            db_wealth = self.collection_list.find_one({'_id': code})
            if db_wealth:
                wealth = self.makeup_wealth(wealth, db_wealth)
                wealth = self.final_makeup_wealth(wealth)
            dict_wealth_back[code] = wealth
        return dict_wealth_back

    def final_makeup_wealth(self, wealth: Wealth):
        if not wealth.redeem_type:
            if wealth.term:
                wealth.redeem_type = '封闭型'
        return wealth

    def makeup_wealth(self, wealth: Wealth, db_wealth: dict):
        db_keys = db_wealth.keys()
        elements_check = set(db_keys).intersection(self.labels_check)
        for one in elements_check:
            extract_method = getattr(self, 'extract_' + one, None)
            if extract_method is not None and callable(extract_method):
                value = db_wealth[one]
                if value:
                    value = re.sub(r'\s+', '', value)
                    wealth = extract_method(str(value), wealth)
            else:
                self.log.error('没有找到相应的方法：extract_%s方法' % one)
        return wealth


    def extract_raise_period(self, value: str, wealth: Wealth):
        if not wealth.date_open or not wealth.date_close:
            list_date = date_to_standard(value)
            if list_date:
                list_date.sort()
                wealth.date_open = list_date[0]
                wealth.date_close = list_date[-1]
        return wealth

    def extract_invest_period(self, value: str, wealth: Wealth):
        if not wealth.date_start or not wealth.date_end:
            wealth.date_start = value
            wealth.date_end = value
        return wealth

    def extract_product_type(self, value: str, wealth: Wealth):
        return wealth

    def extract_amount_size(self, value: str, wealth: Wealth):
        return wealth


    def extract_name(self, value: str, wealth: Wealth):
        if not wealth.name:
            wealth.name = value
        return wealth

    def extract_code(self, value: str, wealth: Wealth):
        if not wealth.code:
            wealth.code = value
        return wealth

    def extract_code_register(self, value: str, wealth: Wealth):
        if not wealth.code_register:
            wealth.code_register = value
        return wealth

    def extract_currency(self, value: str, wealth: Wealth):
        if not wealth.currency:
            wealth.currency = value
        return wealth

    def extract_risk(self, value: str, wealth: Wealth):
        if not wealth.risk:
            result = re.search(r'[012345]', value)
            if result:
                wealth.risk = int(result.group(0))
            else:
                for key in self.list_risk.keys():
                    if key == value:
                        wealth.risk = self.list_risk[key]
                        break
        return wealth

    def extract_rate_max(self, value: str, wealth: Wealth):
        if not wealth.rate_max:
            results = self.pattern_rate.finditer(value)
            list_rate = []
            for one in results:
                rate_text = one.group(0)
                if rate_text:
                    rate_num = percent_to_num(rate_text)
                    list_rate.append(rate_num)
            if list_rate:
                list_rate.sort()
                wealth.rate_max = list_rate[-1]
        return wealth

    def extract_rate_min(self, value: str, wealth: Wealth):
        if not wealth.rate_min:
            results = self.pattern_rate.finditer(value)
            list_rate = []
            for one in results:
                rate_text = one.group(0)
                if rate_text:
                    rate_num = percent_to_num(rate_text)
                    list_rate.append(rate_num)
            if list_rate:
                list_rate.sort()
                wealth.rate_min = list_rate[0]
        return wealth

    def extract_rate_type(self, value: str, wealth: Wealth):
        if not wealth.rate_type:
            result = self.pattern_rate_type.search(value)
            if result:
                rate_type = result.group(0)
                if rate_type == '比较业绩基准' or rate_type == '业绩比较基准' or rate_type == '业绩基准' or rate_type == '净值型':
                    wealth.rate_type = '净值型'
                elif rate_type == '预期理财收益率' or rate_type == '预期年化收益率' or rate_type == '预期到期利率' or rate_type == '年化收益率' or rate_type == '预期收益率' or rate_type == '实现年化收益':
                    wealth.rate_type = '预期收益型'
                elif rate_type == '结构性存款':
                    wealth.rate_type = '预期收益型'
        return wealth

    def extract_redeem_type(self, value: str, wealth: Wealth):
        if not wealth.redeem_type:
            wealth.redeem_type = value
        return wealth

    def extract_fixed_type(self, value: str, wealth: Wealth):
        if not wealth.fixed_type:
            wealth.fixed_type = value
        return wealth

    def extract_promise_type(self, value: str, wealth: Wealth):
        if not wealth.promise_type:
            wealth.promise_type = value
        return wealth

    def extract_raise_type(self, value: str, wealth: Wealth):
        if not wealth.raise_type:
            wealth.raise_type = value
        return wealth

    def extract_date_open(self, value: str, wealth: Wealth):
        if not wealth.date_open:
            wealth.date_open = value
        return wealth

    def extract_date_close(self, value: str, wealth: Wealth):
        if not wealth.date_close:
            wealth.date_close = value
        return wealth

    def extract_date_start(self, value: str, wealth: Wealth):
        if not wealth.date_start:
            wealth.date_start = value
        return wealth

    def extract_date_end(self, value: str, wealth: Wealth):
        if not wealth.date_end:
            wealth.date_end = value
        return wealth

    def extract_term(self, value: str, wealth: Wealth):
        if not wealth.term:
            result = self.pattern_term.search(value)
            if result:
                num = result.group(1)
                num = num.replace(',', '')
                num = num.replace('，', '')
                num = int(num)
                unit = result.group(2)
                if unit == '月':
                    num = num * 30
                elif unit == '年':
                    num = num * 365
                if num < 7301:
                    wealth.term = num
        return wealth

    def extract_term_looped(self, value: str, wealth: Wealth):
        if not wealth.term_looped:
            if '投资周期顺延' in value or '自动再投资' in value or '无固定期限' in value:
                wealth.term_looped = 'YES'
        return wealth

    def extract_amount_size_min(self, value: str, wealth: Wealth):
        if not wealth.amount_size_min:
            if value and value != '-':
                num = transfer_to_yuan(value)
                wealth.amount_size_min = num
        return wealth

    def extract_amount_size_max(self, value: str, wealth: Wealth):
        if not wealth.amount_size_max:
            if value and value != '-':
                num = transfer_to_yuan(value)
                wealth.amount_size_max = num
        return wealth

    def extract_amount_buy_min(self, value: str, wealth: Wealth):
        if not wealth.amount_buy_min:
            if value and value != '-':
                num = transfer_to_yuan(value)
                wealth.amount_buy_min = num
        return wealth

    def extract_amount_buy_max(self, value: str, wealth: Wealth):
        if not wealth.amount_buy_max:
            if value and value != '-':
                num = transfer_to_yuan(value)
                wealth.amount_buy_max = num
        return wealth

    def extract_amount_per_buy(self, value: str, wealth: Wealth):
        if not wealth.amount_per_buy:
            if value and value != '-':
                num = transfer_to_yuan(value)
                wealth.amount_per_buy = num
        return wealth

    def extract_custodian(self, value: str, wealth: Wealth):
        if not wealth.custodian:
            wealth.custodian = value
        return wealth

    def extract_fee_types(self, value: str, wealth: Wealth):
        if not wealth.fee_types:
            wealth.fee_types = value
        return wealth

    def extract_fee_rate(self, value: str, wealth: Wealth):
        if not wealth.fee_rate:
            if value and value != '-':
                results = self.pattern_rate.finditer(value)
                rate = 0.0
                for one in results:
                    rate_text = one.group(0)
                    rate_num = percent_to_num(rate_text)
                    rate += rate_num
                if rate > 0:
                    wealth.fee_rate = rate
        return wealth

    def extract_sale_areas(self, value: str, wealth: Wealth):
        if not wealth.sale_areas:
            wealth.sale_areas = value
        return wealth

    def extract_sale_ways(self, value: str, wealth: Wealth):
        if not wealth.sale_ways:
            wealth.sale_ways = value
        return wealth

    def extract_sale_agents(self, value: str, wealth: Wealth):
        if not wealth.sale_agents:
            wealth.sale_agents = value
        return wealth

    def extract_invest_on(self, value: str, wealth: Wealth):
        if not wealth.invest_on:
            wealth.invest_on = value
        return wealth

    def extract_loan_rule(self, value: str, wealth: Wealth):
        if not wealth.loan_rule:
            wealth.loan_rule = value
        return wealth
