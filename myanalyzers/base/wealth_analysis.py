# 如果以后还要分析更多的元素，则可以以WealthAnalysis为父类进行扩展。
from constants import BankDict


class WealthAnalysis(object):

    def __init__(
            self,
            wkeyhash: str = None,
            wkey: str = None,

            bank_name: str = None,
            bank_type: str = None,

            name: str = None,
            code: str = None,
            code_register: str = None,

            rate_max: str = None,
            rate_min: str = None,

            currency: str = None,
            risk: str = None,
            term: str = None,
            term_type: str = None,

            amount_size_max: str = None,
            amount_buy_min: str = None,
            amount_per_buy: str = None,

            date_open: str = None,
            date_close: str = None,
            date_start: str = None,
            date_end: str = None,

            create_time: str = None,
    ):
        self._wkeyhash = wkeyhash                           # 存储索引 纯数字
        self._wkey = wkey                                   # 存储索引 文字

        self._bank_name = bank_name                         # 仅作显示用
        self._bank_type = bank_type                         # 数据分类用  国有银行、股份银行、城商银行、农商银行、理财公司、外资银行、其他机构

        self._name = name                                   # 仅作显示用
        self._code = code                                   # 仅作显示用
        self._code_register = code_register                 # 仅作显示用

        self._rate_max = rate_max                           # 数据计算
        self._rate_min = rate_min                           # 数据计算

        self._currency = currency                           # 数据分类用
        self._risk = risk                                   # 数据分类用 0，1，2，3，4，5
        self._term = term
        self._term_type = term_type                         # 数据区间分类用 0-7, 7-30, 30-90, 90-180, 180-360, 360-1080, 1080以上

        self._amount_size_max = amount_size_max             # 数据规模计算
        self._amount_buy_min = amount_buy_min               # 数据分类用
        self._amount_per_buy = amount_per_buy               # 仅作显示用

        self._date_open = date_open                         # 数据区间计算
        self._date_close = date_close                       # 数据区间计算
        self._date_start = date_start                       # 数据区间计算
        self._date_end = date_end                           # 数据区间计算    如果有值的话

        self._create_time = create_time                     # 新增数据计算    每周日执行，划分范围为一个星期，上周日，至本周六

        self._list_bank_type = BankDict.list_bank_type
        self._list_term_type = BankDict.list_term_type

    def __repr__(self):
        return f"[{self._bank_name}] WealthAnalysis wkeyhash: {self._wkeyhash}, " \
               f"name: {self._name}, code: {self._code}, code_register: {self._code_register}, " \
               f"rate_max: {self._rate_max}, rate_min: {self._rate_min}, " \
               f"currency: {self._currency}, risk: {self._risk}, term: {self._term}, " \
               f"amount_size_max: {self._amount_size_max}, amount_buy_min: {self._amount_buy_min}, amount_per_buy: {self._amount_per_buy}, " \
               f"date_open: {self._date_open}, date_close: {self._date_close}, date_start: {self._date_start}, date_end: {self._date_end}"

    def do_dict_data(self):
        elements = [one for one in dir(self) if not (one.startswith('__') or one.startswith('_') or one.startswith('do_'))]
        data = {}
        for name in elements:
            value = getattr(self, name, None)
            data[name] = str(value) if value else ''
        data['_id'] = self.wkeyhash                         # 为了保存进mongodb，增加_id，并设置其值为wkeyhash
        return data

    @classmethod
    def do_load_data(cls, data: dict):
        wealth_analysis = cls()
        elements = [one for one in dir(wealth_analysis) if not (one.startswith('__') or one.startswith('_') or one.startswith('do_'))]
        wealth_analysis.wkeyhash = data['_id']
        for key, value in data.items():
            if key in elements:
                setattr(wealth_analysis, key, value)
        # 设置bank_type的值
        for key, value in wealth_analysis._list_bank_type.items():
            if key == wealth_analysis.bank_name:
                wealth_analysis.bank_type = value
        # 设置term_type的值
        if wealth_analysis.term:
            for key, value in wealth_analysis._list_term_type.items():
                term = int(wealth_analysis.term)
                if term <= key:
                    wealth_analysis.term_type = value
                    break
        return wealth_analysis

    @property
    def wkeyhash(self):
        return self._wkeyhash

    @wkeyhash.setter
    def wkeyhash(self, value):
        self._wkeyhash = value

    @property
    def wkey(self):
        return self._wkey

    @wkey.setter
    def wkey(self, value):
        self._wkey = value

    @property
    def bank_name(self):
        return self._bank_name

    @bank_name.setter
    def bank_name(self, value):
        self._bank_name = value

    @property
    def bank_type(self):
        return self._bank_type

    @bank_type.setter
    def bank_type(self, value):
        self._bank_type = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

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
    def term(self):
        return self._term

    @term.setter
    def term(self, value):
        self._term = value

    @property
    def term_type(self):
        return self._term_type

    @term_type.setter
    def term_type(self, value):
        self._term_type = value

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
    def amount_per_buy(self):
        return self._amount_per_buy

    @amount_per_buy.setter
    def amount_per_buy(self, value):
        self._amount_per_buy = value

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
    def create_time(self):
        return self._create_time

    @create_time.setter
    def create_time(self, value):
        self._create_time = value


