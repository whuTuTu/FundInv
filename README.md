# 股票基金代码说明文档

### 1.基金池初筛

**变量说明**

| 名称                   | 变量                               | 日期   | 备注         |
| ---------------------- | ---------------------------------- | ------ | ------------ |
| 基金简称（官方）       | ths_fund_short_name_fund           | 无参数 | 无           |
| 基金经理(现任)         | ths_fund_manager_current_fund      | 无参数 | 无           |
| 基金经理(历任)         | ths_fund_manager_his_fund          | 无参数 | 无           |
| 是否指数基金           | ths_isindexfund_fund               | 无参数 | 无           |
| 投资类型(一级分类)     | ths_invest_type_first_classi_fund  | 无参数 | 无           |
| 投资类型(二级分类)     | ths_invest_type_second_classi_fund | 无参数 | 无           |
| 基金规模               | ths_fund_scale_fund                | 交易日 | 部分缺失     |
| 成立年限               | ths_found_years_fund               | 交易日 | 无           |
| 机构投资者持有比例     | ths_org_investor_held_ratio_fund   | 报告期 | **季度数据** |
| 股票市值占基金资产净值 | ths_stock_mv_to_fanv_fund          | 报告期 | **季度数据** |

**筛选条件：**

1. 每期基金规模：>=2亿 
2. 成立年限：>3年 
3. 管理人：至少从2018年开始管理 
4. 只保留ACE中A类的基金 
5. 每期权益仓位至少为60%，各期均值至少位80% 
6. 排除被动指数型基金



### 2.行业主题标签

**编制方法：**

首先，我们依据中信一级行业划分标准，初步将其映射至各个产业板块。其中，周期制造板块既包含了上游原材料、下游由经济波动主导的周期板块公司，也包含了产业链中游的制造型企业。 

进一步地，对于每一产业板块大类划分，下探至中信三级行业进行细分调整：

(a) 对于“交通运输”一级分 类：将 “航运”、“航空”、“港口”中信三级行业分类板块调整至“周期制造”板块；

(c) 对于“汽车”一级分类： 将“乘用车Ⅲ”、“摩托车及其他”、“汽车消费及服务Ⅲ”中信三级行业调整至“消费”板块；

(d) 对于“轻工制 造”一级分类：“家具”、“文娱轻工”、“其他家居”中信三级行业调整至“消费”板块。

| 行业大类 |                         中信一级行业                         |
| :------: | :----------------------------------------------------------: |
| 行业大类 | 食品饮料、商贸零售、消费者服务（/餐饮旅游）、家电、纺织服装、农林牧渔 |
|   医药   |                             医药                             |
|   周期   | 石油石化、煤炭、有色金属、钢铁、基础化工、建筑、建材、轻工制造 |
|   制造   |     机械、电力设备及新能源（/电力设备）、国防军工、汽车      |
|   TMT    |           通信、计算机、传媒、电子（/电子元器件）            |
| 金融地产 |              银行、非银行金融、综合金融、房地产              |
|   其他   |                交通运输、电力及公用事业、综合                |

(1) **短期标签**：当期某一行业板块配置比例≥60%，则为“XX 行业基金”；否则为“行业均衡基金”。

(2) **长期标签**：过去三年（N=6 期年报或半年报），某一行业板块配置比例平均值≥60%，且当期行业配置 比例≥40%，则为“XX 行业基金”；否则为“行业均衡基金”。对于观察期未满三年的基金，以建仓结束 日起的各行业配置比例平均值做替代，并在长期标签上备注“（未满回看期）”。<font color='red'> (x) </font>

(3)**行为标签**：如果观察期内所有短期标签均为“XX 行业基金”，即稳定性（标签出现的次数 / 标签样本总期数）＝100%，即该基金的 稳定性总结为“稳定 XX 行业基金”；如果观察期内所有短期标签均为“行业均衡基金”，即该基金的行业均衡标签稳定性（占比）＝100%，即该基金的稳定性总结为“稳定行业均衡基金”。如果不满足“稳定 XX 行业基金”或“稳定行业均衡基金”，即任一标签的稳定性（占比）均小于 100%，则<u>进一步筛选出</u><u>观察期内存在一行业的配置比例极差(range)＞20%的基金，则该类基金的稳定性总结为“行业轮动基金”</u>。其余基金的稳定性总结为空值。对于观察期未满三年的基金，我们在稳定性总结后标注“（未满回看期）”。

**时间频率**：年报/半年报

<font color='red'> **特殊处理**： </font>

