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

from jukuan_macd_signal import *  # 导入自定义的，用于信号检测的库


# 长时交易信号：15分钟级别，需要间隔15个1分钟bar判断一次是否交易
LONG_TRADE_BAR_DURATION = 15
LONG_UNIT = str(LONG_TRADE_BAR_DURATION) + 'm'
# 短时交易信号：5分钟级别，需要间隔5个1分钟bar判断一次是否交易
SHORT_TRADE_BAR_DURATION = 5
SHORT_UNIT = str(SHORT_TRADE_BAR_DURATION) + 'm'

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
    log.set_level('strategy', 'info')

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
    # 缓存15分钟级别计算MACD需要的数据
    g.macd_cache_long           = None
    # 缓存5分钟级别计算MACD需要的数据
    g.macd_cache_short          = None
    # 缓存15分钟级别底背离数据
    g.bottom_divergence_long    = dict()
    # 缓存15分钟级别顶背离数据
    g.top_divergence_long       = dict()
    # 缓存5分钟级别底背离数据
    g.bottom_divergence_short   = dict()
    # 缓存5分钟级别顶背离数据
    g.top_divergence_short      = dict()
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
        atr = calc_history_atr(code=code,end_time=get_last_time(position.init_time),timeperiod=ATR_WINDOW,unit=LONG_UNIT)
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

    if g.macd_cache_long is not None:
        # 15分钟级别交易
        if g.bar_number % LONG_TRADE_BAR_DURATION == 0:
            update_macd_cache(context,LONG_UNIT)
            buy(context, LONG_UNIT)   # 买入
            sell(context,LONG_UNIT)  # 卖出
    # 5分钟级别交易
    if g.macd_cache_short is not None:
        if g.bar_number % SHORT_TRADE_BAR_DURATION == 0:
            update_macd_cache(context,SHORT_UNIT)
            buy(context, SHORT_UNIT)   # 买入
            sell(context,SHORT_UNIT)  # 卖出
    g.bar_number = g.bar_number + 1
    pass


def update_macd_cache(context,unit):
    '''
    更新MACD缓存数据
    '''
    current_tm = context.current_dt.strftime("%Y-%m-%d %H:%M:%S")
    if unit == LONG_UNIT:
        # 更新15分钟级别的数据
        g.macd_cache_long.update_cache(context.current_dt)
        # 15分钟级别不需要判断连续背离，所以不需要缓存过多的数据
        g.bottom_divergence_long = dict()
        g.top_divergence_long = dict()

        for code in g.macd_cache_long.bars.keys():
            if code not in g.bottom_divergence_long.keys():
                g.bottom_divergence_long[code] = dict()
            if code not in g.top_divergence_long.keys():
                g.top_divergence_long[code] = dict()

            # 获取最新一根bar检测到的背离
            divergences = g.macd_cache_long.divergences[code] if code in g.macd_cache_long.divergences.keys() else []
            if len(divergences) > 0:
                for divergence in divergences:
                    last_dif_limit_tm = divergence.last_dif_limit_tm.strftime("%Y-%m-%d %H:%M:%S")
                    # DivergenceType.Bottom - 底背离，DivergenceType.Top - 顶背离
                    if divergence.divergence_type == DivergenceType.Bottom:
                        if current_tm not in g.bottom_divergence_long[code]:
                            g.bottom_divergence_long[code][current_tm] = list()

                        g.bottom_divergence_long[code][current_tm].append({
                            "last_dif_limit_tm":last_dif_limit_tm,
                            "pre_dif_limit_tm":divergence.pre_dif_limit_tm.strftime("%Y-%m-%d %H:%M:%S")
                            })

                    elif divergence.divergence_type == DivergenceType.Top:
                        # 顶背离
                        if current_tm not in g.top_divergence_long[code]:
                            g.top_divergence_long[code][current_tm] = list()
                        g.top_divergence_long[code][current_tm].append({
                            "last_dif_limit_tm": last_dif_limit_tm,
                            "pre_dif_limit_tm": divergence.pre_dif_limit_tm.strftime("%Y-%m-%d %H:%M:%S")
                            })
    elif unit == SHORT_UNIT:
        # 更新5分钟级别的数据
        g.macd_cache_short.update_cache(context.current_dt)

        for code in g.macd_cache_short.bars.keys():
            if code not in g.bottom_divergence_short.keys():
                g.bottom_divergence_short[code] = dict()
            if code not in g.top_divergence_short.keys():
                g.top_divergence_short[code] = dict()

            # 获取最新一根bar检测到的背离
            divergences = g.macd_cache_short.divergences[code] if code in g.macd_cache_short.divergences.keys() else []
            if len(divergences) > 0:
                for divergence in divergences:
                    last_dif_limit_tm = divergence.last_dif_limit_tm.strftime("%Y-%m-%d %H:%M:%S")
                    # DivergenceType.Bottom - 底背离，DivergenceType.Top - 顶背离
                    if divergence.divergence_type == DivergenceType.Bottom:
                        if current_tm not in g.bottom_divergence_short[code]:
                            g.bottom_divergence_short[code][current_tm] = list()

                        g.bottom_divergence_short[code][current_tm].append({
                            "last_dif_limit_tm":last_dif_limit_tm,
                            "pre_dif_limit_tm":divergence.pre_dif_limit_tm.strftime("%Y-%m-%d %H:%M:%S")
                            })

                    elif divergence.divergence_type == DivergenceType.Top:
                        # 顶背离
                        if current_tm not in g.top_divergence_short[code]:
                            g.top_divergence_short[code][current_tm] = list()
                        g.top_divergence_short[code][current_tm].append({
                            "last_dif_limit_tm":last_dif_limit_tm,
                            "pre_dif_limit_tm":divergence.pre_dif_limit_tm.strftime("%Y-%m-%d %H:%M:%S")
                            })
    pass


