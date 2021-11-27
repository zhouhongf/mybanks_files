# 本周新增理财数量，本周新增理财金额
# 其中：
# 收益类型分类：
# 保本类型分类：
# 风险等级分类：
# 期限分类：
# 规模分类：
# 起购金额分类：

# 最大利率 分析
# 最小利率 分析


class WealthCount(object):

    def __init__(
            self,
            ukeyhash: str = None,
            ukey: str = None,                       # 格式为 count_name=count_unit=timestamp
            count_unit: str = None,                 # 统计维度单位 数量num、金额amt
            count_name: str = None,                 # 统计对象的名字， 银行名字，或国有银行、股份银行、城商银行 等等
            create_time: str = None,                # create_time需要转换为timestamp
            total: int = None,
    ):
        self._ukeyhash = ukeyhash
        self._ukey = ukey
        self._count_unit = count_unit
        self._count_name = count_name
        self._create_time = create_time
        self._total = total

    def do_dict_data(self):
        elements = [one for one in dir(self) if not (one.startswith('__') or one.startswith('_') or one.startswith('do_'))]
        data = {}
        for name in elements:
            value = getattr(self, name, None)
            data[name] = str(value) if value else ''
        data['_id'] = self.ukeyhash                         # 为了保存进mongodb，增加_id，并设置其值为wkeyhash
        return data

    @classmethod
    def do_load_data(cls, data: dict):
        wealth_count = cls()
        elements = [one for one in dir(wealth_count) if not (one.startswith('__') or one.startswith('_') or one.startswith('do_'))]
        wealth_count.ukeyhash = data['_id']
        for key, value in data.items():
            if key in elements:
                setattr(wealth_count, key, value)
        return wealth_count

    @property
    def ukeyhash(self):
        return self._ukeyhash

    @ukeyhash.setter
    def ukeyhash(self, value):
        self._ukeyhash = value

    @property
    def ukey(self):
        return self._ukey

    @ukey.setter
    def ukey(self, value):
        self._ukey = value
        
    @property
    def count_unit(self):
        return self._count_unit

    @count_unit.setter
    def count_unit(self, value):
        self._count_unit = value
        
    @property
    def count_name(self):
        return self._count_name

    @count_name.setter
    def count_name(self, value):
        self._count_name = value
    
    @property
    def create_time(self):
        return self._create_time

    @create_time.setter
    def create_time(self, value):
        self._create_time = value
    
    @property
    def total(self):
        return self._total

    @total.setter
    def total(self, value):
        self._total = value


class WealthCountRateType(WealthCount):

    def __init__(
            self,
            ukeyhash: str = None,
            ukey: str = None,                       # 格式为 count_name=count_unit=timestamp

            count_unit: str = None,                 # 统计维度单位 数量、金额
            count_name: str = None,                 # 统计对象的名字， 银行名字，或国有银行、股份银行、城商银行 等等
            create_time: str = None,                # create_time需要转换为timestamp

            total: int = None,

            rate_type_i: int = None,
            rate_type_ii: int = None,
    ):
        super(WealthCountRateType, self).__init__(
            ukeyhash=ukeyhash,
            ukey=ukey,
            count_unit=count_unit,
            count_name=count_name,
            create_time=create_time,
            total=total,
        )
        self._rate_type_i = rate_type_i
        self._rate_type_ii = rate_type_ii

    @property
    def rate_type_i(self):
        return self._rate_type_i

    @rate_type_i.setter
    def rate_type_i(self, value):
        self._rate_type_i = value

    @property
    def rate_type_ii(self):
        return self._rate_type_ii

    @rate_type_ii.setter
    def rate_type_ii(self, value):
        self._rate_type_ii = value