1. 原本是将交通运输、电力及公用事业、综合行业划分为其他，由于存在中信行业的数据缺失值，因此将匹配完剩下的全部划分在了其他行业，包括缺失值。
2. 行业轮动基金没有写极差>20的条件，将稳定性不等于100的基金划分为“行业轮动基金”

**参考资料：**

信达证券_基金研究系列之六：基金标签体系-资产配置与行业主题配置.pdf

**变量说明：**

| 名称         | 变量                         | 日期        | 备注                                   |
| ------------ | ---------------------------- | ----------- | -------------------------------------- |
| 所属中信行业 | ths_the_citic_industry_stock | 自然日      | 部分缺失，参数100一级行业，102三级行业 |
| 占股票投资比 | p00475_f009                  | 半年报/年报 | 基金全部持仓数据在专题报告-资产配置中  |



### 3.风格标签

**编制方法：**

详情见参考资料，成长价值得分表

| 类别 | 因子简称         | 因子全称               | 合成比例 |
| :--: | ---------------- | ---------------------- | -------- |
| 价值 | BP               | 账面市值比             | 50%      |
| 价值 | EPTTM            | 市盈率倒数TTM          | 25%      |
| 价值 | SPTTM            | 市销率倒数TTM          | 25%      |
| 成长 | NETPROFITINCYOY  | 单季度净利润同比增速   | 33%      |
| 成长 | OPERREVINCYOY    | 单季度营业收入同比增速 | 33%      |
| 成长 | OPERPROFITINCYOY | 单季度营业利润同比增速 | 33%      |

**时间频率**：年报/半年报

<font color='red'>**特殊处理：**</font>

1. 初始数据部分缺失值用行业均值替代，每次大概有80-110只股票数据缺失。
2. 晨星的大中小盘划分以70%，90%的累计市值划分，大概划分出大盘768，中盘1625，小盘2674。天风证券研报做了修改，修改为前200只为大盘，300为中盘，剩下为小盘。此处采用研报做法，后续计算rawy不变。
3. 计算出rawx（风格）依照五等分点，分别为成长型、成长-均衡性，均衡性、均衡-价值型、价值型。rawy（市值）依照晨星原做法。

**参考资料：**

晨星中国投资风格箱概要说明.pdf

基金研究专题报告：基金的风格划分与不同风格下超额收益能力探究-20181019-天风证券-15页.pdf

**变量说明：**

|           名称            | 变量                         | 日期   | 备注                                         |
| :-----------------------: | :--------------------------- | ------ | -------------------------------------------- |
|          总市值           | ths_market_value_stock       | 交易日 | 无                                           |
|      市净率(PB,最新)      | ths_pb_latest_stock          | 交易日 | 参数100表示报告截至日期，101表示报告公告日期 |
|      市盈率(PE,TTM)       | ths_pe_ttm_stock             | 交易日 | 参数100表示报告截至日期，101表示报告公告日期 |
|      市销率(PS,TTM)       | ths_ps_ttm_stock             | 交易日 | 参数100表示报告截至日期，101表示报告公告日期 |
|  单季度.净利润同比增长率  | ths_sq_np_yoy_stock          | 报告日 | 无                                           |
| 单季度.营业收入同比增长率 | ths_revenue_yoy_sq_stock     | 报告日 | 无                                           |
| 单季度.营业利润同比增长率 | ths_op_yoy_sq_stock          | 报告日 | 无                                           |
|       所属中信行业        | ths_the_citic_industry_stock | 自然日 | 部分缺失，参数100一级行业，102三级行业       |

### 4.共振因子

**编制方法：**

基金X公布十只重仓股，分别被$x_1,x_2,...,x_{10}$只基金重仓持有，十只重仓股的持股市值分别为$v_1,v_2,...,v_{10}$，则其重仓占比$w_i=v_i/(v_1+v_2+...+v_{10})$，基金X的共振因子得分为$H=\sum\limits_i^nw_ix_i$。对共振因子从高到低 将基金等比例均分为：共振基金、中立基金、独立基金。

**数据频率**：季度

**变量说明：**

| 名称                   | 变量                                  | 日期   | 备注     |
| ---------------------- | ------------------------------------- | ------ | -------- |
| 持有重仓证券的基金数量 | ths_fund_num_of_heavily_held_sec_fund | 报告日 | 季报披露 |
| 重仓证券持仓市值       | ths_top_sec_held_num_fund             | 报告日 | 季报披露 |

<font color='red'> **特别说明：目前用的是全市场划分，其他用的是筛选后基金进行三等分。** </font>



### 5.集中度标签

根据【前10名重仓证券市值合计占证券投资市值比】将初筛后的基金降序排列并且等分为三份，定义集中度标签为“高”、“中”、“低”。

