# ukey
# wkey
# wkeyhash

# name:                     产品名称
# code:                     产品代码
# code_register:            登记编码
# bank_name                 银行名称
# bank_level                银行层级（国有银行、股份银行、城商银行、农商银行）
# currency:                 币种
# risk:                     风险等级

# rate_max:                 最高利率 或 净值参考     %转换为小数表述
# rate_min:                 最低利率 或 净值参考     %转换为小数表述
# rate_type:                净值型、预期收益型

# redeem_type:              封闭式、开放式，即赎回规则

# fixed_type:               固定收益、浮动收益       如rate_type为净值型，则默认 浮动收益
# promise_type:             保本、非保本            如rate_type为净值型，则默认 非保本
# raise_type:               公募、私募              如未找到私募，则默认为公募

# date_open:                发行起始日期
# date_close:               发行到期日期
# date_start:               产品起息日期
# date_end:                 产品结束日期
# term:                     期限                          单位（天）
# term_looped:              投资周期顺延 自动再投资

# amount_size_min:          产品规模最小    单位(元)
# amount_size_max:          产品规模最大    单位(元)
# amount_buy_min:           起购金额        单位(元)
# amount_buy_max:           购买上限        单位(元)
# amount_per_buy            每份购买金额    单位(元)

# custodian:                托管机构
# fee_types:                托管费、申购费、赎回费、管理费、销售费等
# fee_rate:                 费用数量  加总        %转换为小数表述

# sale_areas:               销售区域  全国、上海、北京、江苏等
# sale_ways:                购买方式  手机、柜面等
# sale_agents:              代销机构

# invest_on:                产品投资范围
# loan_rule:                融资服务， 如理财质押贷款

# test为一个实例化的类
# 获取类中全部的自定义方法，不包含@property和@setter注释的方法, 注意：callable()方法里面的参数是类方法，而不是str
# b = set(filter(lambda m: callable(getattr(test, m)) and not m.startswith('__'), dir(test)))

# 获取类中全部的属性和方法，不包含'__'、'_', 'pattern'开头的方法
# b = [a for a in dir(test) if not (a.startswith('__') or a.startswith('_') or a.startswith('pattern'))]

import time


