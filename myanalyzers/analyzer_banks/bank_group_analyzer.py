from myanalyzers.base.analyzer import Analyzer
from myanalyzers.base.wealth_analysis import WealthAnalysisOne


class BankGroupAnalyzer(Analyzer):
    analyzer_name = '分组银行分析'
    wealth_analysis = WealthAnalysisOne


def start():
    # BankGroupAnalyzer.start()
    pass