class WealthCountPromiseType(WealthCount):

    def __init__(
            self,
            ukeyhash: str = None,
            ukey: str = None,                       # 格式为 count_name=count_unit=timestamp

            count_unit: str = None,                 # 统计维度单位 数量、金额
            count_name: str = None,                 # 统计对象的名字， 银行名字，或国有银行、股份银行、城商银行 等等
            create_time: str = None,                # create_time需要转换为timestamp

            total: int = None,

            promise_type_true: int = None,
            promise_type_false: int = None,
    ):
        super(WealthCountPromiseType, self).__init__(
            ukeyhash=ukeyhash,
            ukey=ukey,
            count_unit=count_unit,
            count_name=count_name,
            create_time=create_time,
            total=total,
        )

        self._promise_type_true = promise_type_true
        self._promise_type_false = promise_type_false

    @property
    def promise_type_true(self):
        return self._promise_type_true

    @promise_type_true.setter
    def promise_type_true(self, value):
        self._promise_type_true = value

    @property
    def promise_type_false(self):
        return self._promise_type_false

    @promise_type_false.setter
    def promise_type_false(self, value):
        self._promise_type_false = value


class WealthCountRisk(WealthCount):

    def __init__(
            self,
            ukeyhash: str = None,
            ukey: str = None,                       # 格式为 count_name=count_unit=timestamp

            count_unit: str = None,                 # 统计维度单位 数量、金额
            count_name: str = None,                 # 统计对象的名字， 银行名字，或国有银行、股份银行、城商银行 等等
            create_time: str = None,                # create_time需要转换为timestamp

            total: int = None,

            risk_o: int = None,
            risk_i: int = None,
            risk_ii: int = None,
            risk_iii: int = None,
            risk_iv: int = None,
            risk_v: int = None,
    ):
        super(WealthCountRisk, self).__init__(
            ukeyhash=ukeyhash,
            ukey=ukey,
            count_unit=count_unit,
            count_name=count_name,
            create_time=create_time,
            total=total,
        )
        self._risk_o: int = risk_o
        self._risk_i: int = risk_i
        self._risk_ii: int = risk_ii
        self._risk_iii: int = risk_iii
        self._risk_iv: int = risk_iv
        self._risk_v: int = risk_v

    @property
    def risk_o(self):
        return self._risk_o

    @risk_o.setter
    def risk_o(self, value):
        self._risk_o = value

    @property
    def risk_i(self):
        return self._risk_i

    @risk_i.setter
    def risk_i(self, value):
        self._risk_i = value

    @property
    def risk_ii(self):
        return self._risk_ii

    @risk_ii.setter
    def risk_ii(self, value):
        self._risk_ii = value

    @property
    def risk_iii(self):
        return self._risk_iii

    @risk_iii.setter
    def risk_iii(self, value):
        self._risk_iii = value

    @property
    def risk_iv(self):
        return self._risk_iv

    @risk_iv.setter
    def risk_iv(self, value):
        self._risk_iv = value

    @property
    def risk_v(self):
        return self._risk_v

    @risk_v.setter
    def risk_v(self, value):
        self._risk_v = value


class WealthCountTerm(WealthCount):

    def __init__(
            self,
            ukeyhash: str = None,
            ukey: str = None,                       # 格式为 count_name=count_unit=timestamp

            count_unit: str = None,                 # 统计维度单位 数量、金额
            count_name: str = None,                 # 统计对象的名字， 银行名字，或国有银行、股份银行、城商银行 等等
            create_time: str = None,                # create_time需要转换为timestamp

            total: int = None,

            term_i: int = None,
            term_ii: int = None,
            term_iii: int = None,
            term_iv: int = None,
            term_v: int = None,
            term_vi: int = None,
            term_vii: int = None,
    ):
        super(WealthCountTerm, self).__init__(
            ukeyhash=ukeyhash,
            ukey=ukey,
            count_unit=count_unit,
            count_name=count_name,
            create_time=create_time,
            total=total,
        )
        self._term_i: int = term_i
        self._term_ii: int = term_ii
        self._term_iii: int = term_iii
        self._term_iv: int = term_iv
        self._term_v: int = term_v
        self._term_vi: int = term_vi
        self._term_vii: int = term_vii

    @property
    def term_i(self):
        return self._term_i

    @term_i.setter
    def term_i(self, value):
        self._term_i = value

    @property
    def term_ii(self):
        return self._term_ii

    @term_ii.setter
    def term_ii(self, value):
        self._term_ii = value

    @property
    def term_iii(self):
        return self._term_iii

    @term_iii.setter
    def term_iii(self, value):
        self._term_iii = value

    @property
    def term_iv(self):
        return self._term_iv

    @term_iv.setter
    def term_iv(self, value):
        self._term_iv = value

    @property
    def term_v(self):
        return self._term_v

    @term_v.setter
    def term_v(self, value):
        self._term_v = value

    @property
    def term_vi(self):
        return self._term_vi

    @term_vi.setter
    def term_vi(self, value):
        self._term_vi = value

    @property
    def term_vii(self):
        return self._term_vii

    @term_vii.setter
    def term_vii(self, value):
        self._term_vii = value