**说明**：长期指标（N=6），季度

**变量说明**

| 名称                                  | 变量                                 | 日期   | 备注 |
| ------------------------------------- | ------------------------------------ | ------ | ---- |
| 基金代码                              | ths_fund_code_fund                   | 无参数 | 无   |
| 前N名重仓证券市值合计占证券投资市值比 | ths_top_n_top_stock_mv_to_si_mv_fund | 季度   | N=10 |



### 6.编制基金指数

编制风格指数，首先根据行业长期标签筛选出“稳定行业均衡基金”，再根据短期标签划分为五类指数：成长型、成长-均衡性，均衡性、均衡-价值型、价值型。收益率每日等权加总，根据标签频率（即半年）进行调仓，并绘制时间序列图像。



### 附录一：报告披露时间

```
公募基金需要披露的报告有：季报、半年报和年报。

每个季度结束后的15个工作日内需要披露完成季报。

半年度后60个自然日内需要披露完成半年报。

年报则是需要在90个自然日内披露完成。

注意区分：工作日和自然日。

也即是：每年的1月、4月、7月和10月的20日前后（大致对应15个工作日）会看到季报的披露。季报只披露前十大重仓股。

在每年的3月底和8月底则是分别前一年的年报和当年的半年报，而年报和半年报则是会披露完整持仓。
```



### 附录二：短期和长期标签的选择

```
1.构建基金指数选择短期标签。

2.基金打标一律选择长期标签。
如果观察期（N=6）内所有短期标签均为同一个标签，即稳定性（标签出现的次数 / 标签样本总期数）＝100%，即该基金的 稳定性总结为“稳定 XX 基金”，否则为“XX轮动基金”。
```



# 纯债基金代码说明文档

### 1.基金池初筛

**变量说明**

| 名称               | 变量                               | 日期   | 备注 |
| ------------------ | ---------------------------------- | ------ | ---- |
| 基金代码           | ths_fund_code_fund                 | 无参数 | 无   |
| 基金简称(官方)     | ths_fund_short_name_fund           | 无参数 | 无   |
| 基金管理人         | ths_fund_supervisor_fund           | 无参数 | 无   |
| 基金经理(现任)     | ths_fund_manager_current_fund      | 无参数 | 无   |
| 投资类型(二级分类) | ths_invest_type_second_classi_fund | 无参数 | 无   |
| 基金规模(合并)     | ths_mergesize_fund                 | 交易日 | 无   |

**筛选条件：**

1. 只保留A份额的基金

