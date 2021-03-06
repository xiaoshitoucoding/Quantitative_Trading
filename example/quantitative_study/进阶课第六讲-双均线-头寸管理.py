'''
普量学院量化投资课程系列案例源码包
普量学院版权所有
仅用于教学目的，严禁转发和用于盈利目的，违者必究
©Plouto-Quants All Rights Reserved

普量学院助教微信：niuxiaomi3
'''

# 导入函数库
import jqdata
import pandas as pd
import numpy as np
import math
import talib as tl


# 两次处理交易逻辑的窗口大小
TRADE_BAR_DURATION = 15
# 操作时的分钟线级别
UNIT = str(TRADE_BAR_DURATION) + 'm'
# 股票池计算涨跌幅的窗口大小
CHANGE_PCT_DAY_NUMBER = 25
# 更新股票池的间隔天数
CHANGE_STOCK_POOL_DAY_NUMBER = 25

# 买卖信号的长时均线窗口大小
LONG_MEAN = 30
# 买卖信号的短时均线窗口大小
SHORT_MEAN = 5
# 标的调整出股票池后是否卖出
CLOSE_POSITION = False
# 跟踪止损的ATR倍数，即买入后，从最高价回撤该倍数的ATR后止损
TRAILING_STOP_LOSS_ATR = 4
# 计算ATR时的窗口大小
ATR_WINDOW = 20

POSITION_SIGMA = 3

# 初始化函数，设定基准等等
def initialize(context):
    # 设定沪深300作为基准
    set_benchmark('000300.XSHG')
    # 开启动态复权模式(真实价格)
    set_option('use_real_price', True)
    # 过滤掉order系列API产生的比error级别低的log
    log.set_level('order', 'error')

    ### 股票相关设定 ###
    # 设定滑点为0
    set_slippage(FixedSlippage(0))
    # 股票类每笔交易时的手续费是：买入时佣金万分之三，卖出时佣金万分之三加千分之一印花税, 每笔交易佣金最低扣5块钱
    set_order_cost(OrderCost(close_tax=0.001, open_commission=0.0003, close_commission=0.0003, min_commission=5), type='stock')

    init_global(context)

    # 开盘前运行
    run_daily(before_market_open, time='before_open', reference_security='000300.XSHG')
    # 交易
    run_daily(trade, time='every_bar',reference_security='000300.XSHG')
    # 收盘后运行
    run_daily(after_market_close, time='after_close', reference_security='000300.XSHG')


def init_global(context):
    '''
    初始化全局变量
    '''
    # 距上一次股票池更新的天数
    g.stock_pool_update_day = 0
    # 股票池，股票代码
    g.stock_pool = []
    # 距离上一次处理交易逻辑的bar的个数
    g.bar_number = 0
    # 缓存的数据
    # 当前缓存的数据有买入后最高价，用于跟踪止损
    g.cache_data = dict()


def before_market_open(context):
    '''
    开盘前运行函数
    '''
    # 更新持仓股票的最高价
    for code in context.portfolio.positions.keys():
        position = context.portfolio.positions[code]
        high_price = get_price(security=code, start_date=position.init_time, end_date=context.current_dt, frequency="1m", fields=['high'], skip_paused=True, fq="pre", count=None)['high'].max()
        if code not in g.cache_data.keys():
            g.cache_data[code] = dict()
        g.cache_data[code]['high_price'] = high_price

        # 更新标的的ATR数据
        atr = calc_history_atr(code=code,end_time=position.init_time,timeperiod=ATR_WINDOW,unit=UNIT)
        if code not in g.cache_data.keys():
            g.cache_data[code] = dict()
        g.cache_data[code]['atr'] = atr
    pass


