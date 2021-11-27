from mycleaners.base.cleaner import Cleaner
from mycleaners.base.wealth import Wealth
from mycleaners.base.manual_table import ManualTable
from mycleaners.base.manual_text import ManualText
from utils.nlp_util import UTIL_CN_NUM
import re
from config import CONFIG
import os


class JsbchinaTable(ManualTable):

    table_labels_config = {
        'name': {'名称', '子份额'},
        'code': {'产品编码', '产品代码', '认购编号', '单元代码', '销售编号', '内部代码', '销售系统简称'},
        'term': {'计算天数', '理财期限', '计划期限', '周期天数', '存款期限', '产品期限', '投资周期', '投资期限', '目标客户'},
        'product_type': {'产品类型', '收益类型', '存款类型', '投资及收益币种'},
        'amount_size': {'募集金额', '产品规模', '发行规模', '开放规模', '认购规模', '募集规模', '发售规模', '计划规模', '最大募集额'},

        'date_open': {'募集起始日'},
        'date_close': {'募集结束日'},
        'date_start': {'收益起始日', '起始日'},
        'date_end': {'份额赎回日', '到期日'},
    }
    pattern_risk_cn_table_text = re.compile(r'风险[评等分][级类][属于为是：:\s]*[基本]*([无低较中等高极]+风险)')
    pattern_risk_dig_table_text = re.compile(r'风险[评等分][级类][属于为是：:\s]*([0-9A-Za-z零一二三四五]+)级?')
    pattern_invest_on_table_text = re.compile(r'本[期]?理财[理财募集的资计划产品本金最终可存续期间,，主要]*投资于[以下投资工具：:\s]*([\u4e00-\u9fa5、，；;,:：%％+\[\]（）()A-Za-z0-9\-]+)。')

    pattern_term_jsbchina = re.compile(r'理财[计划]*期限[为是：:\s]*([0-9]+)\s*([天日月年])')
    pattern_fee_types_jsbchina = re.compile(r'([销售托管其他手续固定认购投资]+(管理|服务)?费)[\s:：率为]*([0-9]+(\.[0-9]+)*)[%％][\s/每]*年')

    def parse_table_text(self, wealth: Wealth, table_text: str):
        if not wealth.risk:
            risk = None
            result = self.pattern_risk_cn_table_text.search(table_text)
            if result:
                risk_raw = result.group(1)
                for key in self.list_risk.keys():
                    if key == risk_raw:
                        risk = self.list_risk[key]
                        break
            if not risk:
                result = self.pattern_risk_dig_table_text.search(table_text)
                if result:
                    risk_raw = result.group(1)
                    res_num = re.search(r'[0-9]', risk_raw)
                    if res_num:
                        risk = res_num.group(0)
                        risk = int(risk)
                        if risk > 5:
                            self.log.error('风险评级数字超出范围，内容为：%s' % result.group(0))
                    else:
                        res_cn_num = re.search(r'[零一二三四五]', risk_raw)
                        if res_cn_num:
                            cn_num = res_cn_num.group(0)
                            risk = UTIL_CN_NUM[cn_num]
            wealth.risk = risk

        if not wealth.invest_on:
            result = self.pattern_invest_on_table_text.search(table_text)
            if result:
                text = result.group(1)
                if len(text) > 100:
                    text = text[:100]
                wealth.invest_on = text
        return wealth

    def extract_code(self, label: str, value: str, wealth: Wealth):
        res = self.pattern_code_in_name.search(value)
        if res:
            wealth.code = res.group(1)
            return wealth

        result = self.pattern_code.search(value)
        if result:
            wealth.code = result.group(1)
        return wealth

    def extract_name(self, label: str, value: str, wealth: Wealth):
        if label != '申购子份额':
            wealth.name = value

            result = self.pattern_code_in_name.search(value)
            if result:
                wealth.code = result.group(1)

            res = self.pattern_code_register_in_name.search(value)
            if res:
                wealth.code_register = res.group(2)

            wealth = self.extract_product_type(label, value, wealth)
        return wealth

    def extract_term(self, label: str, value: str, wealth: Wealth):
        if not wealth.term:
            # 检查value单元格是否为纯数字，若是，则再检查label标签中是否有单位，如有单位，则转换为天数后返回
            pattern_num = re.compile(r'[0-9]+')
            res_value = pattern_num.fullmatch(value)
            if res_value:
                num = int(res_value.group(0))
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

            ress = self.pattern_term_jsbchina.search(value)
            if ress:
                num = int(ress.group(1))
                unit = ress.group(2)
                if unit == '月':
                    num = num * 30
                elif unit == '年':
                    num = num * 365
                if num < 7301:              # 设定期限的最大值不能超过20年
                    wealth.term = num
                return wealth

            result = self.pattern_term.search(value)
            if result:
                num = int(result.group(1))
                unit = result.group(2)
                if unit == '月':
                    num = num * 30
                elif unit == '年':
                    num = num * 365
                if num < 7301:              # 设定期限的最大值不能超过20年
                    wealth.term = num
        return wealth

    def extract_sale_areas(self, label: str, value: str, wealth: Wealth):
        if '销售渠道' in value:
            list_value = value.split('销售渠道')
            wealth.sale_areas = list_value[0]
            wealth = self.extract_sale_ways(label, list_value[-1], wealth)
        else:
            wealth.sale_areas = value.strip()
        return wealth


class JsbchinaText(ManualText):
    labels_check_config = {}
    labels_check_one_config = {}


class JsbchinaCleaner(Cleaner):
    name = 'JsbchinaCleaner'
    bank_name = None

    # 江苏银行的PDF文件解析不出来，先要将其PDF文件使用word转换为docx文件，然后再解析

    def start_init(self):
        self.bank_name = '江苏银行'
        path = os.path.join(CONFIG.BASE_DIR, 'data\\manual')
        list_filenames = os.listdir(path)
        for filename in list_filenames:
            if filename.startswith(self.bank_name):
                words = os.path.splitext(filename)
                ukey = words[0]
                content_type = words[-1]
                # print('开始执行start_init方法，ukey=%s, content_type=%s' % (ukey, content_type))
                manual_in = self.Manual(ukey=ukey, content='novalue', content_type=content_type)
                yield manual_in

    def process_parse(self, ukey, tables, text):
        # print('解析出来的文字内容是：%s' % text)
        dict_wealth = JsbchinaTable.start(self.bank_name, ukey, tables)
        # print('dict_wealth内容是：', dict_wealth)
        dict_wealth = JsbchinaText.start(self.bank_name, dict_wealth, text)
        print('dict_wealth内容是：', dict_wealth)
        #for one in dict_wealth.values():
        #    print('=============================已解析完成%s=====================================' % one.ukey)
        #    if one.ukey == '江苏银行=1903007FA544':
        #        print('wealth内容是：', one)


def start():
    # JsbchinaCleaner.start()
    pass



