from mycleaners.base.cleaner import Cleaner
from mycleaners.base.manual_table import ManualTable
from mycleaners.base.manual_text import ManualText
from mycleaners.base.manual_online_list import ManualOnlineList


class IcbcTable(ManualTable):
    table_labels_config = {}


class IcbcText(ManualText):
    labels_check_config = {}
    labels_check_one_config = {}


class IcbcOnlineList(ManualOnlineList):
    labels_check_config = {}


class IcbcCleaner(Cleaner):
    name = 'IcbcCleaner'
    bank_name = '工商银行'
    bank_level = '国有银行'

    def process_parse(self, bank_level, ukey, tables, text):
        dict_wealth = IcbcTable.start(self.bank_name, bank_level, ukey, tables)
        # print('一解析的内容是：%s' % dict_wealth)
        dict_wealth = IcbcText.start(self.bank_name, dict_wealth, text)
        # print('二解析的内容是：%s' % dict_wealth)
        dict_wealth = IcbcOnlineList.start(self.bank_name, dict_wealth)
        # print('三解析的内容是：%s' % dict_wealth)
        for k, v in dict_wealth.items():
            data = v.do_dict_data()
            # print('准备保存的wealth是：', data)
            self.mongo.do_insert_one(self.collection_cleans, {'_id': data['_id']}, data)


def start():
    IcbcCleaner.start()
    # pass


