from myanalyzers.base.analyzer import Analyzer
from myanalyzers.base.wealth_analysis import WealthAnalysisOne
from utils.time_util import get_week_number
from myanalyzers.analyzer_banks.mongo_operators import MongoOperators

# 原始数据collection标题使用中文或英文大写，加工过后的数据collection标题使用英文小写
# 计算后的数字，推荐使用float或Double类型，以避免int类不超过8bytes的限制


class BankSingleAnalyzer(Analyzer):
    analyzer_name = '单个银行分析'
    wealth_analysis = WealthAnalysisOne

    def handle_task(self, data_in):
        print('传入的data_in是：', data_in)
        bank_name = data_in['bank_name']
        bank_type = data_in['bank_type']
        last_sunday = data_in['last_sunday']
        last_week_number = get_week_number()

        select_list = [
            {'$match': {'bank_name': bank_name, 'currency': '人民币', 'create_time': {'$gt': last_sunday}}},
            {'$addFields': {'_id': bank_name + '=' + last_week_number, 'bank_type': bank_type}},
            {'$merge': {'into': 'wealth_weekly', 'whenMatched': 'replace'}}
        ]
        select_list.insert(1, MongoOperators.op_categorize_wealth)
        # print('更新过后的select_list是：', select_list)
        self.collection_cleans.aggregate(select_list)



    def handle_task_backup(self, data_in):
        print('传入的data_in是：', data_in)
        bank_name = data_in['bank_name']
        bank_type = data_in['bank_type']
        last_sunday = data_in['last_sunday']
        last_week_number = get_week_number()

        select_list = [
            {'$match': {'bank_name': bank_name, 'create_time': {'$gt': last_sunday}}},
            {'$group': {
                '_id': bank_name + '=' + last_week_number,
                'num_all': {'$sum': 1},
                'amt_size_all': {'$sum': '$amount_size_max'},
                'amt_size_avg': {'$avg': '$amount_size_max'},
                'amt_size_max': {'$max': '$amount_size_max'},
                'amt_size_min': {'$min': '$amount_size_max'},
                'amt_start_avg': {'$avg': '$amount_buy_min'},
                'amt_start_max': {'$max': '$amount_buy_min'},
                'amt_start_min': {'$min': '$amount_buy_min'},
            }},
            {'$addFields': {'bank_type': bank_type}},
            {'$merge': {'into': 'wealth_weekly', 'whenMatched': 'replace'}}
        ]
        self.collection_cleans.aggregate(select_list)



def start():
    BankSingleAnalyzer.start()
    # pass