def after_market_close(context):
    '''
    收盘后处理
    1. 更新股票池
    2. 更新MACD缓存数据
    '''
    if g.stock_pool_update_day % CHANGE_STOCK_POOL_DAY_NUMBER == 0:
        # 更新股票池
        stock_pool(context)

        stock_pools = set()
        for code in g.stock_pool:
            stock_pools.add(code)
        for code in context.portfolio.positions.keys():
            stock_pools.add(code)
        log.info("开始缓存计算MACD需要使用到的数据")
        # 缓存15分钟级别计算MACD需要的数据
        g.macd_cache_long  = MacdCache(LONG_UNIT,  context.current_dt, count=250, stocks=stock_pools)
        # 缓存5分钟级别计算MACD需要的数据
        g.macd_cache_short = MacdCache(SHORT_UNIT, context.current_dt, count=250, stocks=stock_pools)
        log.info("缓存计算MACD需要使用到的数据完毕")
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
        # 为防止发生start_date 遭遇建仓时间，这里需要进行判断。
        # 当前时间和建仓时间在同一天时，start_date设置为建仓时间
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

        avg_cost = position.avg_cost

        if current_price <= high_price - atr * TRAILING_STOP_LOSS_ATR:
            # 当前价格小于等于最高价回撤 TRAILING_STOP_LOSS_ATR 倍ATR，进行止损卖出
            order_ = order_target(security=code, amount=0)
            if order_ is not None and order_.filled > 0:
                flag = "WIN*" if current_price > avg_cost else "FAIL"
                log.info("交易 卖出 跟踪止损",
                    code,
                    "卖出数量",order_.filled,
                    "当前价格",current_price,
                    "持仓成本",avg_cost,
                    "最高价",high_price,
                    "ATR",(atr * TRAILING_STOP_LOSS_ATR),
                    "价差",(high_price - current_price)
                    )
    pass