def trade(context):
    '''
    交易函数
    '''
    # 调用平仓处理逻辑。
    if CLOSE_POSITION:
        close_position(context)
    # 调用止损逻辑
    stop_loss(context)
    # 间隔 TRADE_BAR_DURATION 调用一次买入函数
    if g.bar_number % TRADE_BAR_DURATION == 0:
        buy(context)   # 建仓
        sell(context)
    g.bar_number = (g.bar_number + 1 ) % TRADE_BAR_DURATION
    pass


def after_market_close(context):
    '''
    收盘后处理

    1. 更新股票池
    2. 更新股票池后，获取需要新买入的标的列表
    '''
    if g.stock_pool_update_day % CHANGE_STOCK_POOL_DAY_NUMBER == 0:
        # 更新股票池
        stock_pool(context)
    g.stock_pool_update_day = (g.stock_pool_update_day + 1) % CHANGE_STOCK_POOL_DAY_NUMBER
    record(pos=(context.portfolio.positions_value / context.portfolio.total_value * 100))
    pass


def close_position(context):
    '''
    平仓逻辑，当持仓标的不在股票池中时，平仓该标的
    '''
    for code in context.portfolio.positions.keys():
        if code not in g.stock_pool:
            if is_low_limit(code):
                continue
            # 标的已经不在股票池中尝试卖出该标的的股票
            order_ = order_target(security=code, amount=0)
            if order_ is not None and order_.filled:
                log.info("交易 卖出 平仓",code,order_.filled)


def stop_loss(context):
    '''
    跟踪止损
    '''
    for code in context.portfolio.positions.keys():
        position = context.portfolio.positions[code]
        if position.closeable_amount <= 0:
            continue
        if is_low_limit(code):
            continue
        current_data = get_current_data()[code]
        if current_data == None:
            continue
        current_price = current_data.last_price

        # 获取持仓期间最高价
        start_date = context.current_dt.strftime("%Y-%m-%d") + " 00:00:00"
        if context.current_dt.strftime("%Y-%m-%d") <= position.init_time.strftime("%Y-%m-%d"):
            start_date = position.init_time
        high_price = get_price(security=code, start_date=start_date, end_date=context.current_dt, frequency='1m', fields=['high'], skip_paused=True, fq='pre', count=None)['high'].max()
        # 每日9:30时，get_price获取 00:00到09:30之间的最高价时，数据返回的为NaN，需要特殊处理。这里采用当前价格和缓存的最高价进行比较。
        if not np.isnan(high_price):
            high_price = max(high_price,g.cache_data[code]['high_price'])
        else:
            high_price = max(current_price,g.cache_data[code]['high_price'])

        g.cache_data[code]['high_price'] = high_price

        atr = g.cache_data[code]['atr']
        if current_price <= high_price - atr * TRAILING_STOP_LOSS_ATR:
            # 当前价格小于等于最高价回撤 TRAILING_STOP_LOSS_ATR 倍ATR，进行止损卖出
            order_ = order_target(security=code, amount=0)
            if order_ is not None and order_.filled > 0:
                log.info("交易 卖出 跟踪止损",code,order_.filled,current_price,high_price,atr,(atr * TRAILING_STOP_LOSS_ATR))
    pass


def sell(context):
    '''
    卖出逻辑。
    当标的触发短时均线下穿长时均线时，卖出标的

    注意：
        停牌无法卖出
        跌停无法卖出
        没有可卖出仓位时无法卖出
    '''
    for code in context.portfolio.positions.keys():
        current_data = get_current_data()[code]
        if current_data == None:
            continue
        if is_low_limit(code):
            continue
        if context.portfolio.positions[code].closeable_amount <= 0:
            continue

        # 计算均线交叉需要最新3个均线值。所以这里需要+3
        count = max(LONG_MEAN,SHORT_MEAN) + 3
        close_data = attribute_history(security=code, count=count, unit=UNIT,fields=['close'],skip_paused=True, df=True, fq='pre')['close']
        if (list(np.isnan(close_data)).count(True) > 0) or (len(list(close_data)) < count):
            continue

        # 长时均线
        long_mean  = pd.rolling_mean(close_data,LONG_MEAN)
        # 短时均线
        short_mean = pd.rolling_mean(close_data,SHORT_MEAN)

        # 短时均线下穿长时均线时买入
        if (cross(short_mean,long_mean) < 0):
            available_cash = context.portfolio.available_cash
            order_ = order_target(security=code, amount=0)
            used_cash = context.portfolio.available_cash - available_cash
            if order_ is not None and order_.filled > 0:
                log.info("交易 卖出 死叉",code,"卖出数量",order_.filled,"卖出价格",order_.price,"买入均价",order_.avg_cost,"成交金额",used_cash)
    pass