class WealthCountAmountSize(WealthCount):

    def __init__(
            self,
            ukeyhash: str = None,
            ukey: str = None,                       # 格式为 count_name=count_unit=timestamp

            count_unit: str = None,                 # 统计维度单位 数量、金额
            count_name: str = None,                 # 统计对象的名字， 银行名字，或国有银行、股份银行、城商银行 等等
            create_time: str = None,                # create_time需要转换为timestamp

            total: int = None,

            amount_size_i: int = None,
            amount_size_ii: int = None,
            amount_size_iii: int = None,
            amount_size_iv: int = None,
            amount_size_v: int = None,
            amount_size_vi: int = None,
            amount_size_vii: int = None,
            amount_size_viii: int = None,
    ):
        super(WealthCountAmountSize, self).__init__(
            ukeyhash=ukeyhash,
            ukey=ukey,
            count_unit=count_unit,
            count_name=count_name,
            create_time=create_time,
            total=total,
        )
        self._amount_size_i: int = amount_size_i
        self._amount_size_ii: int = amount_size_ii
        self._amount_size_iii: int = amount_size_iii
        self._amount_size_iv: int = amount_size_iv
        self._amount_size_v: int = amount_size_v
        self._amount_size_vi: int = amount_size_vi
        self._amount_size_vii: int = amount_size_vii
        self._amount_size_viii: int = amount_size_viii

    @property
    def amount_size_i(self):
        return self._amount_size_i

    @amount_size_i.setter
    def amount_size_i(self, value):
        self._amount_size_i = value

    @property
    def amount_size_ii(self):
        return self._amount_size_ii

    @amount_size_ii.setter
    def amount_size_ii(self, value):
        self._amount_size_ii = value

    @property
    def amount_size_iii(self):
        return self._amount_size_iii

    @amount_size_iii.setter
    def amount_size_iii(self, value):
        self._amount_size_iii = value

    @property
    def amount_size_iv(self):
        return self._amount_size_iv

    @amount_size_iv.setter
    def amount_size_iv(self, value):
        self._amount_size_iv = value

    @property
    def amount_size_v(self):
        return self._amount_size_v

    @amount_size_v.setter
    def amount_size_v(self, value):
        self._amount_size_v = value

    @property
    def amount_size_vi(self):
        return self._amount_size_vi

    @amount_size_vi.setter
    def amount_size_vi(self, value):
        self._amount_size_vi = value

    @property
    def amount_size_vii(self):
        return self._amount_size_vii

    @amount_size_vii.setter
    def amount_size_vii(self, value):
        self._amount_size_vii = value

    @property
    def amount_size_viii(self):
        return self._amount_size_viii

    @amount_size_viii.setter
    def amount_size_viii(self, value):
        self._amount_size_viii = value