2. 剔除被动指数型基金和二级债基，包括被动指数型债券基金、增强指数型债券基金、混合债券型基金(二级）

3. 取基金经理管理总规模前20%的基金经理的产品

   

### 2.基金公司标签

统计基金公司纯债基金的总规模，定义前20%的公司的产品为“大基金公司基金”，其余为“小基金公司基金”。

**说明**：长期指标（N=6），季度

| 名称           | 变量                     | 日期   | 备注 |
| -------------- | ------------------------ | ------ | ---- |
| 基金代码       | ths_fund_code_fund       | 无参数 | 无   |
| 基金管理人     | ths_fund_supervisor_fund | 无参数 | 无   |
| 基金规模(合并) | ths_mergesize_fund       | 交易日 | 无   |



### 3.杠杆率标签

根据杠杆率将初筛后的基金降序排列并且等分为三分，定义杠杆率标签为“高”、“中”、“低”。

**说明**：长期指标（N=6），季度

| 名称               | 变量               | 日期           | 备注 |
| ------------------ | ------------------ | -------------- | ---- |
| 基金代码           | ths_fund_code_fund | 无参数         | 无   |
| 基金报告期杠杆比率 | ths_jjggbl_fund    | 报告期（季报） | 无   |



### 4.久期标签

根据久期将初筛后的基金降序排列并且等分为三分，定义杠杆率标签为“长”、“中”、“短”。

**说明**：长期指标（N=6），季度

| 名称         | 变量                        | 日期           | 备注 |
| ------------ | --------------------------- | -------------- | ---- |
| 基金代码     | ths_fund_code_fund          | 无参数         | 无   |
| 基金组合久期 | ths_portfolio_duration_fund | 报告期（季报） | 无   |



### 5.债券种类标签

**编制方法：**

获取基金年报/半年报的全部持仓数据，然后统计利率债和信用债的占债券市值比例，如果利率债比例>信用债比例，那么定义为“利率债”，否则为“信用债”。

**说明**：长期指标（N=6），半年度

**利率债和信用债划分的依据：**

| 类别   | 同花顺一级划分                                               |
| ------ | ------------------------------------------------------------ |
| 利率债 | 国债，地方政府债，政府支持机构债                             |
| 信用债 | 金融债，中期票据，企业债，可转债，公司债，资产支持证券，可交换债券，其他债券，同业存单，短期融资券 |

**变量说明：**

| 名称              | 变量                         | 日期   | 备注 |
| ----------------- | ---------------------------- | ------ | ---- |
| 代码              | jydm:Y                       | 无参数 | 无   |
| 名称              | jydm_mc:Y                    | 无参数 | 无   |
| 债券代码          | p00483_f002:Y                | 无参数 | 无   |
| 占基金净值比（%） | p00483_f007:Y                | 无参数 | 无   |
| 占债券市值比（%） | p00483_f008:Y                | 无参数 | 无   |
| THS债券一级类型   | ths_ths_bond_first_type_bond | 无参数 | 无   |

<font color='red'>**问题：持仓披露并不完整；最后标签并没有稳定利率债基（长期标签）？**</font>



### 6.定开标签

**编制方法：**

对基金名称进行字段提取，如果有“定开”字段，则为1，否则为0。说明：定开的基金相比不定开的基金现金流更统一，方便管理人进行管理和投资。

**说明**：不分长短期标签



### 7.量化指标（基金通用）

**input(list):基金累计单位净值序列（复权方式：分红再投）**

**日频数据**

| 名称         | 函数名                                                       | 计算方法                                                     | 完成情况 |
| ------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | -------- |
| 收益率       | netvalue2return                                              | $(netvalue4list[i+1] - netvalue4list[i]) / netvalue4list[i]$ | √        |
| 累计收益率   | calculate_one_cum_return（单值）calculate_cum_returns（序列） | $(netvalue4list[i] - netvalue4list[0]) / netvalue4list[0]$   | √        |
| 夏普比率     | calculate_sharpe_ratio                                       | $(r_p-r_f)/\sigma(p)$   $r_f=0$                              | √        |
| 最大回撤     | calculate_max_drawdown                                       | 计算回撤序列$(onevalue - peak) / peak$，取max                | √        |
| 胜率         | calculate_win_rate                                           | 统计区间内基金收益率超大于0的周期数与总周期数之比            | √        |
| 赔率         | calculate_odds_ratio                                         | 又名盈亏比，获取区间内，平均盈利/平均损失。衡量基金每承担一单位亏损，可获得多少盈利 | √        |
| ---------    | ----------------------------------------------------------   | ----------------------------------------------------------------------------- | -----    |
| 超额收益率   | calculate_excess_returns                                     | $(1+基金涨幅)/(1+基准涨幅)-1$                                | √        |
| 超额夏普比率 | calculate_excess_sharpe_ratio                                | $超额收益均值/基金波动率$                                    | √        |
| 超额最大回撤 | calculate_excess_max_drawdown                                | 超额收益率→超额累计收益率→超额最大回撤                       | √        |
| 超额胜率     | calculate_excess_win_rate                                    | 统计区间内基金收益率超越标的指数的周期数与总周期数之比       | √        |
| 超额赔率     | calculate_excess_odds_ratio                                  | 用超额收益计算，平均盈利/平均损失                            | √        |
| ---------    | ----------------------------------------------------------   | ----------------------------------------------------------------------------- | -----    |



# 转债基金代码说明文档

THS转债定义：选取基金全称中含“转债”或“可转换”字样的所有债券型基金。

<img src="微信图片_20231011155500.jpg" alt="微信图片_20231011155500" style="zoom:50%;" />



# 模拟回测

### 1.长期好短期好vs长期好短期差

**选取指标：**

| 长期标签      | 短期标签      |
| ------------- | ------------- |
| 近5年累计收益 | 近1年累计收益 |
| 近5年最大回撤 | 近1年最大回撤 |
| 近5年夏普比例 | 近1年夏普比例 |
| 近5年胜率     | 近1年胜率     |
| 近5年赔率     | 近1年赔率     |

**计算过程：**

计算上述指标，并且根据指标排序打分，得到单个指标的得分，根据所有指标得分总和得到总得分。

- 长期好短期好——长期指标权重为1，短期指标为1，加总求均值
- 长期好短期差——长期指标权重为1，短期指标为-1，加总求均值

得到总得分降序排列，选取前10%的基金构成指数池，每半年更换一次基金池基金，根据其净值计算并画出指数走势。

**结论：**

对于股票基金——长期好短期差win

对于纯债基金——长期好短期好win