def buy(context):
    '''
    买入逻辑。
    股票池中的标的在发生短时均线上穿长时均线时买入

    注意：
        涨停无法买入
        停牌无法买入
        已经持仓的股票无法买入
    '''
    for code in g.stock_pool:
        if code in context.portfolio.positions.keys():
            continue
        current_data = get_current_data()[code]
        if current_data == None:
            return
        if is_high_limit(code):
            continue
        count = max(LONG_MEAN,SHORT_MEAN) + 3
        close_data = attribute_history(security=code, count=count, unit=UNIT,fields=['close'],skip_paused=True, df=True, fq='pre')['close']
        if (list(np.isnan(close_data)).count(True) > 0) or (len(list(close_data)) < count):
            continue

        # 长时均线
        long_mean  = pd.rolling_mean(close_data,LONG_MEAN)
        # 短时均线
        short_mean = pd.rolling_mean(close_data,SHORT_MEAN)

        # 短时均线上穿长时均线时买入
        if (cross(short_mean,long_mean) > 0):
            # 计算头寸
            position_amount = calc_position(context,code)
            available_cash = context.portfolio.available_cash
            order_ = order_target(security=code,amount=position_amount)
            used_cash = context.portfolio.available_cash - available_cash

            if order_ is not None and order_.filled > 0:
                log.info("交易 买入",code,"预期买入股数",position_amount,"实际买入的股数",order_.filled,"价格",order_.price,"成交金额",used_cash)
                # 计算标的的ATR数据，并缓存
                atr = calc_history_atr(code=code,end_time=context.current_dt,timeperiod=ATR_WINDOW,unit=UNIT)
                if code not in g.cache_data.keys():
                    g.cache_data[code] = dict()
                g.cache_data[code]['atr'] = atr

    pass


def cross(short_mean,long_mean):
    '''
    判断短时均线和长时均线的关系。

    Args:
        short_mean 短时均线，长度不应小于3
        long_mean  长时均线，长度不应小于3。

    Returns:
         1 短时均线上穿长时均线
         0 短时均线和长时均线未发生交叉
        -1 短时均线下穿长时均线
    '''
    delta = short_mean[-3:] - long_mean[-3:]
    if (delta[-1] > 0) and ((delta[-2] < 0) or ((delta[-2] == 0) and (delta[-3] < 0))):
        return 1
    elif (delta[-1] < 0) and ((delta[-2] > 0) or ((delta[-2] == 0) and (delta[-3] > 0))):
        return -1
    return 0


def load_fundamentals_data(context):
    '''
    加载股票的财务数据，包括总市值和PE
    '''
    df = get_fundamentals(query(valuation,indicator), context.current_dt.strftime("%Y-%m-%d"))
    raw_data = []
    for index in range(len(df['code'])):
        raw_data_item = {
            'code'      :df['code'][index],
            'market_cap':df['market_cap'][index],
            'pe_ratio'  :df['pe_ratio'][index]
            }
        raw_data.append(raw_data_item)
    return raw_data


