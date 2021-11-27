from mycleaners.base.cleaner import Cleaner
from mycleaners.base.wealth import Wealth
from mycleaners.base.manual_table import ManualTable
from mycleaners.base.manual_text import ManualText
from utils.nlp_util import find_datetimes, parse_datetime, transfer_to_yuan, percent_to_num
import re



class SpdbTable(ManualTable):

    table_labels_config = {
        'amount_size': {'募集金额', '产品规模', '发行规模', '开放规模', '认购规模', '募集规模', '发售规模', '单期规模'},
        'amount_buy_min': {'认购起点', '单笔认购', '起存金额', '认购金额', '申购金额', '申购份额', '认购份额', '最低持有份额'},
    }

    pattern_code_spdb = re.compile(r'([0-9]{6,})[产品代码编号登记为是：:\s]{4,}([A-Za-z0-9][-+A-Za-z0-9]+)?')
    pattern_rate_spdb = re.compile(r'[保底收益利率]{4,}[为：:\s]*([0-9]+(\.[0-9]+)*[%％])[,，;；][浮动收益利率范围]{4,}[为：:\s]*([0-9]+(\.[0-9]+)*[%％])[~或到和\-]([0-9]+(\.[0-9]+)*[%％])')
    pattern_rate_extra_spdb = re.compile(r'([0-9]+(\.[0-9]+)*[%％]?)[~或到和\-]([0-9]+(\.[0-9]+)*[%％])')

    pattern_fee_spdb = re.compile(r'产品管理费|托管费|投资管理费|销售手续费|认购费|固定管理费')

    pattern_date_period_spdb = re.compile(r'([0-9A-Za-z]{6,})([0-9]{4}年[0-9]{1,2}月[0-9]{1,2}日)-([0-9]{4}年[0-9]{1,2}月[0-9]{1,2}日)')
    pattern_date_spdb = re.compile(r'([0-9A-Za-z]{6,})([0-9]{4}年[0-9]{1,2}月[0-9]{1,2}日)')

    def extract_raise_period(self, label: str, value: str, wealth: Wealth):
        date_start = {'扣款日', '起息日', '成立日', '开始日', '起始日', '起算日'}
        for date in date_start:
            if date in label:
                return wealth

        results = self.pattern_date_period_spdb.findall(value)
        if results:
            ukey = self.ukey
            code = ukey.split('=')[-1]
            for one in results:
                code_one = one[0]
                if code_one == code:
                    date_open = one[1]
                    date_close = one[2]
                    if date_open and date_close:
                        wealth.date_open = parse_datetime(date_open)
                        wealth.date_close = parse_datetime(date_close)
            return wealth

        list_datetimes = find_datetimes(value)
        wealth.date_open = list_datetimes[0]
        wealth.date_close = list_datetimes[-1]
        return wealth

    def extract_date_start(self, label: str, value: str, wealth: Wealth):
        results = self.pattern_date_spdb.findall(value)
        if results:
            ukey = self.ukey
            code = ukey.split('=')[-1]
            for one in results:
                code_one = one[0]
                if code_one == code:
                    date_need = one[1]
                    if date_need:
                        wealth.date_start = parse_datetime(date_need)
            return wealth

        list_datetimes = find_datetimes(value)
        if list_datetimes:
            wealth.date_start = list_datetimes[0]
        return wealth

    def extract_date_end(self, label: str, value: str, wealth: Wealth):
        results = self.pattern_date_spdb.findall(value)
        if results:
            ukey = self.ukey
            code = ukey.split('=')[-1]
            for one in results:
                code_one = one[0]
                if code_one == code:
                    date_need = one[1]
                    if date_need:
                        wealth.date_end = parse_datetime(date_need)
            return wealth

        list_datetimes = find_datetimes(value)
        if list_datetimes:
            wealth.date_end = parse_datetime(list_datetimes[0])
        return wealth

    def extract_name(self, label: str, value: str, wealth: Wealth):
        ukey = self.ukey
        code = ukey.split('=')[-1]
        wealth.code = code

        name = value.strip()
        wealth.name = name

        wealth = self.extract_product_type(label, value, wealth)
        if not wealth.code_register:
            results = self.pattern_code_spdb.search(name)
            if results:
                wealth.code_register = results.group(2)
                return wealth

            res = self.pattern_code_register_in_name.search(name)
            if res:
                wealth.code_register = res.group(2)
                return wealth
        return wealth

    def extract_rate_type(self, label: str, value: str, wealth: Wealth):
        if '业绩' in label:
            wealth.rate_type = '净值型'
            wealth.promise_type = '非保本'
            wealth.fixed_type = '浮动收益'
        elif '收益率' in label:
            wealth.rate_type = '预期收益型'

        # 使用正则表达式，匹配是否为保本或非保本
        wealth = self.extract_promise_type(label, value, wealth)
        # 重要，使用extract_product_type()再次匹配关键字，或正则表达式搜索匹配 业绩比较基准 或 预期收益率
        wealth = self.extract_product_type(label, value, wealth)

        ukey = self.ukey
        code = ukey.split('=')[-1]
        list_value = value.split(code)
        if len(list_value) == 2:
            value = list_value[1]

        list_data = []
        res = self.pattern_rate_spdb.search(value)
        if res:
            rate_base = res.group(1)
            rate_floor = res.group(3)
            rate_ceil = res.group(5)
            if rate_base:
                num_base = percent_to_num(rate_base)
                if rate_floor and rate_ceil:
                    num_floor = percent_to_num(rate_floor)
                    num_ceil = percent_to_num(rate_ceil)
                    num_floor = round(num_base + num_floor, 6)
                    num_ceil = round(num_base + num_ceil, 6)
                    if num_ceil < 0.15 and num_floor < 0.15:
                        list_data.append(num_floor)
                        list_data.append(num_ceil)
                        list_data.sort(reverse=True)
                        wealth.rate_max = list_data[0]
                        wealth.rate_min = list_data[-1]
                    else:
                        self.log.error('收益率num_ceil: %s或num_floor: %s超过0.15' % (str(num_ceil), str(num_floor)))
                else:
                    wealth.rate_max = num_base
                    wealth.rate_min = num_base
                return wealth

        list_data = []
        res_extra = self.pattern_rate_extra_spdb.search(value)
        if res_extra:
            rate_floor = res_extra.group(1)
            rate_ceil = res_extra.group(3)
            if rate_floor and rate_ceil:
                num_floor = percent_to_num(rate_floor + '%')
                num_ceil = percent_to_num(rate_ceil)
                num_floor = round(num_floor, 6)
                num_ceil = round(num_ceil, 6)
                if num_ceil < 0.15 and num_floor < 0.15:
                    list_data.append(num_floor)
                    list_data.append(num_ceil)
                    list_data.sort(reverse=True)
                    wealth.rate_max = list_data[0]
                    wealth.rate_min = list_data[-1]
                else:
                    self.log.error('收益率num_ceil: %s或num_floor: %s超过0.15' % (str(num_ceil), str(num_floor)))
            return wealth

        list_data = []
        results = self.pattern_rate.finditer(value)
        for one in results:
            word = one.group(0)
            if word:
                num = percent_to_num(word)
                if num < 0.15:
                    list_data.append(num)
                else:
                    self.log.error('收益率超过0.15，解析出来的num为：%s' % str(num))
        if len(list_data) > 0:
            list_data.sort(reverse=True)
            wealth.rate_max = list_data[0]
            wealth.rate_min = list_data[-1]
        return wealth


    def extract_fee_types(self, label: str, value: str, wealth: Wealth):
        ukey = self.ukey
        code = ukey.split('=')[-1]
        list_value = value.split(code)
        if len(list_value) == 2:
            value = list_value[1]

        fees = wealth.fee_types if wealth.fee_types else {}

        result = self.pattern_fee_spdb.search(label)
        if result:
            fee_name = result.group(0)
            if fee_name:
                res = self.pattern_rate.search(value)
                fee_text = res.group(0)
                if fee_text:
                    fee_rate = percent_to_num(fee_text)
                    if 0.0 < fee_rate < 0.01:
                        fees[fee_name] = fee_rate
                        fee_total = 0.0
                        for v in fees.values():
                            fee_total += v
                        wealth.fee_rate = round(fee_total, 6)
                        wealth.fee_types = fees
                        return wealth

        results = self.pattern_fee_types.finditer(value)
        fees = {}
        fee_rate = 0.0
        for one in results:
            name = one.group(1)
            amount = float(one.group(3))
            amount = round(amount / 100, 6)
            if 0.0 < amount < 0.01:                     # 设定一个检查值，即费率小于1%的，才加入fees字典中
                fees[name] = amount                     # 字典中如果key相同，则自动更新内容
                fee_rate += amount
        if len(fees) > 0:
            if not wealth.fee_types:
                wealth.fee_rate = round(fee_rate, 6)
                wealth.fee_types = fees
            else:
                fees.update(wealth.fee_types)
                fee_total = 0.0
                for v in fees.values():
                    fee_total += v
                wealth.fee_rate = round(fee_total, 6)
                wealth.fee_types = fees
        return wealth

    def extract_amount_size(self, label: str, value: str, wealth: Wealth):
        ukey = self.ukey
        code = ukey.split('=')[-1]
        list_value = value.split(code)
        if len(list_value) == 2:
            value = list_value[1]

        results = self.pattern_amount.finditer(value)
        list_amount = []
        for one in results:
            amount = one.group(0)
            if amount:
                num = transfer_to_yuan(amount)
                if num > 1000000:                   # 募集金额低于100万的自动过滤掉
                    list_amount.append(num)
        if len(list_amount) > 0:
            list_amount.sort(reverse=True)
            amount_max = list_amount[0]
            amount_min = list_amount[-1]
            if not wealth.amount_size_max:
                wealth.amount_size_max = amount_max
            else:
                if amount_max > wealth.amount_size_max:
                    wealth.amount_size_max = amount_max

            if not wealth.amount_size_min:
                wealth.amount_size_min = amount_min
            else:
                if amount_min < wealth.amount_size_min:
                    wealth.amount_size_min = amount_min
        return wealth

    def extract_amount_buy_min(self, label: str, value: str, wealth: Wealth):
        ukey = self.ukey
        code = ukey.split('=')[-1]
        list_value = value.split(code)
        if len(list_value) == 2:
            value = list_value[1]

        result = self.pattern_amount_per_buy.search(value)
        if result:
            one = result.group(0)
            num = transfer_to_yuan(one)
            if not wealth.amount_per_buy:
                wealth.amount_per_buy = num
            else:
                if num < wealth.amount_per_buy:
                    wealth.amount_per_buy = num
            # 此处的value为已经全部去掉“XXX万元的整数倍”文字后的内容
            value = self.pattern_amount_per_buy.sub('', value)

        num = None
        res = self.pattern_amount_buy_min.search(value)
        if res:
            one = res.group(0)
            num = transfer_to_yuan(one)
        else:
            results = self.pattern_amount.finditer(value)   # 如果pattern_amount_buy_min正则未匹配到，则使用pattern_amount找出所有的金额数字，取最小值为amount_buy_min的数值
            list_results = []
            for one in results:
                amount = one.group(0)
                if amount:
                    num = transfer_to_yuan(amount)
                    list_results.append(num)
            if len(list_results) > 0:
                list_results.sort(reverse=True)
                num = list_results[-1]                      # 找出value单元格中最小的数字，将其设置为amount_buy_min的数值

        # 起购金额最低设置为1万
        if num and num >= 10000:
            if wealth.amount_size_min:
                if num > wealth.amount_size_min:
                    return wealth
            if wealth.amount_size_max:
                if num > wealth.amount_size_max:
                    return wealth

            if not wealth.amount_buy_min:
                wealth.amount_buy_min = num
            else:
                if num < wealth.amount_buy_min:
                    wealth.amount_buy_min = num
        return wealth


class SpdbText(ManualText):
    labels_check_config = {}
    labels_check_one_config = {}

    def do_parse_text(self, wealth: Wealth):
        if not wealth.invest_on:
            if '结构性存款产品说明书' in self.text:
                wealth.invest_on = '结构性存款'
        if wealth.custodian == '上海浦东发展银行':
            wealth.custodian = None
        return wealth


class SpdbCleaner(Cleaner):
    name = 'SpdbCleaner'
    bank_name = '浦发银行'

    def process_parse(self, ukey, tables, text):
        # print('解析出来的tables内容是：%s' % tables)
        dict_wealth = SpdbTable.start(self.bank_name, ukey, tables)
        dict_wealth = SpdbText.start(self.bank_name, dict_wealth, text)
        print('解析的内容是：%s' % dict_wealth)



def start():
    # SpdbCleaner.start()
    pass



