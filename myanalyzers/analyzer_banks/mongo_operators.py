# Mongo数据库操作命令
import time


class MongoOperators:
    # 收益类型 分类
    # 保本类型 分类
    # 风险等级 分类

    # 理财期限 分类
    # 理财规模 分类
    # 起购金额 分类

    # 最大利率 分类
    # 最小利率 分类
    op_categorize_wealth = {
        '$facet': {
            "categorizedByRateType": [
                {'$sortByCount': '$rate_type'}
            ],
            "categorizedByPromiseType": [
                {'$sortByCount': '$promise_type'}
            ],
            "categorizedByRisk": [
                {'$match': {'risk': {'$exists': 1}}},
                {
                    '$bucket': {
                        'groupBy': '$risk',
                        'boundaries': [0, 1, 2, 3, 4, 5, 6],
                        'default': -1,
                        'output': {
                            'num': {'$sum': 1},
                            'sum': {'$sum': '$risk'},
                            'avg': {'$avg': '$risk'},
                            'max': {'$max': '$risk'},
                            'min': {'$min': '$risk'},
                            'wkey': {'$push': '$wkey'}
                        }
                    }
                }
            ],
            "categorizedByTerm": [
                {'$match': {'term': {'$exists': 1}}},
                {
                    '$bucket': {
                        'groupBy': '$term',
                        'boundaries': [0, 7, 30, 90, 180, 365, 1095, 3650, 36500],
                        'default': -1,
                        'output': {
                            'num': {'$sum': 1},
                            'sum': {'$sum': '$term'},
                            'avg': {'$avg': '$term'},
                            'max': {'$max': '$term'},
                            'min': {'$min': '$term'},
                            'wkey': {'$push': '$wkey'}
                        }
                    }
                }
            ],
            "categorizedByAmountSize": [
                {'$match': {'amount_size_max': {'$exists': 1}}},
                {
                    '$bucket': {
                        'groupBy': '$amount_size_max',
                        'boundaries': [10000, 1000000, 10000000, 20000000, 50000000, 100000000, 500000000, 1000000000, 5000000000, 10000000000, 20000000000, 50000000000, 100000000000, 1000000000000],
                        'default': -1,
                        'output': {
                            'num': {'$sum': 1},
                            'sum': {'$sum': '$amount_size_max'},
                            'avg': {'$avg': '$amount_size_max'},
                            'max': {'$max': '$amount_size_max'},
                            'min': {'$min': '$amount_size_max'},
                            'wkey': {'$push': '$wkey'}
                        }
                    }
                }
            ],
            "categorizedByAmountBuy": [
                {'$match': {'amount_buy_min': {'$exists': 1}}},
                {
                    '$bucket': {
                        'groupBy': '$amount_buy_min',
                        'boundaries': [1, 1000, 10000, 50000, 100000, 500000, 1000000, 2000000, 5000000, 10000000, 20000000, 50000000, 100000000, 1000000000],
                        'default': -1,
                        'output': {
                            'num': {'$sum': 1},
                            'sum': {'$sum': '$amount_buy_min'},
                            'avg': {'$avg': '$amount_buy_min'},
                            'max': {'$max': '$amount_buy_min'},
                            'min': {'$min': '$amount_buy_min'},
                            'wkey': {'$push': '$wkey'}
                        }
                    }
                }
            ],
            "categorizedByRateMax": [
                {'$match': {'rate_max': {'$exists': 1}}},
                {
                    '$bucket': {
                        'groupBy': '$rate_max',
                        'boundaries': [0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.15],
                        'default': -1,
                        'output': {
                            'num': {'$sum': 1},
                            'sum': {'$sum': '$rate_max'},
                            'avg': {'$avg': '$rate_max'},
                            'max': {'$max': '$rate_max'},
                            'min': {'$min': '$rate_max'},
                            'wkey': {'$push': '$wkey'}
                        }
                    }
                }
            ],
            "categorizedByRateMin": [
                {'$match': {'rate_min': {'$exists': 1}}},
                {
                    '$bucket': {
                        'groupBy': '$rate_min',
                        'boundaries': [0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.15],
                        'default': -1,
                        'output': {
                            'num': {'$sum': 1},
                            'sum': {'$sum': '$rate_min'},
                            'avg': {'$avg': '$rate_min'},
                            'max': {'$max': '$rate_min'},
                            'min': {'$min': '$rate_min'},
                            'wkey': {'$push': '$wkey'}
                        }
                    }
                }
            ],
            "summary": [
                {'$group': {
                    '_id': int(time.time() * 1000),
                    'num_all': {'$sum': 1},
                    'amt_size_all': {'$sum': '$amount_size_max'},
                    'amt_size_avg': {'$avg': '$amount_size_max'},
                    'amt_size_max': {'$max': '$amount_size_max'},
                    'amt_size_min': {'$min': '$amount_size_max'},
                    'amt_start_avg': {'$avg': '$amount_buy_min'},
                    'amt_start_max': {'$max': '$amount_buy_min'},
                    'amt_start_min': {'$min': '$amount_buy_min'},
                }},
            ]
        }
    }