def load_change_pct_data(context,codes):
    '''
    计算标的的25日涨跌幅。

    Args:
        context 上下文
        codes   标的的代码列表
    Returns:
        标的的涨跌幅列表。列表中的每一项数据时一个字典：
            code:标的代码
            change_pct: 标的的涨跌幅
    '''
    change_pct_dict_list = []
    # 计算涨跌幅需要用到前一日收盘价，所以需要多加载一天的数据，
    # 而这里在第二日的开盘前运行，计算前一个交易日收盘后的数据，所以需要再多加载一天
    # 使用固定的25个交易日，而非25个bar计算涨跌幅
    count = CHANGE_PCT_DAY_NUMBER + 1
    # 获取25个交易日的日期
    pre_25_dates = jqdata.get_trade_days(start_date=None, end_date=context.current_dt, count=count)
    pre_25_date = pre_25_dates[0]
    pre_1_date = pre_25_dates[-1]
    for code in codes:
        pre_25_data =  get_price(code, start_date=None, end_date=pre_25_date, frequency='daily', fields=['close'], skip_paused=True, fq='post', count=1)
        pre_1_data =  get_price(code, start_date=None, end_date=pre_1_date, frequency='daily', fields=['close'], skip_paused=True, fq='post', count=1)
        pre_25_close = None
        pre_1_close = None
        if str(pre_25_date) == str(pre_25_data.index[0])[:10]:
            pre_25_close = pre_25_data['close'][0]
        if str(pre_1_date) == str(pre_1_data.index[0])[:10]:
            pre_1_close = pre_1_data['close'][0]

        if pre_25_close != None and pre_1_close != None and not math.isnan(pre_25_close) and not math.isnan(pre_1_close):
            change_pct = (pre_1_close - pre_25_close) / pre_25_close
            item = {'code':code, 'change_pct': change_pct}
            change_pct_dict_list.append(item)
    return change_pct_dict_list


def stock_pool(context):
    '''
    更新股票池。该方法在收盘后调用。

    1. 全市场的股票作为基础股票池
    2. 在基础股票池的基础上剔除ST的股票作为股票池1
    3. 在股票池1的基础上剔除总市值最小的10%的股票作为股票池2
    4. 在股票池2的基础上剔除PE < 0 或 PE > 100的股票作为股票池3
    5. 在股票池3的基础上 取25日跌幅前10%的股票作为最终的股票池
    '''
    current_date = context.current_dt.strftime("%Y-%m-%d")
    # 获取股票财务数据
    raw_data = load_fundamentals_data(context)

    # 剔除ST的股票
    raw_data_array = []
    current_datas = get_current_data()
    for item in raw_data:
        code = item['code']
        current_data = current_datas[code]
        if current_data.is_st:
            continue
        name = current_data.name
        if 'ST' in name or '*' in name or '退' in name:
            continue
        raw_data_array.append(item)

    raw_data = raw_data_array
    # 按照财务信息中的总市值降序排序
    raw_data = sorted(raw_data,key = lambda item:item['market_cap'],reverse=True)
    # 剔除总市值排名最小的10%的股票
    fitered_market_cap = raw_data[:int(len(raw_data) * 0.9)]
    # 剔除PE TTM 小于0或大于100的股票
    filtered_pe = []
    for stock in fitered_market_cap:
        if stock['pe_ratio'] == None or math.isnan(stock['pe_ratio']) or float(stock['pe_ratio']) < 0 or float(stock['pe_ratio']) > 100:
            continue
        filtered_pe.append(stock['code'])

    # 加载标的的涨跌幅信息
    change_pct_dict_list = load_change_pct_data(context,filtered_pe)
    # 按照涨跌幅升序排序
    change_pct_dict_list = sorted(change_pct_dict_list,key = lambda item:item['change_pct'],reverse=False)
    # 取跌幅前10%的股票
    change_pct_dict_list = change_pct_dict_list[0:(int(len(change_pct_dict_list)*0.1))]

    # 获取最终的股票池
    g.stock_pool = []
    for stock in change_pct_dict_list:
        g.stock_pool.append(stock['code'])
    log.info('调整股票池,筛选出的股票池：',g.stock_pool)
    pass



