from mycleaners.base.cleaner import Cleaner
from mycleaners.base.manual_table import ManualTable
from mycleaners.base.manual_text import ManualText
from mycleaners.base.wealth import Wealth


# 本文件为示例文件
class DemoTable(ManualTable):

    #table_labels_config = {
    #    'loan_rule_two': {'质押条款2', '融资服务2'},
    #}

    def do_clean(self, wealth: Wealth, table: list):
        print('==============CmbchinaTableDict的do_clean方法=====================')
        return wealth


class DemoCleaner(Cleaner):
    name = 'CmbchinaCleaner'
    bank_name = '招商银行'

    # 如果要使用start_init()方法的，则把要打开的文件，复制一份至data/manual文件夹下
    #def start_init(self):
    #    with open('中信银行=123.html', 'rb') as f:
    #        content = f.read()
    #        ukey = '中信银行=123'
    #        content_type = '.html'
    #        manual_in = Manual(ukey=ukey, content=content, content_type=content_type)
    #        yield manual_in

    def process_parse(self, ukey, tables, text):
        # print('解析出来的文字内容是：%s' % text)
        list_wealth = DemoTable(self.bank_name, ukey, tables).start()
        list_wealth = ManualText(self.bank_name, text, list_wealth).start()
        print('解析出来的表格内容是：%s' % list_wealth)


def start():
    DemoCleaner.start()
    # pass



