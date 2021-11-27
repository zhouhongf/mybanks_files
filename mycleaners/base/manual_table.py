import re
from config.log import Logger
from config import CONFIG
import os
from utils.nlp_util import find_datetimes, transfer_to_yuan, percent_to_num
from mycleaners.base.wealth import Wealth
from constants import BankDict
from utils.nlp_util import UTIL_CN_NUM


class ManualTable(object):
    log_path = os.path.join(CONFIG.LOG_DIR, 'ManualTable.log')
    log = Logger(log_path, level='warning').logger

    # 理财产品说明书布局 的思考：
    # 1、一般来说，表格为母表的，含有基础内容，表格为其子表，含有补充内容
    # 2、子理财产品的名称为母理财产品的名称或名称简称，再加上 第XX期  XX天型

    table_labels = {
        'raise_period': {'募集期', '发行期', '认购期', '申购期', '开放期'},
        'product_type': {'产品类型', '收益类型', '存款类型'},
        'amount_size': {'募集金额', '募集规模', '产品规模', '产品额度', '产品购买', '发行规模', '开放规模', '认购规模', '发售规模', '计划规模', '计划发行量'},

        'name': {'名称'},
        'code': {'产品编码', '产品代码', '认购编号', '单元代码', '销售编号'},
        'code_register': {'登记编码'},
        'risk': {'风险等级', '风险分级', '风险分类', '风险评级', '产品评级', '风险评定'},
        'currency': {'币种'},

        'rate_max': {},
        'rate_min': {'固定收益率'},
        'rate_type': {'业绩基准', '比较基准', '理财收益率', '理财收益', '利息', '预期收益率', '年化收益率', '净值', '预期收益', '年化净收益率', '结构性存款', '参考收益率', '参考净收益率', '参照收益率'},

        'redeem_type': {'赎回'},

        'fixed_type': {'固定收益', '浮动收益'},
        'promise_type': {'保本', '非保本'},
        'raise_type': {'募集方式', '发行方式'},

        'date_open': {'申购日', '认购日'},
        'date_close': {},
        'date_start': {'扣款日', '起息日', '成立日', '开始日', '起始日', '起算日'},
        'date_end': {'到期日', '终止日', '结束日'},
        'term': {'计算天数', '理财期限', '计划期限', '周期天数', '存款期限', '产品期限', '投资周期', '投资期限', '持有期'},
        'term_looped': {'投资周期顺延', '自动再投资'},

        'amount_size_min': {},
        'amount_size_max': {},
        'amount_buy_min': {'认购起点', '认购份额', '认购金额', '申购起点', '申购份额', '申购金额', '单笔认购', '起存金额', '起点金额', '起购金额'},
        'amount_buy_max': {'认购上限', '申购上限'},
        'amount_per_buy': {},

        'custodian': {'托管人', '托管机构', '托管银行', '托管单位'},
        'fee_types': {'费用', '费率', '销售费', '销售手续费', '托管费', '固定管理费', '保管费', '赎回费'},
        'fee_rate': {},

        'sale_areas': {'销售地区', '销售范围'},
        'sale_ways': {'购买渠道', '购买方式', '销售渠道'},
        'sale_agents': {},


        'loan_rule': {'质押条款', '融资服务'},
        'invest_on': {'投资范围', '投资目标'},
    }

    # 用户也可以在cleaner子类中，重新写一个ManualTable类的子类，根据具体情况，重写以下正则表达式
    pattern_code = re.compile(r'[内部产品代码编号为是：:\s]*([A-Za-z0-9][-+A-Za-z0-9]+)')
    pattern_code_in_name = re.compile(r'[代码编号]{2,}[为是：:\s]*([A-Za-z0-9][-+A-Za-z0-9]+)')
    pattern_code_register = re.compile(r'[A-Z0-9]{6,}')
    pattern_code_register_in_name = re.compile(r'(登记|注册)[编码代号]+[为是：:\s]*([A-Za-z0-9]{6,})')

    pattern_risk_dig = re.compile(r'([0-9A-Za-z零一二三四五]+)级?')
    pattern_risk_cn = re.compile(r'[无低极较中等高]+风险')

    pattern_term = re.compile(r'([0-9，,]+)个?([天日月年])')
    pattern_term_sub = re.compile(r'([0-9]{2,4}年)?[0-9]{1,2}月[0-9]{1,2}日')

    pattern_rate = re.compile(r'[0-9]+\.?[0-9]*[%％]|[0-9]+\.[0-9]+')      # 带%号的，可以为整数或小数，不带%号的，则必须为小数格式
    pattern_rate_extra = re.compile(r'([0-9]+\.?[0-9]*)[%％]?\+([0-9]+\.?[0-9]*)[%％]')   # 带+号的，最高最低利率区间需要自己再计算一下
    pattern_rate_type = re.compile(r'业绩比较基准|比较业绩基准|预期收益率|预期理财收益率|预期年化收益率|预期到期利率|年化收益率|净值')

    pattern_promise_type = re.compile(r'([不无]?)[提供]*本金[完全]*保障|([不无]?)[保证障]{2}[理财购买资金]*[金额本]{2}')


    pattern_redeem_type_sub = re.compile(r'(如果|若|假设)[封闭期内投资理财计划成立后]*(投资者|投资人|客户)[不没]?(得|享有|开放|可以|可|能|能够|无|有|接受)[提前]*赎回')
    pattern_redeem_type = re.compile(r'(投资者|投资人|客户)[不没]?(得|享有|开放|可以|可|能|能够|无|有|接受)[提前]*赎回|本[理财产品计划投资]{2,}[在产品到期日之前封闭内]*[不没]?(对|得|享有|开放|可以|可|能|能够|无|有|接受)[\u4e00-\u9fa5]*赎回')
    pattern_redeem_type_extra = re.compile(r'[存续封闭期内投资理财计划成立后]*[不没]?(得|享有|开放|可以|可|能|能够|无|有|接受)[提前申购和与或]*赎回')
    # pattern_redeem_type = re.compile(r'[投资者人客户产品理财计划]*不?[提供得享没有开放可以能够无]*[申购和与提前]*赎回')

    pattern_amount = re.compile(r'[1-9][0-9]*(\.[0-9]+)*[亿万千百美欧元英镑日\s]+')
    pattern_amount_size_min = re.compile(r'[理财产品初始]{2,}[计划总发行认购最大运作]*[规模量额度]{1,}下限[为是：:\s]*([1-9][0-9]*(\.[0-9]+)*[亿万千百美欧元英镑日\s]+)')
    pattern_amount_size_max = re.compile(r'[理财产品初始]{2,}[计划总发行认购最大运作]*[规模量额度]{1,}[上限为是：:\s]*([1-9][0-9]*(\.[0-9]+)*[亿万千百美欧元英镑日\s]+)')

    # pattern_amount_buy_min = re.compile(r'(不低于|起点|起点份额|认购金额|最低余额|申购金额)[:\s：为]*(人民币|美元|欧元|英镑|日元)*[1-9][0-9]*[\s亿万千美欧元英镑日]+|[1-9][0-9]*[\s亿万千美欧元英镑日]+起')   # 仅能用于search()方法
    pattern_amount_buy_min = re.compile(r'[不低于起点认购金最余申份额]+[:\s：为]*(人民币|美元|欧元|英镑|日元)*[1-9][0-9]*[\s亿万千百美欧元英镑日]+|[1-9][0-9]*[\s亿万千百美欧元英镑日]+起')
    pattern_amount_buy_max = re.compile(r'上限[:\s：为是]*(人民币|美元|欧元|英镑|日元)*([1-9][0-9]*[\s亿万千百美欧元英镑日]+)')
    pattern_amount_per_buy = re.compile(r'[1-9][0-9]*[亿万千百美欧英镑日元份人民币\s]+的?整数倍|以[1-9][0-9]*[亿万千百美欧英镑日元份人民币\s]递增')

    # 托管人一般为非本银行的其他银行
    pattern_custodian_one = re.compile(r'(托管)(人|单位|机构|银行)[为是：:\s]*([\u4e00-\u9fa5]+[农村商业城市银行股份有限公司]{2,})')
    pattern_custodian_two = re.compile(r'[\u4e00-\u9fa5]+[农村商业城市银行股份有限公司]{2,}')
    # pattern_fee_types = re.compile(r'([销售托管理其他手续固定认购]+费)[\s:：率为]*([0-9]+(\.[0-9]+)*%)[/每年]*')
    pattern_fee_types = re.compile(r'([销售托管其他手续固定申认购投资]+(管理|服务)?费)[\s:：率标准为]*([0-9]+(\.[0-9]+)*)[%％][\s/每年]*')
    pattern_fee_types_names = re.compile(r'[销售托管其他手续固定申认购投资]+(管理|服务)?费')
    pattern_sale_ways = re.compile(r'(网点柜面|营业网点|授权网点|网银|网上银行|网上个人银行|手机银行|微信银行|电话银行|掌上银行|现金管理平台|自助渠道|电子渠道)+')

    pattern_invest_on = re.compile(r'投资于[：:\s]*([\u4e00-\u9fa5、，；;,（）\\(\\)A-Za-z0-9]+)。')

    list_risk = BankDict.list_risk
    list_currency = BankDict.list_currency
    list_ignore = ['ukey', 'wkey', 'wkeyhash', 'bank_name', 'name', 'code', 'do_dict_data']

    # 如果实例化时，传入了自定义的table_labels字典，则将其更新至类属性table_labels当中，
    # table_labels字典中key对应的value将发生变化
    def __init__(self, bank_name: str, bank_level: str, ukey: str, tables: list):
        self.bank_name = bank_name
        self.bank_level = bank_level
        self.ukey = ukey
        self.tables = tables
        config = getattr(self, 'table_labels_config', None)
        if config:
            if not isinstance(config, dict):
                raise ValueError("table_labels_config must be type of dict")
            self.table_labels.update(config)

    @classmethod
    def start(cls, bank_name: str, bank_level: str, ukey: str, tables: list):
        print('开始解析:', ukey)
        #if ukey == '江苏银行=1903007FA544':
        #    print('tables有：', tables)
        manual_table_in = cls(bank_name, bank_level, ukey, tables)
        dict_wealth = manual_table_in._start()
        return dict_wealth

    def _start(self):
        dict_wealth = {}                                                    # dict_wealth的key为code, value为wealth实例
        last_wealth = Wealth(ukey='last', bank_level=self.bank_level)       # 生成一个last_wealth实例，用于保存上一张表格的信息
        for table in self.tables:
            wealth = Wealth(ukey=self.ukey, bank_level=self.bank_level)
            for row in table:
                label = re.sub(r'[【】()（）《》\s]+', '', row[0])
                value = re.sub(r'[【】()（）《》\s]+', '', row[1])          # ！！！去掉value中的一些特殊字符，以减少后期正则匹配的难度

                wealth = self.parse_row(label, value, wealth)

            # 根据table中的内容，补充wealth
            wealth = self.makeup_wealth(wealth, table)

            # 正常情况下，应对一张table中只有一个wealth的情形，解析每个table中的row时，
            # 如果存在wealth的code，则将该wealth添加到dict_wealth字典中
            # 如果不存在wealth的code, 则将code默认设置为codeless，然后将wealth添加到dict_wealth字典中，
            # 以防止该文件中只有一张table，并且该table只存在一个不含有code的wealth情况的出现

            # 此处插入自定义解析方法do_parse_table()
            wealth = self.do_parse_table(wealth, table)
            # 比较last_wealth和wealth,
            # 如果last_wealth当中没有wealth的内容，则用wealth更新last_wealth，
            # 如果wealth中缺少内容，则从last_wealth中获取
            wealth = self.compare_last_wealth(last_wealth, wealth)
            # 所以，如果一个文件中存在2张具有相同code的表格，则后一个wealth最终会具有最为完整的内容，前一个wealth可以被更新为后一个wealth
            if wealth.code:
                dict_wealth[wealth.code] = wealth
            else:
                dict_wealth['codeless'] = wealth
        return dict_wealth

    def makeup_wealth(self, wealth: Wealth, table: list):
        for row in table:
            label = row[0]
            if '封闭' in label:
                wealth.redeem_type = '封闭式'

        return wealth

    # 此方法开放给用户，ManualTable的子类继承后，自定义使用
    def do_parse_table(self, wealth: Wealth, table: list):
        return wealth

    def parse_row(self, label: str, value: str, wealth: Wealth):
        for k, v in self.table_labels.items():
            # 遍历对应key的所有的value值，如果有value值存在于label中，则应用解析方法，去取值
            for one in v:
                if one in label:
                    extract_method = getattr(self, 'extract_' + k, None)
                    if extract_method is not None and callable(extract_method):
                        wealth = extract_method(label, value, wealth)
                    else:
                        self.log.error('没有找到相应的方法：extract_%s方法' % k)
        return wealth

    # 比较last_wealth和当前的wealth
    # (1) 挑选出wealth中需要更新的实例元素，去除内置元素和内置方法，去除不需要比较的元素，放入wealth_instance_elements集合中
    # (2) 遍历wealth_instance_elements集合
    # (3) 如果wealth的元素current_element的值存在，则将last_wealth中的element的值设置为current_element的值
    # (4) 如果wealth的元素current_element的值不存在，相反，如果last_wealth的元素last_element存在值，则将wealth的current_element设置为last_element的值
    def compare_last_wealth(self, last_wealth: Wealth, wealth: Wealth):
        wealth_instance_elements = [one for one in dir(wealth) if not (one.startswith('__') or one.startswith('_') or (one in self.list_ignore))]
        for element in wealth_instance_elements:
            last_element = getattr(last_wealth, element, None)
            current_element = getattr(wealth, element, None)
            if current_element:
                setattr(last_wealth, element, current_element)
            else:
                if last_element:
                    setattr(wealth, element, last_element)
        return wealth

    def extract_raise_period(self, label: str, value: str, wealth: Wealth):
        print('【raise_period标签：%s, 解析：%s】' % (label, value))
        # 解析募集期标签，一般来说都有2个日期，为募集起始日和募集结束日，
        # 因此，只要有一个日期有值了，则直接返回
        if wealth.date_open or wealth.date_close:
            return wealth

        list_datetimes = find_datetimes(value)
        if list_datetimes:
            wealth.date_open = list_datetimes[0]
            wealth.date_close = list_datetimes[-1]

        wealth = self.extract_amount_size_max(label, value, wealth)
        wealth = self.extract_amount_size_min(label, value, wealth)
        return wealth

    def extract_product_type(self, label: str, value: str, wealth: Wealth):
        # 直接搜索关键字
        # print('product_type【标签】：%s, 【解析内容】：%s' % (label, value))
        if not wealth.promise_type:
            if '非保本' in value:
                wealth.promise_type = '非保本'
            elif '保本' in value:
                wealth.promise_type = '保本'

        if not wealth.fixed_type:
            if '浮动' in value:
                wealth.fixed_type = '浮动收益'
            elif '固定' in value:
                wealth.fixed_type = '固定收益'

        if not wealth.redeem_type:
            if '封闭' in value:
                wealth.redeem_type = '封闭式'
            elif '开放' in value:
                wealth.redeem_type = '开放式'

        if not wealth.rate_type:
            if '净值' in value:
                wealth.rate_type = '净值型'
                # wealth.promise_type = '非保本'
                wealth.fixed_type = '浮动收益'
            elif '预期收益' in value:
                wealth.rate_type = '预期收益型'
            elif '结构性存款' in value:
                wealth.rate_type = '预期收益型'

        if not wealth.raise_type:
            if '公募' in value:
                wealth.raise_type = '公募'
            elif '公开募集' in value:
                wealth.raise_type = '公募'
            elif '私募' in value:
                wealth.raise_type = '私募'
            elif '私下募集' in value:
                wealth.raise_type = '私募'

        if '保证收益' in value:
            wealth.promise_type = '保本'

        # 使用正则表达式匹配 业绩比较基准 或 预期收益率
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

    def extract_amount_size(self, label: str, value: str, wealth: Wealth):
        #（1）过滤掉value中的逗号
        value = re.sub('[,，]+', '', value)
        list_amount = []

        #（2）用fullmatch匹配一下，是否是纯数字，如果是，再检查一下label中是否存在单位，如有单位，则换算成数字
        pattern_num = re.compile(r'[0-9]+(\.[0-9]+)*')
        res_value = pattern_num.fullmatch(value)
        if res_value:
            num = res_value.group(0)
            pattern_unit = re.compile(r'[亿万]')
            res_label = pattern_unit.search(label)
            if res_label:
                unit = res_label.group(0)
                amount = transfer_to_yuan(num + unit)
            else:
                amount = int(float(num))
            if amount > 1000000:                     # 募集金额低于100万的自动过滤掉
                list_amount.append(amount)

        #（3）遍历搜索value中带单位的数字
        results = self.pattern_amount.finditer(value)
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

    # 总是更新
    def extract_name(self, label: str, value: str, wealth: Wealth):
        wealth.name = value

        result = self.pattern_code_in_name.search(value)
        if result:
            wealth.code = result.group(1)

        res = self.pattern_code_register_in_name.search(value)
        if res:
            wealth.code_register = res.group(2)

        wealth = self.extract_product_type(label, value, wealth)
        return wealth

    # 总是更新
    def extract_code(self, label: str, value: str, wealth: Wealth):
        result = self.pattern_code.search(value)
        if result:
            wealth.code = result.group(1)
        return wealth

    # 总是更新
    def extract_code_register(self, label: str, value: str, wealth: Wealth):
        result = self.pattern_code_register.search(value)
        if result:
            wealth.code_register = result.group(0)
        return wealth

    def extract_currency(self, label: str, value: str, wealth: Wealth):
        if not wealth.currency:
            for one in self.list_currency:
                if one in value:
                    wealth.currency = one
                    break
        return wealth

    # 返回风险等级的数字表示
    def extract_risk(self, label: str, value: str, wealth: Wealth):
        # print('【risk标签：%s, 解析：%s】' % (label, value))
        if not wealth.risk:
            risk = None
            result = self.pattern_risk_cn.search(value)
            if result:
                risk_raw = result.group(0)
                # print('risk_raw1是：', risk_raw)
                for key in self.list_risk.keys():
                    if key == risk_raw:
                        risk = self.list_risk[key]
                        break
            if not risk:
                res = self.pattern_risk_dig.search(value)
                if res:
                    risk_raw = res.group(1)
                    # print('risk_raw2是：', risk_raw)
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

    def extract_rate_max(self, label: str, value: str, wealth: Wealth):
        return wealth

    def extract_rate_min(self, label: str, value: str, wealth: Wealth):
        res = self.pattern_rate_extra.search(value)
        if res:
            rate_base = res.group(1)
            rate_add = res.group(2)

            num_base = float(rate_base) / 100
            num_base = round(num_base, 6)
            num_add = float(rate_add) / 100
            num_ceil = num_base + num_add
            num_ceil = round(num_ceil, 6)

            wealth.rate_min = num_base
            wealth.rate_max = num_ceil
            return wealth

        result = self.pattern_rate.search(value)
        if result:
            word = result.group(0)
            if word:
                num = percent_to_num(word)
                if num < 0.1:
                    wealth.rate_min = num
                else:
                    self.log.error('收益率超过0.1，解析出来的num为：%s' % str(num))
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

        res = self.pattern_rate_extra.search(value)
        if res:
            rate_base = res.group(1)
            rate_add = res.group(2)

            num_base = float(rate_base) / 100
            num_base = round(num_base, 6)
            num_add = float(rate_add) / 100
            num_ceil = num_base + num_add
            num_ceil = round(num_ceil, 6)

            wealth.rate_min = num_base
            wealth.rate_max = num_ceil
            return wealth

        list_data = []
        results = self.pattern_rate.finditer(value)
        for one in results:
            word = one.group(0)
            if word:
                num = percent_to_num(word)
                if num < 0.1:
                    list_data.append(num)
                else:
                    self.log.error('收益率超过0.15，解析出来的num为：%s' % str(num))
        if len(list_data) > 0:
            list_data.sort(reverse=True)
            wealth.rate_max = list_data[0]
            wealth.rate_min = list_data[-1]
        return wealth

    def extract_redeem_type(self, label: str, value: str, wealth: Wealth):
        if not wealth.redeem_type:
            value = self.pattern_redeem_type_sub.sub('', value)         # 去除内容中关于赎回权利的如果，假设等语句
            value = re.sub(r'[投资者人客户申购买认]+', '', value)         # 去除内容中类似投资人，购买者，认购者，申购者等名词

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

    def extract_fixed_type(self, label: str, value: str, wealth: Wealth):
        return wealth

    def extract_promise_type(self, label: str, value: str, wealth: Wealth):
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

    def extract_raise_type(self, label: str, value: str, wealth: Wealth):
        if '公募' in value:
            wealth.raise_type = '公募'
        elif '公开募集' in value:
            wealth.raise_type = '公募'
        elif '私募' in value:
            wealth.raise_type = '私募'
        elif '私下募集' in value:
            wealth.raise_type = '私募'
        return wealth

    def extract_date_open(self, label: str, value: str, wealth: Wealth):
        if not wealth.date_open:
            list_datetimes = find_datetimes(value)
            if list_datetimes:
                wealth.date_open = list_datetimes[0]
        return wealth

    def extract_date_close(self, label: str, value: str, wealth: Wealth):
        if not wealth.date_close:
            list_datetimes = find_datetimes(value)
            if list_datetimes:
                wealth.date_close = list_datetimes[0]
        return wealth

    def extract_date_start(self, label: str, value: str, wealth: Wealth):
        if not wealth.date_start:
            list_datetimes = find_datetimes(value)
            if list_datetimes:
                wealth.date_start = list_datetimes[0]
        return wealth

    def extract_date_end(self, label: str, value: str, wealth: Wealth):
        if not wealth.date_end:
            list_datetimes = find_datetimes(value)
            if list_datetimes:
                wealth.date_end = list_datetimes[0]
        return wealth

    def extract_term(self, label: str, value: str, wealth: Wealth):
        if not wealth.term:
            # 检查value单元格是否为纯数字，若是，则再检查label标签中是否有单位，如有单位，则转换为天数后返回
            pattern_num = re.compile(r'[0-9，,]+')
            res_value = pattern_num.fullmatch(value)
            if res_value:
                num = res_value.group(0)
                num = num.replace(',', '')
                num = num.replace('，', '')
                num = int(num)

                pattern_unit = re.compile(r'[天日月年]')
                res_label = pattern_unit.search(label)
                if res_label:
                    unit = res_label.group(0)
                    if unit == '月':
                        num = num * 30
                    elif unit == '年':
                        num = num * 365
                    if num < 7301:
                        wealth.term = num
                    return wealth

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

        # 检查是否是循环理财
        if not wealth.term_looped:
            if '投资周期顺延' in value or '自动再投资' in value or '无固定期限' in value:
                wealth.term_looped = 'YES'
        return wealth

    def extract_term_looped(self, label: str, value: str, wealth: Wealth):
        if not wealth.term_looped:
            if '投资周期顺延' in label or '自动再投资' in label:
                wealth.term_looped = 'YES'
        return wealth

    def extract_amount_size_min(self, label: str, value: str, wealth: Wealth):
        if not wealth.amount_size_min:
            results = self.pattern_amount_size_min.search(value)
            if results:
                amount = results.group(1)
                num = transfer_to_yuan(amount)
                wealth.amount_size_min = num
        return wealth

    def extract_amount_size_max(self, label: str, value: str, wealth: Wealth):
        if not wealth.amount_size_max:
            results = self.pattern_amount_size_max.search(value)
            if results:
                amount = results.group(1)
                num = transfer_to_yuan(amount)
                wealth.amount_size_max = num
        return wealth

    def extract_amount_buy_min(self, label: str, value: str, wealth: Wealth):
        value = re.sub('[,，]+', '', value)

        # 查找匹配amount_per_buy
        if not wealth.amount_per_buy:
            result = self.pattern_amount_per_buy.search(value)
            if result:
                one = result.group(0)
                wealth.amount_per_buy = transfer_to_yuan(one)

        # 此处的value为已经全部去掉“XXX万元的整数倍”文字后的内容
        value = self.pattern_amount_per_buy.sub('', value)

        # 用match匹配一下，是否是纯数字
        if not wealth.amount_buy_min:
            num = None
            res_value = re.fullmatch(r'[0-9]+(\.[0-9]+)*', value)
            if res_value:
                num = res_value.group(0)
                # 如果是，再检查一下label中是否存在单位，如有单位，则换算成数字
                res_label = re.search(r'[亿万]', label)
                if res_label:
                    unit = res_label.group(0)
                    num = transfer_to_yuan(num + unit)
                else:
                    num = int(num)
            else:
                # 如果不是纯数字，则使用带文字的pattern_amount_buy_min正则表达式去匹配
                res = self.pattern_amount_buy_min.search(value)
                if res:
                    one = res.group(0)
                    num = transfer_to_yuan(one)
                else:
                    # 如果未匹配到，则使用pattern_amount找出所有的金额数字，取最小值为amount_buy_min的数值
                    results = self.pattern_amount.finditer(value)
                    list_results = []
                    for one in results:
                        amount = one.group(0)
                        if amount:
                            num = transfer_to_yuan(amount)
                            list_results.append(num)
                    if len(list_results) > 0:
                        list_results.sort(reverse=True)
                        num = list_results[-1]                      # 找出value单元格中最小的数字，将其设置为amount_buy_min的数值

            # 起购金额最低设置为1万, 并且不得超过amount_size_min或amount_size_max
            if num and num >= 10000:
                if wealth.amount_size_min:
                    if num > wealth.amount_size_min:
                        return wealth
                if wealth.amount_size_max:
                    if num > wealth.amount_size_max:
                        return wealth
                wealth.amount_buy_min = num
        return wealth

    def extract_amount_buy_max(self, label: str, value: str, wealth: Wealth):
        if not wealth.amount_buy_max:
            results = self.pattern_amount_buy_max.search(value)
            if results:
                amount = results.group(2)
                if amount:
                    num = transfer_to_yuan(amount)

                    if wealth.amount_size_min:
                        if num > wealth.amount_size_min:
                            return wealth
                    if wealth.amount_size_max:
                        if num > wealth.amount_size_max:
                            return wealth

                    wealth.amount_buy_max = num
        return wealth

    def extract_amount_per_buy(self, label: str, value: str, wealth: Wealth):
        if not wealth.amount_per_buy:
            result = self.pattern_amount_per_buy.search(value)
            if result:
                one = result.group(0)
                num = transfer_to_yuan(one)
                wealth.amount_per_buy = num
        return wealth

    def extract_custodian(self, label: str, value: str, wealth: Wealth):
        text = None
        results = self.pattern_custodian_one.search(value)
        if results:
            text = results.group(3)
        else:
            result = self.pattern_custodian_two.search(value)
            if result:
                text = result.group(0)
        if text:
            text = re.sub(r'[股份有限公司责任]+', '', text)
            if self.bank_name not in text:                                  # 托管人为非本银行，才记录，否则默认为None
                wealth.custodian = text
        return wealth

    def extract_fee_types(self, label: str, value: str, wealth: Wealth):
        # （1）单元格中为：文字内容+百分比
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

        # （2）单元格中为：百分比或数字， label中匹配专有费用名称
        res_num = self.pattern_rate.fullmatch(value)        # 使用fullmatch匹配全部单元格内容
        if res_num:
            fee = res_num.group(0)
            amount = percent_to_num(fee)
            if 0.0 < amount < 0.01:
                res_label = self.pattern_fee_types_names.search(label)
                if res_label:
                    name = res_label.group(0)
                    fees[name] = amount
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

    def extract_fee_rate(self, label: str, value: str, wealth: Wealth):
        return wealth

    def extract_sale_areas(self, label: str, value: str, wealth: Wealth):
        wealth.sale_areas = value.strip()
        return wealth

    def extract_sale_ways(self, label: str, value: str, wealth: Wealth):
        results = self.pattern_sale_ways.finditer(value)
        set_data = set()
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

    def extract_sale_agents(self, label: str, value: str, wealth: Wealth):
        return wealth

    def extract_loan_rule(self, label: str, value: str, wealth: Wealth):
        text = value.strip()
        if len(text) > 100:
            text = text[:100]
        wealth.loan_rule = text
        return wealth

    def extract_invest_on(self, label: str, value: str, wealth: Wealth):
        result = self.pattern_invest_on.search(value)
        if result:
            text = result.group(1)
            if len(text) > 100:
                text = text[:100]
            wealth.invest_on = text
        return wealth