def sell(context,unit):
    '''
    卖出逻辑。
    触发15分钟顶背离或5分钟连续顶背离时卖出持仓标的
    '''
    for code in context.portfolio.positions.keys():
        current_data = get_current_data()[code]
        if current_data == None:
            continue
        if is_low_limit(code):
            continue
        if context.portfolio.positions[code].closeable_amount <= 0:
            continue
        current_tm = context.current_dt.strftime("%Y-%m-%d %H:%M:%S")

        is_sell = False
        sell_type = None
        if unit == LONG_UNIT:
            # 15分钟级别交易顶背离卖出
            if current_tm in g.top_divergence_long[code].keys():
                is_sell     = True
                sell_type   = "LONG "
        elif unit == SHORT_UNIT:
            # 5分钟级别交易 连续顶背离卖出
            if current_tm in g.top_divergence_short[code].keys():
                # 发生了5分钟级别的顶背离，需要判断是否发生了连续的顶背离
                for i in range(len(g.top_divergence_short[code][current_tm])):
                    item_obj = g.top_divergence_short[code][current_tm][i]
                    pre_dif_limit_tm = item_obj['pre_dif_limit_tm']

                    for time_key in g.top_divergence_short[code].keys():
                        if is_sell:
                            break
                        for j in range(len(g.top_divergence_short[code][time_key])):
                            last_dif_limit_tm = g.top_divergence_short[code][time_key][j]
                            if pre_dif_limit_tm == last_dif_limit_tm:
                                is_sell     = True
                                sell_type   = "SHORT"
                                break
        if is_sell:
            order_ = order_target(security=code, amount=0)
            if (order_ is not None) and (order_.filled > 0):
                log.info("交易 卖出",code,sell_type,
                    "成交均价",order_.price,
                    "平均成本",order_.avg_cost,
                    "卖出的股数",order_.filled)
    pass



def buy(context,unit):
    '''
    买入逻辑。
    当触发15分钟底背离或5分钟连续底背离时买入标的

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

        current_tm = context.current_dt.strftime("%Y-%m-%d %H:%M:%S")

        is_buy = False
        buy_type = None
        if unit == LONG_UNIT:
            # 15分钟级别交易底背离买入
            if current_tm in g.bottom_divergence_long[code].keys():
                # 发生了15分钟级别的底背离
                is_buy = True
                buy_type = "LONG "
        elif unit == SHORT_UNIT:
            # 5分钟级别交易 连续底背离买入
            if current_tm in g.bottom_divergence_short[code].keys():
                # 发生了5分钟级别的底背离，需要判断是否发生了连续的底背离
                for i in range(len(g.bottom_divergence_short[code][current_tm])):
                    item_obj = g.bottom_divergence_short[code][current_tm][i]
                    pre_dif_limit_tm = item_obj['pre_dif_limit_tm']

                    for time_key in g.bottom_divergence_short[code].keys():
                        if is_buy:
                            break
                        for j in range(len(g.bottom_divergence_short[code][time_key])):
                            last_dif_limit_tm = g.bottom_divergence_short[code][time_key][j]
                            if pre_dif_limit_tm == last_dif_limit_tm:
                                is_buy = True
                                buy_type = "SHORT"
                                break
        if is_buy:
            position_amount = calc_position(context,code)
            order_ = order_target(security=code, amount=position_amount)
            if (order_ is not None) and (order_.filled > 0):
                log.info("交易 买入",code,buy_type,"成交均价",order_.price,"买入的股数",order_.filled)
                # 计算ATR，并缓存
                # 计算标的的ATR数据，并缓存

                # 获取最近的15分数据
                atr = calc_history_atr(code=code,end_time=get_last_time(context.current_dt),timeperiod=ATR_WINDOW,unit=LONG_UNIT)
                if code not in g.cache_data.keys():
                    g.cache_data[code] = dict()
                g.cache_data[code]['atr'] = atr
                g.cache_data[code]['high_price'] = current_data.last_price
    pass


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


def get_last_time(time_):
    time_array = [
        "09:30","09:45",
        "10:00","10:15","10:30","10:45",
        "11:00","11:15","11:30",
        "13:15","13:30","13:45",
        "14:00","14:15","14:30","14:45",
        "15:00"
        ]

    date = time_.strftime("%Y-%m-%d")
    time_str = time_.strftime("%H:%M")

    for i in range(len(time_array) - 1):
        if time_array[i] <= time_str < time_array[i+1]:
            return date + " " + time_array[i] + ":00"


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

    history_values = get_price(security=code, end_date=get_last_time(context.current_dt), frequency=LONG_UNIT, fields=['close','high','low'], skip_paused=True, fq='pre', count=count)

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
