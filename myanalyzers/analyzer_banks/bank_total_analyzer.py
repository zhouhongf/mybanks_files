from myanalyzers.base.analyzer import Analyzer
from myanalyzers.base.wealth_analysis import WealthAnalysisOne


class BankTotalAnalyzer(Analyzer):
    analyzer_name = '全部银行分析'
    wealth_analysis = WealthAnalysisOne


def start():
    # BankTotalAnalyzer.start()
    pass