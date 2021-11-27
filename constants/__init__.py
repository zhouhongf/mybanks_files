from .bank_dict import BankDict


# 风险等级划分
# R0: 无风险，极低风险
# R1: 低风险
# R2: 中低风险
# R3: 中风险
# R4: 中高风险
# R5: 高风险

# 产品要素  只收集个人理财信息
# ukey
# ukeyhash
# name:                     产品名称
# code:                     产品代码
# code_register:            登记编码
# bank_name:                银行名称

# raise_type:               公募、私募
# profit_type:              收益类型     如 净值型，预期收益型
# open_type:                封闭式、开放式
# fixed_type:               固定收益，浮动收益
# promise_type:             保本，非保本
# invest_on:                产品投资范围

# currency:                 币种
# risk:                     风险等级

# date_open:                发行起始日期
# date_close:               发行到期日期
# date_start:               产品起息日期
# date_end:                 产品结束日期
# backdays_need:            到期后资金到账日  如2个工作日
# term:                     期限  单位（天）
# date_detail:              期限说明，详情等

# rate_max:                 最高利率 或 净值参考
# rate_min:                 最低利率 或 净值参考
# rate_type:                利率类型
# rate_isnet:               是否是净利率，即已扣除其他费用等
# rate_detail:              利率说明，备注

# amount_size_min:          产品规模最小
# amount_size_max:          产品规模最大
# amount_buy_min:           起购金额
# amount_buy_max:           购买上限

# custodian:                托管机构
# fee_types:                托管费、申购费、赎回费、管理费、销售费等
# fee_rate:                 费用数量  加总  %
# fee_detail:               费用说明  单位 年化

# sale_areas:               销售区域  全国、上海、北京、江苏等
# sale_ways:                购买方式  手机、柜面等
# sale_agents:              代销机构

# redeem_rule:              赎回规则
# loan_rule:                融资服务， 如理财质押贷款
# memo:                     备注