class WealthCountAmountMin(WealthCount):

    def __init__(
            self,
            ukeyhash: str = None,
            ukey: str = None,                       # 格式为 count_name=count_unit=timestamp

            count_unit: str = None,                 # 统计维度单位 数量、金额
            count_name: str = None,                 # 统计对象的名字， 银行名字，或国有银行、股份银行、城商银行 等等
            create_time: str = None,                # create_time需要转换为timestamp

            total: int = None,

            amount_min_i: int = None,
            amount_min_ii: int = None,
            amount_min_iii: int = None,
            amount_min_iv: int = None,
            amount_min_v: int = None,
            amount_min_vi: int = None,
            amount_min_vii: int = None,
            amount_min_viii: int = None,
    ):
        super(WealthCountAmountMin, self).__init__(
            ukeyhash=ukeyhash,
            ukey=ukey,
            count_unit=count_unit,
            count_name=count_name,
            create_time=create_time,
            total=total,
        )
        self._amount_min_i: int = amount_min_i
        self._amount_min_ii: int = amount_min_ii
        self._amount_min_iii: int = amount_min_iii
        self._amount_min_iv: int = amount_min_iv
        self._amount_min_v: int = amount_min_v
        self._amount_min_vi: int = amount_min_vi
        self._amount_min_vii: int = amount_min_vii
        self._amount_min_viii: int = amount_min_viii

    @property
    def amount_min_i(self):
        return self._amount_min_i

    @amount_min_i.setter
    def amount_min_i(self, value):
        self._amount_min_i = value

    @property
    def amount_min_ii(self):
        return self._amount_min_ii

    @amount_min_ii.setter
    def amount_min_ii(self, value):
        self._amount_min_ii = value

    @property
    def amount_min_iii(self):
        return self._amount_min_iii

    @amount_min_iii.setter
    def amount_min_iii(self, value):
        self._amount_min_iii = value

    @property
    def amount_min_iv(self):
        return self._amount_min_iv

    @amount_min_iv.setter
    def amount_min_iv(self, value):
        self._amount_min_iv = value

    @property
    def amount_min_v(self):
        return self._amount_min_v

    @amount_min_v.setter
    def amount_min_v(self, value):
        self._amount_min_v = value

    @property
    def amount_min_vi(self):
        return self._amount_min_vi

    @amount_min_vi.setter
    def amount_min_vi(self, value):
        self._amount_min_vi = value

    @property
    def amount_min_vii(self):
        return self._amount_min_vii

    @amount_min_vii.setter
    def amount_min_vii(self, value):
        self._amount_min_vii = value

    @property
    def amount_min_viii(self):
        return self._amount_min_viii

    @amount_min_viii.setter
    def amount_min_viii(self, value):
        self._amount_min_viii = value


class WealthCountRateMin(WealthCount):

    def __init__(
            self,
            ukeyhash: str = None,
            ukey: str = None,                       # 格式为 count_name=count_unit=timestamp

            count_unit: str = None,                 # 统计维度单位 数量、金额
            count_name: str = None,                 # 统计对象的名字， 银行名字，或国有银行、股份银行、城商银行 等等
            create_time: str = None,                # create_time需要转换为timestamp

            total: int = None,

            rate_min_i: int = None,
            rate_min_ii: int = None,
            rate_min_iii: int = None,
            rate_min_iv: int = None,
            rate_min_v: int = None,
            rate_min_vi: int = None,
            rate_min_vii: int = None,
            rate_min_viii: int = None,
            rate_min_ix: int = None,
            rate_min_x: int = None,
    ):
        super(WealthCountRateMin, self).__init__(
            ukeyhash=ukeyhash,
            ukey=ukey,
            count_unit=count_unit,
            count_name=count_name,
            create_time=create_time,
            total=total,
        )
        self._rate_min_i: int = rate_min_i
        self._rate_min_ii: int = rate_min_ii
        self._rate_min_iii: int = rate_min_iii
        self._rate_min_iv: int = rate_min_iv
        self._rate_min_v: int = rate_min_v
        self._rate_min_vi: int = rate_min_vi
        self._rate_min_vii: int = rate_min_vii
        self._rate_min_viii: int = rate_min_viii
        self._rate_min_ix: int = rate_min_ix
        self._rate_min_x: int = rate_min_x

    @property
    def rate_min_i(self):
        return self._rate_min_i

    @rate_min_i.setter
    def rate_min_i(self, value):
        self._rate_min_i = value

    @property
    def rate_min_ii(self):
        return self._rate_min_ii

    @rate_min_ii.setter
    def rate_min_ii(self, value):
        self._rate_min_ii = value

    @property
    def rate_min_iii(self):
        return self._rate_min_iii

    @rate_min_iii.setter
    def rate_min_iii(self, value):
        self._rate_min_iii = value

    @property
    def rate_min_iv(self):
        return self._rate_min_iv

    @rate_min_iv.setter
    def rate_min_iv(self, value):
        self._rate_min_iv = value

    @property
    def rate_min_v(self):
        return self._rate_min_v

    @rate_min_v.setter
    def rate_min_v(self, value):
        self._rate_min_v = value

    @property
    def rate_min_vi(self):
        return self._rate_min_vi

    @rate_min_vi.setter
    def rate_min_vi(self, value):
        self._rate_min_vi = value

    @property
    def rate_min_vii(self):
        return self._rate_min_vii

    @rate_min_vii.setter
    def rate_min_vii(self, value):
        self._rate_min_vii = value

    @property
    def rate_min_viii(self):
        return self._rate_min_viii

    @rate_min_viii.setter
    def rate_min_viii(self, value):
        self._rate_min_viii = value

    @property
    def rate_min_ix(self):
        return self._rate_min_ix

    @rate_min_ix.setter
    def rate_min_ix(self, value):
        self._rate_min_ix = value

    @property
    def rate_min_x(self):
        return self._rate_min_x

    @rate_min_x.setter
    def rate_min_x(self, value):
        self._rate_min_x = value


