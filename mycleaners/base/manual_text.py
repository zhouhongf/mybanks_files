import re
from config.log import Logger
from config import CONFIG
import os
from utils.nlp_util import transfer_to_yuan
from mycleaners.base.wealth import Wealth
import farmhash
from constants import BankDict
from utils.nlp_util import UTIL_CN_NUM
from datetime import datetime, timedelta


class ManualText(object):
    # 从PDF等文件的文字内容中，提取符合正则表达式的内容，来补充之前在表格中提取的，然而未能提取到的内容
    log_path = os.path.join(CONFIG.LOG_DIR, 'ManualText.log')
    log = Logger(log_path, level='warning').logger

    # 如添加一个labels_check成员，则应相应的添加一个extract_开头的成员方法
    labels_check = {
        'product_type', 'fee_types', 'sale_ways',
        'risk',
        'rate_type', 'promise_type', 'redeem_type',
        'amount_buy_min', 'amount_per_buy',
        'invest_on', 'custodian',
    }
    # 如果只有一个wealth，则将下面这些也添加进labels_check中
    labels_check_one = {
        'name', 'code', 'code_register',
        'term', 'term_looped',
        'amount_size_min', 'amount_size_max',
    }

    # ！！！ManualText类中的正则表达式内容与ManualTable类中的正则表达式的内容是不同的
    pattern_product_type = re.compile(r'理财[计划]*产品类型[属于为是：:\s]*[非保本证固定浮动收益开放式封闭净值型类公私募]{5,}|本[期理财]*产品[属于为是：:\s]*[非保本证固定浮动收益开放式封闭净值型类公私募\s]{5,}[理财]*产品')
    pattern_fee_types = re.compile(r'([销售托管其他手续固定申认购投资]+(管理|服务)?费)[\s:：率为]*([0-9]+(\.[0-9]+)*)[%％][\s/每]*年')
    pattern_sale_ways = re.compile(r'(网点柜面|营业网点|授权网点|网银|网上银行|网上个人银行|手机银行|微信银行|电话银行|掌上银行|现金管理平台|自助渠道|电子渠道)+')

    pattern_risk_dig = re.compile(r'风险[评等分][级类][结果属于为是：:\s]*([0-9A-Za-z零一二三四五]+)级?')
    pattern_risk_cn = re.compile(r'风险[评等分][级类][结果属于为是：:\s]*[基本]*([无低较中等高极]+风险)')

    pattern_rate_type = re.compile(r'业绩比较基准|比较业绩基准|预期收益率|预期理财收益率|预期年化收益率|预期到期利率|净值型|结构性存款')
    pattern_promise_type = re.compile(r'([不无]?)[提供]*本金[完全]*保障|([不无]?)[保证障]{2}[理财购买资金]*[金额本]{2}')
    pattern_redeem_type_sub = re.compile(r'(如果|若|假设)[封闭期内投资理财计划成立后]*(投资者|投资人|客户)[不没]?(得|享有|开放|可以|可|能|能够|无|有)[提前]*赎回')
    pattern_redeem_type = re.compile(r'(投资者|投资人|客户)[不没]?(得|享有|开放|可以|可|能|能够|无|有)[提前]*赎回')

    pattern_amount_buy_min = re.compile(r'[起点份额认购金最低余申]{4,}[:：为不低于\s]*(人民币|美元|欧元|英镑|日元)*\s*([1-9][0-9]*)\s*([亿万千百元]+)起?')     # 仅能用于search()方法
    pattern_amount_per_buy = re.compile(r'[1-9][0-9]*[亿万千百美欧英镑日元份\s]+的?整数倍')

    # pattern_invest_on = re.compile(r'本[期]?理财[理财募集的资计划产品本金最终可]*投资于[：:\s]*([\u4e00-\u9fa5、，；;,（）\\(\\)A-Za-z0-9]+)。')
    pattern_invest_on = re.compile(r'本[期]?理财[理财募集的资计划产品本金最终可存续期间,，管人主要]*投资于[以下投资工具：:\s]*([\u4e00-\u9fa5、，；;,:：%％+\[\]（）()A-Za-z0-9\-]+)。')
    pattern_custodian = re.compile(r'本[投资产品理财计划的]+(托管)(人|单位|机构|银行)[为是：:\s]*([\u4e00-\u9fa5]+[农村商业城市银行股份有限公司]{2,})')

    pattern_name = re.compile(r'《([\u4e00-\u9fa5、，,:：“”"+\[\]\s（）()A-Za-z0-9\-]+)(风险揭示及说明书|产品说明书|协议书)》')
    pattern_code = re.compile(r'(产品|单元|理财|计划)[的认购]*[代码编号]{2}[为是：:\s]*([A-Za-z0-9][-+A-Za-z0-9]+)')
    pattern_code_register = re.compile(r'(登记|注册)[编码代号]+[为是：:\s]*([A-Za-z0-9]{6,})')
    pattern_term = re.compile(r'理财[计划]*期限[为是：:\s]*([0-9，,]+)\s*([天日月年])')
    pattern_term_sub = re.compile(r'([0-9]{2,4}年)?[0-9]{1,2}月[0-9]{1,2}日')

    pattern_amount_size_max = re.compile(r'理财[计划总发行运作]*规模上限[为是：:\s]*([1-9][0-9]*(\.[0-9]+)*[亿万千百美欧元英镑日\s]+)')
    pattern_amount_size_min = re.compile(r'理财[计划总发行运作]*规模下限[为是：:\s]*([1-9][0-9]*(\.[0-9]+)*[亿万千百美欧元英镑日\s]+)')

    list_risk = BankDict.list_risk
    list_currency = BankDict.list_currency
    list_ignore = ['ukey', 'wkey', 'wkeyhash', 'bank_name', 'name', 'code', 'do_dict_data']

    def __init__(self, bank_name: str, dict_wealth: dict, text: str):
        self.bank_name = bank_name
        self.dict_wealth = dict_wealth
        self.text = re.sub(r'[【】()（）/\s]+', '', text)

        config = getattr(self, 'labels_check_config', None)
        if config:
            if not isinstance(config, set):
                raise ValueError("labels_check_config must be type of set")
            self.labels_check.update(config)
        config_one = getattr(self, 'labels_check_one_config', None)
        if config_one:
            if not isinstance(config_one, set):
                raise ValueError("labels_check_one_config must be type of set")
            self.labels_check_one.update(config_one)

        self.wealth_codeless = None
        if len(self.dict_wealth) > 1:                                   # 如果传入的字典含有2个及以上的wealth, 并且其中含有一个codeless的wealth, 则去掉该codeless的wealth
            if 'codeless' in self.dict_wealth.keys():
                self.wealth_codeless = self.dict_wealth['codeless']     # 将codeless的wealth的临时保存再wealth_codeless实例变量中
                self.dict_wealth.pop('codeless')
        if len(self.dict_wealth) == 1:
            self.labels_check.update(self.labels_check_one)             # 如果传入的字典只含有1个wealth, 则设置为可以全文搜索补充所有的label的内容


    @classmethod
    def start(cls, bank_name: str, dict_wealth: dict, text: str):
        manual_text_in = cls(bank_name, dict_wealth, text)
        list_need = manual_text_in._start()
        return list_need

    def _start(self):
        list_wealth_new = []
        for wealth in self.dict_wealth.values():
            #if wealth.ukey == '工商银行=QDXT1845':
            #    print('想了解的wealth内容是：', wealth)

            wealth = self.makeup_wealth_table(self.text, wealth)
            list_wealth_new.append(wealth)
        list_need = self.final_makeup_wealth(list_wealth_new)
        return list_need

    def makeup_wealth_table(self, value: str, wealth: Wealth):
        for one in self.labels_check:
            extract_method = getattr(self, 'extract_' + one, None)
            if extract_method is not None and callable(extract_method):
                wealth = extract_method(value, wealth)
            else:
                self.log.error('没有找到相应的方法：extract_%s方法' % one)
        return wealth

    # 此方法开放给用户，ManualText的子类继承后，自定义使用
    def do_parse_text(self, wealth: Wealth):
        return wealth

    def final_makeup_wealth(self, list_wealth: list):
        # !!!! 过滤掉code为空值的wealth, 为wealth定义wkey和wkeyhash
        # 因为没有 产品名称、产品代码 开头的表格，已被并入上一表格中显示，
        # 如果文件中只有一张表格，则在manual_text中，将进行全文正则匹配，来寻找code
        # 所以如果仍未找到code, 则code为空值的wealth, 则可遗弃
        dict_need = {}
        for wealth in list_wealth:
            code = wealth.code
            if code:
                wkey = self.bank_name + '=' + code
                wealth.wkey = wkey
                wealth.wkeyhash = farmhash.hash64(wkey)

                if not wealth.raise_type:
                    wealth.raise_type = '公募'

                # 检查date_open
                if not wealth.date_open:
                    if wealth.date_start:
                        wealth.date_open = wealth.date_start

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

                # 此处需要再检查一下，如找不到收益类型，则默认浮动收益，是否合适？
                if not wealth.fixed_type:
                    wealth.fixed_type = '浮动收益'

                wealth = self.makeup_from_codeless(wealth, self.wealth_codeless)
                wealth = self.do_parse_text(wealth)

                dict_need[code] = wealth
        return dict_need

    def makeup_from_codeless(self, wealth: Wealth, wealth_codeless: Wealth):
        wealth_instance_elements = [one for one in dir(wealth) if not (one.startswith('__') or one.startswith('_') or (one in self.list_ignore))]
        for element in wealth_instance_elements:
            codeless_element = getattr(wealth_codeless, element, None)
            current_element = getattr(wealth, element, None)
            if not current_element:
                if codeless_element:
                    setattr(wealth, element, codeless_element)
        return wealth

    def extract_product_type(self, value: str, wealth: Wealth):
        # 全文关键字匹配
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

    def extract_fee_types(self, value: str, wealth: Wealth):
        results = self.pattern_fee_types.finditer(value)
        fees = {}
        fee_rate = 0.0
        for one in results:
            name = one.group(1)
            amount = float(one.group(3))
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

    def extract_sale_ways(self, value: str, wealth: Wealth):
        if wealth.sale_ways:
            set_data = set(wealth.sale_ways)
        else:
            set_data = set()

        results = self.pattern_sale_ways.finditer(value)
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
            wealth.risk = risk
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
                if rate_type == '预期理财收益率' or rate_type == '预期年化收益率' or rate_type == '预期到期利率' or rate_type == '年化收益率' or rate_type == '预期收益率':
                    wealth.rate_type = '预期收益型'
                elif rate_type == '结构性存款':
                    wealth.rate_type = '预期收益型'
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

    def extract_amount_buy_min(self, value: str, wealth: Wealth):
        if not wealth.amount_buy_min:
            results = self.pattern_amount_buy_min.search(value)
            if results:
                text = results.group(0)
                num = transfer_to_yuan(text)
                wealth.amount_buy_min = num
        return wealth

    def extract_amount_per_buy(self, value: str, wealth: Wealth):
        if not wealth.amount_per_buy:
            result = self.pattern_amount_per_buy.search(value)
            if result:
                one = result.group(0)
                num = transfer_to_yuan(one)
                wealth.amount_per_buy = num
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

    def extract_redeem_type(self, value: str, wealth: Wealth):
        if not wealth.redeem_type:
            # 去除内容中关于赎回权利的如果，假设等语句
            value = self.pattern_redeem_type_sub.sub('', value)

            result = self.pattern_redeem_type.search(value)
            if result:
                text = result.group(0)
                if '不' in text or '无' in text or '没' in text:
                    wealth.redeem_type = '封闭式'
                else:
                    wealth.redeem_type = '开放式'
        return wealth

    def extract_custodian(self, value: str, wealth: Wealth):
        if not wealth.custodian:
            results = self.pattern_custodian.search(value)
            if results:
                text = results.group(3)
                if text:
                    text = re.sub(r'[股份有限公司责任]+', '', text)
                    if self.bank_name not in text:                  # 托管人为非本银行，才记录，否则默认为None
                        wealth.custodian = text
        return wealth



    def extract_name(self, value: str, wealth: Wealth):
        if not wealth.name:
            results = self.pattern_name.findall(value)         # 全文搜索带书名号的文字，选择最长的作为name, 需要考虑是否合适？
            if results:
                word_longest = ''
                for one in results:
                    name_raw = one[0]
                    name_net = name_raw.replace('结构性存款', '')
                    if len(name_net) > 0:
                        if len(name_raw) > len(word_longest):
                            word_longest = name_raw
                wealth.name = word_longest
                # print('extract_name中的wealth.name是：%s' % wealth.name)
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

    def extract_term(self, value: str, wealth: Wealth):
        if not wealth.term:
            # 去除value单元格中XX年XX月XX日格式的文字
            res = self.pattern_term_sub.finditer(value)
            for one in res:
                date = one.group(0)
                value = value.replace(date, '')

            # 查找数量的年、月、日
            result = self.pattern_term.search(value)
            if result:
                num = result.group(1)
                num = num.replace(',', '')
                num = num.replace('，', '')
                num = int(num)

                unit = result.group(2)
                if unit == '月':
                    num = num * 30
                elif unit == '年':
                    num = num * 365
                if num < 7301:              # 设定期限的最大值不能超过20年
                    wealth.term = num
        return wealth

    def extract_term_looped(self, value: str, wealth: Wealth):
        if not wealth.term_looped:
            if '投资周期顺延' in value or '自动再投资' in value or '无固定期限' in value:
                wealth.term_looped = 'YES'
        return wealth

    def extract_amount_size_max(self, value: str, wealth: Wealth):
        result = self.pattern_amount_size_max.search(value)
        if result:
            text = result.group(1)
            num = transfer_to_yuan(text)
            if not wealth.amount_size_max:
                wealth.amount_size_max = num
                return wealth

            if num > wealth.amount_size_max:
                wealth.amount_size_max = num
        return wealth

    def extract_amount_size_min(self, value: str, wealth: Wealth):
        result = self.pattern_amount_size_min.search(value)
        if result:
            text = result.group(1)
            num = transfer_to_yuan(text)
            if not wealth.amount_size_min:
                wealth.amount_size_min = num
                return wealth

            if num < wealth.amount_size_min:
                wealth.amount_size_min = num
        return wealth

