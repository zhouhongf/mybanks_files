from mycleaners.base.cleaner import Cleaner
from mycleaners.base.wealth import Wealth
from mycleaners.base.manual_table import ManualTable
from mycleaners.base.manual_text import ManualText
from utils.nlp_util import parse_regex
import re


class CmbchinaTable(ManualTable):

    table_labels_config = {
        'fee_types_extra': {'管理费', '托管费'},
        'invest_on': {'投资范围'},
    }

    pattern_fee_types_extra = re.compile(r'收取([销售托管其他手续固定认购投资]+(管理|服务)?费)[\s:：，,年费率为]*([0-9]+(\.[0-9]+)*)[%％]')

    def extract_fee_types_extra(self, label: str, value: str, wealth: Wealth):
        results = parse_regex(self.pattern_fee_types_extra, value, many=True)
        if results:
            fees = {}
            fee_rate = 0.0
            for one in results:
                name = one[0]
                amount = float(one[2])
                amount = round(amount / 100, 6)
                if amount < 0.01 and amount != 0.0:     # 设定一个检查值，即费率小于1%的，才加入fees字典中
                    fees[name] = amount                 # 字典中如果key相同，则自动更新内容
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


class CmbchinaText(ManualText):
    labels_check_config = {}
    labels_check_one_config = {}


class CmbchinaCleaner(Cleaner):
    name = 'CmbchinaCleaner'
    bank_name = '招商银行'

    def process_parse(self, ukey, tables, text):
        # print('解析出来的文字内容是：%s' % text)
        dict_wealth = CmbchinaTable.start(self.bank_name, ukey, tables)
        dict_wealth = CmbchinaText.start(self.bank_name, dict_wealth, text)
        print('解析的内容是：%s' % dict_wealth)

def start():
    # CmbchinaCleaner.start()
    pass