class WealthCountRateMax(WealthCount):

    def __init__(
            self,
            ukeyhash: str = None,
            ukey: str = None,                       # 格式为 count_name=count_unit=timestamp

            count_unit: str = None,                 # 统计维度单位 数量、金额
            count_name: str = None,                 # 统计对象的名字， 银行名字，或国有银行、股份银行、城商银行 等等
            create_time: str = None,                # create_time需要转换为timestamp

            total: int = None,

            rate_max_i: int = None,
            rate_max_ii: int = None,
            rate_max_iii: int = None,
            rate_max_iv: int = None,
            rate_max_v: int = None,
            rate_max_vi: int = None,
            rate_max_vii: int = None,
            rate_max_viii: int = None,
            rate_max_ix: int = None,
            rate_max_x: int = None,
    ):
        super(WealthCountRateMax, self).__init__(
            ukeyhash=ukeyhash,
            ukey=ukey,
            count_unit=count_unit,
            count_name=count_name,
            create_time=create_time,
            total=total,
        )
        self._rate_max_i: int = rate_max_i
        self._rate_max_ii: int = rate_max_ii
        self._rate_max_iii: int = rate_max_iii
        self._rate_max_iv: int = rate_max_iv
        self._rate_max_v: int = rate_max_v
        self._rate_max_vi: int = rate_max_vi
        self._rate_max_vii: int = rate_max_vii
        self._rate_max_viii: int = rate_max_viii
        self._rate_max_ix: int = rate_max_ix
        self._rate_max_x: int = rate_max_x

    @property
    def rate_max_i(self):
        return self._rate_max_i

    @rate_max_i.setter
    def rate_max_i(self, value):
        self._rate_max_i = value

    @property
    def rate_max_ii(self):
        return self._rate_max_ii

    @rate_max_ii.setter
    def rate_max_ii(self, value):
        self._rate_max_ii = value

    @property
    def rate_max_iii(self):
        return self._rate_max_iii

    @rate_max_iii.setter
    def rate_max_iii(self, value):
        self._rate_max_iii = value

    @property
    def rate_max_iv(self):
        return self._rate_max_iv

    @rate_max_iv.setter
    def rate_max_iv(self, value):
        self._rate_max_iv = value

    @property
    def rate_max_v(self):
        return self._rate_max_v

    @rate_max_v.setter
    def rate_max_v(self, value):
        self._rate_max_v = value

    @property
    def rate_max_vi(self):
        return self._rate_max_vi

    @rate_max_vi.setter
    def rate_max_vi(self, value):
        self._rate_max_vi = value

    @property
    def rate_max_vii(self):
        return self._rate_max_vii

    @rate_max_vii.setter
    def rate_max_vii(self, value):
        self._rate_max_vii = value

    @property
    def rate_max_viii(self):
        return self._rate_max_viii

    @rate_max_viii.setter
    def rate_max_viii(self, value):
        self._rate_max_viii = value

    @property
    def rate_max_ix(self):
        return self._rate_max_ix

    @rate_max_ix.setter
    def rate_max_ix(self, value):
        self._rate_max_ix = value

    @property
    def rate_max_x(self):
        return self._rate_max_x

    @rate_max_x.setter
    def rate_max_x(self, value):
        self._rate_max_x = value