class WealthAnalysisOne(WealthAnalysis):

    def __init__(
            self,
            wkeyhash: str = None,
            wkey: str = None,
            bank_name: str = None,
            name: str = None,
            code: str = None,
            code_register: str = None,

            promise_type: str = None,
            rate_type: str = None,

            rate_max: str = None,
            rate_min: str = None,

            currency: str = None,
            risk: str = None,
            term: str = None,
            term_type: str = None,

            amount_size_max: str = None,
            amount_buy_min: str = None,
            amount_per_buy: str = None,

            date_open: str = None,
            date_close: str = None,
            date_start: str = None,
            date_end: str = None,

            create_time: str = None,
    ):
        super(WealthAnalysisOne, self).__init__(
            wkeyhash=wkeyhash,
            wkey=wkey,
            bank_name=bank_name,
            name=name,
            code=code,
            code_register=code_register,
            rate_max=rate_max,
            rate_min=rate_min,
            currency=currency,
            risk=risk,
            term=term,
            term_type=term_type,
            amount_size_max=amount_size_max,
            amount_buy_min=amount_buy_min,
            amount_per_buy=amount_per_buy,
            date_open=date_open,
            date_close=date_close,
            date_start=date_start,
            date_end=date_end,
            create_time=create_time,
        )
        self._promise_type = promise_type,  # 数据分类用  保本、非保本
        self._rate_type = rate_type,        # 数据分类用  净值型、预期收益型

    def __repr__(self):
        return f"[{self._bank_name}] WealthAnalysisOne wkeyhash: {self._wkeyhash}, " \
               f"name: {self._name}, code: {self._code}, code_register: {self._code_register}, " \
               f"promise_type: {self._promise_type}, " \
               f"rate_type: {self._rate_type}, rate_max: {self._rate_max}, rate_min: {self._rate_min}, " \
               f"currency: {self._currency}, risk: {self._risk}, term: {self._term}, " \
               f"amount_size_max: {self._amount_size_max}, amount_buy_min: {self._amount_buy_min}, amount_per_buy: {self._amount_per_buy}, " \
               f"date_open: {self._date_open}, date_close: {self._date_close}, date_start: {self._date_start}, date_end: {self._date_end}"

    @property
    def rate_type(self):
        return self._rate_type

    @rate_type.setter
    def rate_type(self, value):
        self._rate_type = value

    @property
    def promise_type(self):
        return self._promise_type

    @promise_type.setter
    def promise_type(self, value):
        self._promise_type = value


class WealthAnalysisTwo(WealthAnalysis):

    def __init__(
            self,
            wkeyhash: str = None,
            wkey: str = None,
            bank_name: str = None,
            name: str = None,
            code: str = None,
            code_register: str = None,

            redeem_type: str = None,
            fixed_type: str = None,
            promise_type: str = None,
            raise_type: str = None,
            rate_type: str = None,

            rate_max: str = None,
            rate_min: str = None,

            currency: str = None,
            risk: str = None,
            term: str = None,
            term_type: str = None,

            amount_size_max: str = None,
            amount_buy_min: str = None,
            amount_per_buy: str = None,

            date_open: str = None,
            date_close: str = None,
            date_start: str = None,
            date_end: str = None,

            create_time: str = None,
    ):
        super(WealthAnalysisTwo, self).__init__(
            wkeyhash=wkeyhash,
            wkey=wkey,
            bank_name=bank_name,
            name=name,
            code=code,
            code_register=code_register,
            rate_max=rate_max,
            rate_min=rate_min,
            currency=currency,
            risk=risk,
            term=term,
            term_type=term_type,
            amount_size_max=amount_size_max,
            amount_buy_min=amount_buy_min,
            amount_per_buy=amount_per_buy,
            date_open=date_open,
            date_close=date_close,
            date_start=date_start,
            date_end=date_end,
            create_time=create_time,
        )
        self._redeem_type = redeem_type,    # 数据分类用  封闭式、开放式       数据抓取准确度不高 没太大意义
        self._fixed_type = fixed_type,      # 数据分类用  固定收益、浮动收益                     没太大意义
        self._promise_type = promise_type,  # 数据分类用  保本、非保本
        self._raise_type = raise_type,      # 数据分类用  公募、私募                            没太大意义
        self._rate_type = rate_type,        # 数据分类用  净值型、预期收益型

    def __repr__(self):
        return f"[{self._bank_name}] WealthAnalysisTwo wkeyhash: {self._wkeyhash}, " \
               f"name: {self._name}, code: {self._code}, code_register: {self._code_register}, " \
               f"raise_type: {self._raise_type}, fixed_type: {self._fixed_type}, promise_type: {self._promise_type}, redeem_type: {self._redeem_type}, " \
               f"rate_type: {self._rate_type}, rate_max: {self._rate_max}, rate_min: {self._rate_min}, " \
               f"currency: {self._currency}, risk: {self._risk}, term: {self._term}, " \
               f"amount_size_max: {self._amount_size_max}, amount_buy_min: {self._amount_buy_min}, amount_per_buy: {self._amount_per_buy}, " \
               f"date_open: {self._date_open}, date_close: {self._date_close}, date_start: {self._date_start}, date_end: {self._date_end}"

    @property
    def rate_type(self):
        return self._rate_type

    @rate_type.setter
    def rate_type(self, value):
        self._rate_type = value

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