def is_high_limit(code):
    '''
    判断标的是否涨停或停牌。

    Args:
        code 标的的代码

    Returns:
        True 标的涨停或停牌，该情况下无法买入
    '''
    current_data = get_current_data()[code]
    if current_data.last_price >= current_data.high_limit:
        return True
    if current_data.paused:
        return True
    return False


def is_low_limit(code):
    '''
    判断标的是否跌停或停牌。

    Args:
        code 标的的代码

    Returns:
        True 标的跌停或停牌，该情况下无法卖出
    '''
    current_data = get_current_data()[code]
    if current_data.last_price <= current_data.low_limit:
        return True
    if current_data.paused:
        return True
    return False


def calc_history_atr(code,end_time,timeperiod=14,unit='1d'):
    '''
    计算标的的ATR。

    Args:
        code 标的的编码
        end_time 计算ATR的时间点
        timeperiod 计算ATR的窗口
        unit 计算ATR的bar的单位

    Returns:
        计算的标的在 end_time的ATR值
    '''
    security_data = get_price(security=code, end_date=end_time, frequency=unit, fields=['close','high','low'], skip_paused=True, fq='pre', count=timeperiod+1)
    nan_count = list(np.isnan(security_data['close'])).count(True)
    if nan_count == len(security_data['close']):
        log.info("股票 %s 输入数据全是 NaN，该股票可能已退市或刚上市，返回 NaN 值数据。" %stock)
        return np.nan
    else:
        return tl.ATR(np.array(security_data['high']), np.array(security_data['low']), np.array(security_data['close']), timeperiod)[-1]
    pass


def calc_position(context,code):
    '''
    计算建仓头寸

    Args:
        context 上下文
        code 要计算的标的的代码
    Returns:
        计算得到的头寸，单位 股数
    '''
    # 计算 risk_adjust_factor 用到的sigma的窗口大小
    RISK_WINDOW = 60
    # 计算 risk_adjust_factor 用到的两个sigma间隔大小
    RISK_DIFF = 30
    # 计算 sigma 的窗口大小
    SIGMA_WINDOW = 60

    # 计算头寸需要用到的数据的数量
    count = RISK_WINDOW + RISK_DIFF * 2
    count = max(SIGMA_WINDOW,count)

    history_values = get_price(security=code, end_date=context.current_dt, frequency=UNIT, fields=['close','high','low'], skip_paused=True, fq='pre', count=count)

    h_array = history_values['high']
    l_array = history_values['low']
    c_array = history_values['close']

    if (len(history_values.index) < count) or (list(np.isnan(h_array)).count(True) > 0) or (list(np.isnan(l_array)).count(True) > 0) or (list(np.isnan(c_array)).count(True) > 0):
        # 数据不足或者数据错误存在nan
        return 0

    # 数据转换
    value_array = []
    for i in range(len(h_array)):
        value_array.append((h_array[i] + l_array[i] + c_array[i] * 2) / 4)

    first_sigma  = np.std(value_array[-RISK_WINDOW-(RISK_DIFF*2):-(RISK_DIFF*2)])    # -120:-60
    center_sigma = np.std(value_array[-RISK_WINDOW-(RISK_DIFF*1):-(RISK_DIFF*1)])    #  -90:-30
    last_sigma   = np.std(value_array[-RISK_WINDOW              :])                  #  -60:
    sigma        = np.std(value_array[-SIGMA_WINDOW:])

    risk_adjust_factor_ = 0
    if last_sigma > center_sigma :
        risk_adjust_factor_ = 0.5
    elif last_sigma < center_sigma and last_sigma > first_sigma:
        risk_adjust_factor_ = 1.0
    elif last_sigma < center_sigma and last_sigma < first_sigma:
        risk_adjust_factor_ = 1.5

    return int(context.portfolio.starting_cash * 0.0025 * risk_adjust_factor_ / ((POSITION_SIGMA * sigma) * 100))  * 100