class Wealth(object):

    def __init__(
        self,
        ukey: str,
        bank_level: str,
        name: str = None,
        code: str = None,
        code_register: str = None,
        currency: str = None,
        risk: int = None,
        rate_max: float = None,
        rate_min: float = None,
        rate_type: str = None,
        redeem_type: str = None,
        fixed_type: str = None,
        promise_type: str = None,
        raise_type: str = None,
        date_open: str = None,
        date_close: str = None,
        date_start: str = None,
        date_end: str = None,
        term: int = None,
        term_looped: str = None,
        amount_size_min: int = None,
        amount_size_max: int = None,
        amount_buy_min: int = None,
        amount_buy_max: int = None,
        amount_per_buy: int = None,
        custodian: str = None,
        fee_types: dict = None,
        fee_rate: float = None,
        sale_areas: list = None,
        sale_ways: list = None,
        sale_agents: list = None,
        invest_on: str = None,
        loan_rule: str = None,
    ):
        self._ukey = ukey
        self._bank_level = bank_level
        self._wkey = None              # 唯一键
        self._wkeyhash = None          # 序列化唯一键使用
        ukey_list = ukey.split('=')
        self._bank_name = ukey_list[-2] if len(ukey_list) > 1 else None
        self._name = name
        self._code = code
        self._code_register = code_register
        self._currency = currency
        self._risk = risk
        self._rate_max = rate_max
        self._rate_min = rate_min
        self._rate_type = rate_type
        self._redeem_type = redeem_type
        self._fixed_type = fixed_type
        self._promise_type = promise_type
        self._raise_type = raise_type
        self._date_open = date_open
        self._date_close = date_close
        self._date_start = date_start
        self._date_end = date_end
        self._term = term
        self._term_looped = term_looped
        self._amount_size_min = amount_size_min
        self._amount_size_max = amount_size_max
        self._amount_buy_min = amount_buy_min
        self._amount_buy_max = amount_buy_max
        self._amount_per_buy = amount_per_buy
        self._custodian = custodian
        self._fee_types = fee_types
        self._fee_rate = fee_rate
        self._sale_areas = sale_areas
        self._sale_ways = sale_ways
        self._sale_agents = sale_agents
        self._invest_on = invest_on
        self._loan_rule = loan_rule

    def __repr__(self):
        return f"[{self._bank_name}] Wealth wkeyhash: {self._wkeyhash}, " \
               f"name: {self._name}, bank_level: {self._bank_level}, code: {self._code}, code_register: {self._code_register}, currency: {self._currency}, risk: {self._risk}, " \
               f"rate_type: {self._rate_type}, rate_max: {self._rate_max}, rate_min: {self._rate_min}, " \
               f"raise_type: {self._raise_type}, fixed_type: {self._fixed_type}, promise_type: {self._promise_type}, " \
               f"redeem_type: {self._redeem_type}, " \
               f"date_open: {self._date_open}, date_close: {self._date_close}, date_start: {self._date_start}, date_end: {self._date_end}, term: {self._term}, term_looped: {self._term_looped}" \
               f"amount_size_max: {self._amount_size_max}, amount_size_min: {self._amount_size_min}, amount_buy_min: {self._amount_buy_min}, " \
               f"amount_buy_max: {self._amount_buy_max}, amount_per_buy: {self._amount_per_buy}, " \
               f"fee_types: {self._fee_types}, fee_rate: {self._fee_rate}, custodian: {self._custodian}, " \
               f"sale_areas: {self._sale_areas}, sale_ways: {self._sale_ways}, sale_agents: {self._sale_agents}, " \
               f"loan_rule: {self._loan_rule}, invest_on: {self._invest_on}]"

    def do_dict_data(self):
        elements = [one for one in dir(self) if not (one.startswith('__') or one.startswith('_') or one.startswith('do_'))]
        data = {}
        for name in elements:
            value = getattr(self, name, None)
            data[name] = value
        # 为了保存进mongodb，增加_id，并设置其值为wkeyhash, 并添加保存时间
        data['_id'] = str(self.wkeyhash)
        data.pop('wkeyhash')
        data['create_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        return data


    @property
    def ukey(self):
        return self._ukey

    @ukey.setter
    def ukey(self, value):
        self._ukey = value

    @property
    def bank_level(self):
        return self._bank_level

    @bank_level.setter
    def bank_level(self, value):
        self._bank_level = value

    @property
    def wkey(self):
        return self._wkey

    @wkey.setter
    def wkey(self, value):
        self._wkey = value

    @property
    def wkeyhash(self):
        return self._wkeyhash

    @wkeyhash.setter
    def wkeyhash(self, value):
        self._wkeyhash = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def bank_name(self):
        return self._bank_name

    @bank_name.setter
    def bank_name(self, value):
        self._bank_name = value

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, value):
        self._code = value

    @property
    def code_register(self):
        return self._code_register

    @code_register.setter
    def code_register(self, value):
        self._code_register = value

    @property
    def raise_type(self):
        return self._raise_type

    @raise_type.setter
    def raise_type(self, value):
        self._raise_type = value

    @property
    def redeem_type(self):
        return self._redeem_type

    @redeem_type.setter
    def redeem_type(self, value):
        self._redeem_type = value

    @property
    def fixed_type(self):
        return self._fixed_type

    @fixed_type.setter
    def fixed_type(self, value):
        self._fixed_type = value

    @property
    def promise_type(self):
        return self._promise_type

    @promise_type.setter
    def promise_type(self, value):
        self._promise_type = value

    @property
    def invest_on(self):
        return self._invest_on

    @invest_on.setter
    def invest_on(self, value):
        self._invest_on = value

    @property
    def currency(self):
        return self._currency

    @currency.setter
    def currency(self, value):
        self._currency = value

    @property
    def risk(self):
        return self._risk

    @risk.setter
    def risk(self, value):
        self._risk = value

    @property
    def date_open(self):
        return self._date_open

    @date_open.setter
    def date_open(self, value):
        self._date_open = value

    @property
    def date_close(self):
        return self._date_close

    @date_close.setter
    def date_close(self, value):
        self._date_close = value

    @property
    def date_start(self):
        return self._date_start

    @date_start.setter
    def date_start(self, value):
        self._date_start = value

    @property
    def date_end(self):
        return self._date_end

    @date_end.setter
    def date_end(self, value):
        self._date_end = value

    @property
    def term(self):
        return self._term

    @term.setter
    def term(self, value):
        self._term = value

    @property
    def term_looped(self):
        return self._term_looped

    @term_looped.setter
    def term_looped(self, value):
        self._term_looped = value

    @property
    def rate_max(self):
        return self._rate_max

    @rate_max.setter
    def rate_max(self, value):
        self._rate_max = value

    @property
    def rate_min(self):
        return self._rate_min

    @rate_min.setter
    def rate_min(self, value):
        self._rate_min = value

    @property
    def rate_type(self):
        return self._rate_type

    @rate_type.setter
    def rate_type(self, value):
        self._rate_type = value

    @property
    def amount_size_min(self):
        return self._amount_size_min

    @amount_size_min.setter
    def amount_size_min(self, value):
        self._amount_size_min = value

    @property
    def amount_size_max(self):
        return self._amount_size_max

    @amount_size_max.setter
    def amount_size_max(self, value):
        self._amount_size_max = value

    @property
    def amount_buy_min(self):
        return self._amount_buy_min

    @amount_buy_min.setter
    def amount_buy_min(self, value):
        self._amount_buy_min = value

    @property
    def amount_buy_max(self):
        return self._amount_buy_max

    @amount_buy_max.setter
    def amount_buy_max(self, value):
        self._amount_buy_max = value

    @property
    def amount_per_buy(self):
        return self._amount_per_buy

    @amount_per_buy.setter
    def amount_per_buy(self, value):
        self._amount_per_buy = value

    @property
    def custodian(self):
        return self._custodian

    @custodian.setter
    def custodian(self, value):
        self._custodian = value

    @property
    def fee_types(self):
        return self._fee_types

    @fee_types.setter
    def fee_types(self, value):
        self._fee_types = value

    @property
    def fee_rate(self):
        return self._fee_rate

    @fee_rate.setter
    def fee_rate(self, value):
        self._fee_rate = value

    @property
    def sale_areas(self):
        return self._sale_areas

    @sale_areas.setter
    def sale_areas(self, value):
        self._sale_areas = value

    @property
    def sale_ways(self):
        return self._sale_ways

    @sale_ways.setter
    def sale_ways(self, value):
        self._sale_ways = value

    @property
    def sale_agents(self):
        return self._sale_agents

    @sale_agents.setter
    def sale_agents(self, value):
        self._sale_agents = value

    @property
    def loan_rule(self):
        return self._loan_rule

    @loan_rule.setter
    def loan_rule(self, value):
        self._loan_rule = value


