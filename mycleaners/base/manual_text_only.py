#适用于一个文件内就含一个Wealth的情况
import re
from config.log import Logger
from config import CONFIG
import os
from utils.nlp_util import transfer_to_yuan, find_datetimes, percent_to_num
from mycleaners.base.wealth import Wealth
import farmhash
from constants import BankDict
from utils.nlp_util import UTIL_CN_NUM
from datetime import datetime, timedelta


class ManualTextOnly(object):
    log_path = os.path.join(CONFIG.LOG_DIR, 'ManualTextOnly.log')
    log = Logger(log_path, level='warning').logger

    labels_check = {
        'raise_period',         # pass
        'invest_period',        # pass
        'product_type',         # pass
        'amount_size',
        'name',                 # pass
        'code',
        'code_register',
        'currency',             # pass
        'risk',                 # pass
        'rate_max',
        'rate_min',
        'rate_type',
        'redeem_type',
        'fixed_type',
        'promise_type',         # pass
        'raise_type',
        'date_open',            # pass
        'date_close',           # pass
        'date_start',           # pass
        'date_end',             # pass
        'term',                 # pass
        'amount_size_min',
        'amount_size_max',
        'amount_buy_min',       # pass
        'amount_buy_max',
        'amount_per_buy',       # pass
        'custodian',            # pass
        'fee_types',            # pass
        'fee_rate',             # pass
        'sale_areas',
        'sale_ways',            # pass
        'sale_agents',
        'invest_on',
        'loan_rule',
    }
    pattern_invest_period = re.compile(r'投资封闭期[为是：:\s]*[0-9]{2,4}[年/][0-9]{1,2}[月/][0-9]{1,2}日?[上中下午晚早\s]*[0-9\s]*[点:.时]?[0-9\s]*分?[至到-]?([0-9]{2,4}[年/])?[0-9]{1,2}[月/][0-9]{1,2}日?[上中下午晚早\s]*[0-9\s]*[点:.时]?[0-9\s]*分?')
    pattern_raise_period = re.compile(r'[募集发行认申购开放]{2,}期[为是：:\s]*[0-9]{2,4}[年/][0-9]{1,2}[月/][0-9]{1,2}日?[上中下午晚早\s]*[0-9\s]*[点:.时]?[0-9\s]*分?[至到-]?([0-9]{2,4}[年/])?[0-9]{1,2}[月/][0-9]{1,2}日?[上中下午晚早\s]*[0-9\s]*[点:.时]?[0-9\s]*分?')
    pattern_product_type = re.compile(r'[理财计划产品]*产品类型[属于为是：:\s]*[非保本证固定浮动收益开放式封闭净值型类公私募,，、]{5,}|本[期理财]*产品[属于为是：:\s]*[非保本证固定浮动收益开放式封闭净值型类公私募,，、\s]{5,}[理财]*产品')
    pattern_amount_size = re.compile(r'')

    pattern_name = re.compile(r'产品名称([\u4e00-\u9fa5、，,:：·“”"+\[\]\s（）()A-Za-z0-9\-]+?[理财结构性存款]{2,}产品([0-9]+年)?([0-9]+期)?([0-9]+款)?)')

    pattern_code = re.compile(r'[产品单元理财计划]{2,}[的认购]*[代码编号]{2}[为是：:\s]*([A-Za-z0-9][-+A-Za-z0-9]+)')
    pattern_code_register = re.compile(r'(登记|注册)[编码代号]+[为是：:\s]*([A-Za-z0-9]{6,})')
    pattern_currency = re.compile(r'[销售投资及收益本币]{2,}币种(人民币|美元|欧元|日元|英镑)')

    pattern_risk_dig = re.compile(r'风险[评等分][级类][属于为是：:\s]*([0-9A-Za-z零一二三四五]+)级?')
    pattern_risk_cn = re.compile(r'风险[评等分][级类][属于为是：:\s]*[基本]*([无低较中等高极]+风险)')
    pattern_risk_cn_extra = re.compile(r'风险[评等分][级类][属于为是：:\s]*[基本]*(无|低|极低|较低|中低|中等|高|较高|中高)[风险]*')

    pattern_rate = re.compile(r'(业绩比较基准|业绩基准|预期收益率|实现年化收益|预期理财收益率|预期年化收益率|预期到期利率|净值型|结构性存款)[\u4e00-\u9fa5（()）]*([0-9]+(\.)?[0-9]*)[%％]')
    pattern_rate_type = re.compile(r'业绩比较基准|业绩基准|预期收益率|实现年化收益|预期理财收益率|预期年化收益率|预期到期利率|净值型|结构性存款')

    pattern_redeem_type_sub = re.compile(r'(如果|若|假设)[封闭期内投资理财计划成立后]*(投资者|投资人|客户)[不没]?(得|享有|开放|可以|可|能|能够|无|有|接受)[提前]*赎回')
    pattern_redeem_type = re.compile(r'(投资者|投资人|客户)[不没]?(得|享有|开放|可以|可|能|能够|无|有|接受)[提前]*赎回|本[理财产品计划投资]{2,}[在产品到期日之前封闭内]*[不没]?(对|得|享有|开放|可以|可|能|能够|无|有|接受)[\u4e00-\u9fa5]*赎回')
    pattern_redeem_type_extra = re.compile(r'[存续封闭期内投资理财计划成立后]*[不没]?(得|享有|开放|可以|可|能|能够|无|有|接受)[提前申购和与或]*赎回')


    pattern_fixed_type = re.compile(r'')
    pattern_promise_type = re.compile(r'本[投资产品理财计划的]+([不无]?)[提供]*本金[完全]*[保障担证]{2}|([不无]?)[保障担证]{2}[理财购买资金]*[金额本]{2}')
    pattern_raise_type = re.compile(r'')

    pattern_date_open = re.compile(r'[申认购]{2,}[开始日期时间]{3,}[为是：:\s]*[0-9]{2,4}[年/-][0-9]{1,2}[月/-][0-9]{1,2}日?')
    pattern_date_close = re.compile(r'[申认购]{2,}[结束日期时间]{3,}[为是：:\s]*[0-9]{2,4}[年/-][0-9]{1,2}[月/-][0-9]{1,2}日?')
    pattern_date_start = re.compile(r'[投资产品理财计划的]*[起算扣款息成立开始]{2,}[日期时间]{1,2}[为是：:\s]*[0-9]{2,4}[年/-][0-9]{1,2}[月/-][0-9]{1,2}日?')
    pattern_date_end = re.compile(r'[投资产品理财计划的]*[到期终止结束]{2,}[日期时间]{1,2}[为是：:\s]*[0-9]{2,4}[年/-][0-9]{1,2}[月/-][0-9]{1,2}日?')

    pattern_term = re.compile(r'[理财产品计划]{2,}期限[为是：:\s]*([0-9]+)\s*([天日月年])')
    pattern_term_final = re.compile(r'[理财产品计划]*期限[为是：:\s]*[无没有]{1,2}固定期限')

    pattern_amount_size_min = re.compile(r'[理财产品初始]{2,}[计划总发行认购最大运作]*[规模量额度]{1,}下限[为是：:\s]*([1-9][0-9]*(\.[0-9]+)*[亿万千百美欧元英镑日\s]+)')
    pattern_amount_size_max = re.compile(r'[理财产品初始]{2,}[计划总发行认购最大运作]*[规模量额度]{1,}[上限为是：:\s]*([1-9][0-9]*(\.[0-9]+)*[亿万千百美欧元英镑日\s]+)')
    pattern_amount_buy_min = re.compile(r'[起点份额认购买金最低余申产品销售]{4,}[个人对公机构:：为不低于\s]*(人民币|美元|欧元|英镑|日元)*\s*([1-9][0-9]*)\s*([亿万千百元]+)起?')
    pattern_amount_buy_max = re.compile(r'')
    pattern_amount_per_buy = re.compile(r'[1-9][0-9]*[亿万千百美欧英镑日元份\s]+的?整数倍')

    pattern_custodian = re.compile(r'本[投资产品理财计划的]+(托管)(人|单位|机构|银行)[为是：:\s]*([\u4e00-\u9fa5]+[农村商业城市银行股份有限公司]{2,})')
    pattern_custodian_extra = re.compile(r'(托管)(人|单位|机构|银行|行)[为是：:\s]*([\u4e00-\u9fa5]+[农村商业城市银行股份有限公司]{2,})')

    pattern_fee_types = re.compile(r'([销售托管其他手续固定申认购投资]*(管理|服务)?费)[\s:：率为年化（()）]*([0-9]+(\.[0-9]+)*)[%％][\s/每年]*')
    pattern_fee_rate = re.compile(r'')

    pattern_sale_areas = re.compile(r'')
    pattern_sale_ways = re.compile(r'销售渠道[\u4e00-\u9fa5]+?(授权网点|网点柜面|网银|网上银行|网上个人银行|手机银行|营业网点|微信银行|电话银行|掌上银行|现金管理平台|自助渠道|电子渠道)[网点柜面银上行个人手机营业微信电话掌现金管理平台自助渠道子、，；;,\s]+')
    pattern_sale_ways_extra = re.compile(r'(网点柜面|营业网点|授权网点|网银|网上银行|网上个人银行|手机银行|微信银行|电话银行|掌上银行|现金管理平台|自助渠道|电子渠道)+')
    pattern_sale_agents = re.compile(r'(销售)[人单位机构银行]{1,2}[为是：:\s]*([\u4e00-\u9fa5]{2,10}[农村商业城市银行股份有限公司]{2,})')

    pattern_invest_on = re.compile(r'本[期]?理财[理财募集的资计划产品本金最终可存续期间,，管人主要]*投资于[以下投资工具：:\s]*([\u4e00-\u9fa5、，；;,:：%％+\[\]（）()A-Za-z0-9\-]+)。')
    pattern_loan_rule = re.compile(r'本[理财计划产品]+[不没]?(得|可以|可|能|能够|无|有)[质押融资贷款]{2,}')

    list_risk = BankDict.list_risk
    list_currency = BankDict.list_currency

    def __init__(self, bank_name: str, ukey: str, text: str):
        self.bank_name = bank_name
        self.ukey = ukey
        self.text = re.sub(r'[【】\s]+', '', text)
        config = getattr(self, 'labels_check_config', None)
        if config:
            if not isinstance(config, set):
                raise ValueError("labels_check_config must be type of set")
            self.labels_check.update(config)

    @classmethod
    def start(cls, bank_name: str, ukey: str, text: str):
        manual_text_in = cls(bank_name, ukey, text)
        list_need = manual_text_in._start()
        return list_need

    def _start(self):
        wealth = Wealth(ukey=self.ukey)
        wealth = self.makeup_wealth(wealth)
        wealth = self.final_makeup_wealth(wealth)
        return wealth

    def makeup_wealth(self, wealth: Wealth):
        for one in self.labels_check:
            extract_method = getattr(self, 'extract_' + one, None)
            if extract_method is not None and callable(extract_method):
                wealth = extract_method(self.text, wealth)
            else:
                self.log.error('没有找到相应的方法：extract_%s方法' % one)
        return wealth

    # 此方法开放给用户，ManualText的子类继承后，自定义使用
    def do_parse_text(self, wealth: Wealth):
        return wealth

    def final_makeup_wealth(self, wealth: Wealth):
        wkey = self.ukey
        wealth.wkey = wkey
        wealth.wkeyhash = farmhash.hash64(wkey)

        if not wealth.code:
            wealth.code = self.ukey.split('=')[-1]

        if not wealth.raise_type:
            wealth.raise_type = '公募'

        # 计算term, date_start, date_end
        if not wealth.term:
            if wealth.date_start and wealth.date_end:
                start = datetime.strptime(wealth.date_start, "%Y-%m-%d %H:%M:%S")
                end = datetime.strptime(wealth.date_end, "%Y-%m-%d %H:%M:%S")
                differs = end - start
                wealth.term = differs.days
        if not wealth.date_end:
            if wealth.date_start and wealth.term:
                start = datetime.strptime(wealth.date_start, "%Y-%m-%d %H:%M:%S")
                end = (start + timedelta(days=wealth.term)).strftime("%Y-%m-%d %H:%M:%S")
                wealth.date_end = end
        if not wealth.date_start:
            if wealth.date_end and wealth.term:
                end = datetime.strptime(wealth.date_end, "%Y-%m-%d %H:%M:%S")
                start = (end - timedelta(days=wealth.term)).strftime("%Y-%m-%d %H:%M:%S")
                wealth.date_start = start
            else:
                if wealth.date_close:
                    date_close = datetime.strptime(wealth.date_close, "%Y-%m-%d %H:%M:%S")
                    date_start = (date_close + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
                    wealth.date_start = date_start

        if not wealth.term:
            result = self.pattern_term_final.search(self.text)
            if result:
                wealth.term = '无固定期限'

        # 此处需要再检查一下，如找不到收益类型，则默认浮动收益，是否合适？
        #if not wealth.fixed_type:
        #    wealth.fixed_type = '浮动收益'

        fee_types = wealth.fee_types
        if fee_types:
            fee_rates = 0.0
            for rate in fee_types.values():
                fee_rates += rate
            fee_rates = round(fee_rates, 6)
            wealth.fee_rate = fee_rates

        wealth = self.do_parse_text(wealth)
        return wealth

    def extract_raise_period(self, value: str, wealth: Wealth):
        if not wealth.date_open or not wealth.date_close:
            results = self.pattern_raise_period.search(value)
            if results:
                text_date = results.group(0)
                list_date = find_datetimes(text_date)
                if list_date:
                    list_date.sort()
                    wealth.date_open = list_date[0]
                    wealth.date_close = list_date[-1]
        return wealth

    def extract_invest_period(self, value: str, wealth: Wealth):
        if not wealth.date_start or not wealth.date_end:
            results = self.pattern_invest_period.search(value)
            if results:
                text_date = results.group(0)
                list_data = find_datetimes(text_date)
                if list_data:
                    list_data.sort()
                    wealth.date_start = list_data[0]
                    wealth.date_end = list_data[-1]
        return wealth

    def extract_product_type(self, value: str, wealth: Wealth):
        if not wealth.redeem_type:
            if '封闭式' in value:
                wealth.redeem_type = '封闭式'
            elif '开放式' in value:
                wealth.redeem_type = '开放式'

        if not wealth.rate_type:
            if '净值型' in value:
                wealth.rate_type = '净值型'
                # wealth.promise_type = '非保本'
                wealth.fixed_type = '浮动收益'
            elif '预期收益型' in value:
                wealth.rate_type = '预期收益型'
            elif '结构性存款' in value:
                wealth.rate_type = '预期收益型'

        if not wealth.raise_type:
            if '公开募集' in value:
                wealth.raise_type = '公募'
            elif '私下募集' in value:
                wealth.raise_type = '私募'

        # 正则表达式搜索匹配
        result = self.pattern_product_type.search(value)
        if result:
            text = result.group(0)
            if not wealth.promise_type:
                if '非保本' in text:
                    wealth.promise_type = '非保本'
                elif '保本' in text:
                    wealth.promise_type = '保本'

            if not wealth.fixed_type:
                if '浮动' in text:
                    wealth.fixed_type = '浮动收益'
                elif '固定' in text:
                    wealth.fixed_type = '固定收益'
        return wealth

    def extract_amount_size(self, value: str, wealth: Wealth):
        return wealth


    def extract_name(self, value: str, wealth: Wealth):
        if not wealth.name:
            results = self.pattern_name.search(value)
            if results:
                name = results.group(1)
                wealth.name = name

                if not wealth.redeem_type:
                    if '封闭' in name:
                        wealth.redeem_type = '封闭式'
                    elif '开放' in name:
                        wealth.redeem_type = '开放式'

                if not wealth.rate_type:
                    if '净值' in name:
                        wealth.rate_type = '净值型'
                        # wealth.promise_type = '非保本'
                        wealth.fixed_type = '浮动收益'
                    elif '预期收益' in name:
                        wealth.rate_type = '预期收益型'
                    elif '结构性存款' in name:
                        wealth.rate_type = '预期收益型'

                if not wealth.raise_type:
                    if '公募' in name:
                        wealth.raise_type = '公募'
                    elif '私募' in name:
                        wealth.raise_type = '私募'

                if not wealth.promise_type:
                    if '非保本' in name:
                        wealth.promise_type = '非保本'
                    elif '保本' in name:
                        wealth.promise_type = '保本'

                self.extract_product_type(name, wealth)
        return wealth

    def extract_code(self, value: str, wealth: Wealth):
        if not wealth.code:
            result = self.pattern_code.search(value)
            if result:
                wealth.code = result.group(1)
        return wealth

    def extract_code_register(self, value: str, wealth: Wealth):
        if not wealth.code_register:
            result = self.pattern_code_register.search(value)
            if result:
                wealth.code_register = result.group(2)
        return wealth

    def extract_currency(self, value: str, wealth: Wealth):
        if not wealth.currency:
            result = self.pattern_currency.search(value)
            if result:
                wealth.currency = result.group(1)
        return wealth

    # 返回风险等级的数字表示
    def extract_risk(self, value: str, wealth: Wealth):
        if not wealth.risk:
            risk = None
            result = self.pattern_risk_cn.search(value)
            if result:
                risk_raw = result.group(1)
                for key in self.list_risk.keys():
                    if key == risk_raw:
                        risk = self.list_risk[key]
                        break
            if not risk:
                res = self.pattern_risk_dig.search(value)
                if res:
                    risk_raw = res.group(1)
                    res_num = re.search(r'[0-9]', risk_raw)
                    if res_num:
                        risk = res_num.group(0)
                        risk = int(risk)
                        if risk > 5:
                            self.log.error('风险评级数字超出范围，内容为：%s' % value)
                    else:
                        res_cn_num = re.search(r'[零一二三四五]', risk_raw)
                        if res_cn_num:
                            cn_num = res_cn_num.group(0)
                            risk = UTIL_CN_NUM[cn_num]
            if not risk:
                result = self.pattern_risk_cn_extra.search(value)
                if result:
                    risk_raw = result.group(1) + '风险'
                    for key in self.list_risk.keys():
                        if key == risk_raw:
                            risk = self.list_risk[key]
                            break

            wealth.risk = risk
        return wealth


    def extract_rate_max(self, value: str, wealth: Wealth):
        if not wealth.rate_max:
            results = self.pattern_rate.finditer(value)
            list_num = []
            for one in results:
                rate_type = one.group(1)
                if rate_type and not wealth.rate_type:
                    self.extract_rate_type(rate_type, wealth)

                rate_num = one.group(2)
                if rate_num:
                    rate_num = percent_to_num(rate_num + '%')
                    if rate_num < 0.15:
                        list_num.append(rate_num)
            if list_num:
                list_num.sort()
                wealth.rate_min = list_num[0]
                wealth.rate_max = list_num[-1]
        return wealth

    def extract_rate_min(self, value: str, wealth: Wealth):
        if not wealth.rate_min:
            results = self.pattern_rate.finditer(value)
            list_num = []
            for one in results:
                rate_type = one.group(1)
                if rate_type and not wealth.rate_type:
                    self.extract_rate_type(rate_type, wealth)

                rate_num = one.group(2)
                if rate_num:
                    rate_num = percent_to_num(rate_num + '%')
                    if rate_num < 0.15:
                        list_num.append(rate_num)
            if list_num:
                list_num.sort()
                wealth.rate_min = list_num[0]
                wealth.rate_max = list_num[-1]
        return wealth

    def extract_rate_type(self, value: str, wealth: Wealth):
        if not wealth.rate_type:
            result = self.pattern_rate_type.search(value)
            if result:
                rate_type = result.group(0)
                if rate_type == '比较业绩基准' or rate_type == '业绩比较基准' or rate_type == '业绩基准' or rate_type == '净值型':
                    wealth.rate_type = '净值型'
                    # wealth.promise_type = '非保本'
                    wealth.fixed_type = '浮动收益'
                if rate_type == '预期理财收益率' or rate_type == '预期年化收益率' or rate_type == '预期到期利率' or rate_type == '年化收益率' or rate_type == '预期收益率' or rate_type == '实现年化收益':
                    wealth.rate_type = '预期收益型'
                elif rate_type == '结构性存款':
                    wealth.rate_type = '预期收益型'
        return wealth

    def extract_redeem_type(self, value: str, wealth: Wealth):
        if not wealth.redeem_type:
            # 去除内容中关于赎回权利的如果，假设等语句
            value = self.pattern_redeem_type_sub.sub('', value)

            redeem_text = None
            result = self.pattern_redeem_type.search(value)
            if result:
                redeem_text = result.group(0)
            else:
                result = self.pattern_redeem_type_extra.search(value)
                if result:
                    redeem_text = result.group(0)
            if redeem_text:
                if '不' in redeem_text or '无' in redeem_text or '没' in redeem_text:
                    wealth.redeem_type = '封闭式'
                else:
                    wealth.redeem_type = '开放式'
        return wealth

    def extract_fixed_type(self, value: str, wealth: Wealth):
        return wealth

    def extract_promise_type(self, value: str, wealth: Wealth):
        if not wealth.promise_type:
            result = self.pattern_promise_type.search(value)
            if result:
                word = result.group(0)
                if word:
                    one_no = result.group(1)
                    two_no = result.group(2)
                    if one_no or two_no:
                        wealth.promise_type = '非保本'
                    else:
                        wealth.promise_type = '保本'
        return wealth

    def extract_raise_type(self, value: str, wealth: Wealth):
        return wealth

    def extract_date_open(self, value: str, wealth: Wealth):
        if not wealth.date_open:
            results = self.pattern_date_open.finditer(value)
            list_num = []
            for one in results:
                dtime = one.group(0)
                if dtime:
                    list_dtime = find_datetimes(dtime)
                    if list_dtime:
                        list_num.append(list_dtime[0])
            if list_num:
                list_num.sort()
                wealth.date_open = list_num[0]                  # 取最小的日期
        return wealth

    def extract_date_close(self, value: str, wealth: Wealth):
        if not wealth.date_close:
            results = self.pattern_date_close.finditer(value)
            list_num = []
            for one in results:
                dtime = one.group(0)
                if dtime:
                    list_dtime = find_datetimes(dtime)
                    if list_dtime:
                        list_num.append(list_dtime[0])
            if list_num:
                list_num.sort()
                wealth.date_close = list_num[-1]                # 取最大的日期
        return wealth

    def extract_date_start(self, value: str, wealth: Wealth):
        if not wealth.date_start:
            results = self.pattern_date_start.finditer(value)
            list_num = []
            for one in results:
                dtime = one.group(0)
                if dtime:
                    list_dtime = find_datetimes(dtime)
                    if list_dtime:
                        list_num.append(list_dtime[0])
            if list_num:
                list_num.sort()
                date_close = wealth.date_close
                if date_close:
                    for one in list_num:
                        if one >= date_close:               # 开始日期必须大于等于募集结束日期
                            wealth.date_start = one
                            break
                else:
                    wealth.date_start = list_num[0]
        return wealth

    def extract_date_end(self, value: str, wealth: Wealth):
        if not wealth.date_end:
            results = self.pattern_date_end.finditer(value)
            list_num = []
            for one in results:
                dtime = one.group(0)
                if dtime:
                    list_dtime = find_datetimes(dtime)
                    if list_dtime:
                        list_num.append(list_dtime[0])
            if list_num:
                list_num.sort()
                wealth.date_end = list_num[-1]             # 结束日期取集合中最大的一个日期
        return wealth

    # 理财期限应该在所有的包含年月日等date查找完，并从value中去除后，再查找
    def extract_term(self, value: str, wealth: Wealth):
        if not wealth.term:
            results = self.pattern_term.finditer(value)
            list_num = []
            for one in results:
                num = int(one.group(1))
                unit = one.group(2)
                if unit == '月':
                    num = num * 30
                elif unit == '年':
                    num = num * 365
                if num < 7301:              # 设定期限的最大值不能超过20年
                    list_num.append(num)
            if list_num:
                list_num.sort()
                wealth.term = list_num[0]       # 取list中期限日期最短的一个数字
        return wealth

    def extract_amount_size_min(self, value: str, wealth: Wealth):
        if not wealth.amount_size_min:
            result = self.pattern_amount_size_min.search(value)
            if result:
                text = result.group(1)
                num = transfer_to_yuan(text)
                wealth.amount_size_min = num
        return wealth

    def extract_amount_size_max(self, value: str, wealth: Wealth):
        if not wealth.amount_size_max:
            result = self.pattern_amount_size_max.search(value)
            if result:
                text = result.group(1)
                num = transfer_to_yuan(text)
                wealth.amount_size_max = num
        return wealth

    def extract_amount_buy_min(self, value: str, wealth: Wealth):
        if not wealth.amount_buy_min:
            results = self.pattern_amount_buy_min.finditer(value)
            list_num = []
            for one in results:
                num_text = one.group(2)
                unit = one.group(3)
                # print('找到的起购金额为：', (one.group(0)))
                if num_text and unit:
                    num = transfer_to_yuan(num_text + unit)
                    list_num.append(num)
            if list_num:
                list_num.sort()
                wealth.amount_buy_min = list_num[-1]
        return wealth

    def extract_amount_buy_max(self, value: str, wealth: Wealth):
        return wealth

    def extract_amount_per_buy(self, value: str, wealth: Wealth):
        if not wealth.amount_per_buy:
            results = self.pattern_amount_per_buy.finditer(value)
            list_num = []
            for one in results:
                num_text = one.group(0)
                if num_text:
                    num = transfer_to_yuan(num_text)
                    list_num.append(num)
            if list_num:
                list_num.sort()
                wealth.amount_per_buy = list_num[0]
        return wealth


    def extract_custodian(self, value: str, wealth: Wealth):
        if not wealth.custodian:
            name = None
            results = self.pattern_custodian.search(value)
            if results:
                name = results.group(3)
            else:
                res = self.pattern_custodian_extra.search(value)
                if res:
                    name = res.group(3)
            if name:
                name_simple = re.sub(r'[股份有限公司责任]+', '', name)
                if self.bank_name not in name_simple:  # 托管人为非本银行，才记录，否则默认为None
                    wealth.custodian = name_simple
        return wealth


    def extract_fee_types(self, value: str, wealth: Wealth):
        results = self.pattern_fee_types.finditer(value)
        fees = {}
        for one in results:
            name = one.group(1)
            amount = float(one.group(3))
            amount = round(amount / 100, 6)
            if amount < 0.01 and amount != 0.0:     # 设定一个检查值，即费率小于1%的，才加入fees字典中
                fees[name] = amount                 # 字典中如果key相同，则自动更新内容
        if len(fees) > 0:
            if not wealth.fee_types:
                wealth.fee_types = fees
            else:
                fees.update(wealth.fee_types)
                wealth.fee_types = fees
        return wealth

    def extract_fee_rate(self, value: str, wealth: Wealth):
        return wealth

    def extract_sale_areas(self, value: str, wealth: Wealth):
        return wealth

    def extract_sale_ways(self, value: str, wealth: Wealth):
        if not wealth.sale_ways:
            set_data = set()
            res = self.pattern_sale_ways.search(value)
            if res:
                value = res.group(0)

            results = self.pattern_sale_ways_extra.finditer(value)
            for one in results:
                data = one.group(0)
                if data:
                    if data == '网银' or data == '网上个人银行':
                        data = '网上银行'
                    if data == '掌上银行':
                        data = '手机银行'
                    if data == '现金管理平台':
                        data = '自助渠道'
                    if data == '营业网点' or data == '授权网点':
                        data = '网点柜面'
                    if data == '电子渠道':
                        data = '网上银行'
                        set_data.add('手机银行')
                    set_data.add(data)
            if len(set_data) > 0:
                wealth.sale_ways = list(set_data)
        return wealth

    def extract_sale_agents(self, value: str, wealth: Wealth):
        if not wealth.sale_agents:
            results = self.pattern_sale_agents.search(value)
            if results:
                wealth.sale_agents = results.group(2)
        return wealth

    def extract_invest_on(self, value: str, wealth: Wealth):
        if not wealth.invest_on:
            result = self.pattern_invest_on.search(value)
            if result:
                text = result.group(1)
                if len(text) > 100:
                    text = text[:100]
                wealth.invest_on = text
        return wealth

    def extract_loan_rule(self, value: str, wealth: Wealth):
        if not wealth.loan_rule:
            result = self.pattern_loan_rule.search(value)
            if result:
                text = result.group(0)
                if '不' in text or '无' in text or '没' in text:
                    wealth.loan_rule = 'NO'
                else:
                    wealth.loan_rule = 'YES'
        return wealth
