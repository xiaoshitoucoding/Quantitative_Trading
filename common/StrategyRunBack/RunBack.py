# -*- encoding:utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from matplotlib.pyplot import show
import random

from Util.DateUtil import *
from Trade.Capital import Capital
from Trade.Order import Order
from CoreBase.Benchmark import Benchmark
from Trade.KLManager import KLManager
from Trade.PickTimeMaster import PickTimeMaster

from FactorBuy.FactorBuyBreak import FactorBuyBreak
from FactorSell.FactorAtrNStop import FactorAtrNStop
from FactorSell.FactorCloseAtrNStop import FactorCloseAtrNStop
from FactorSell.FactorPreAtrNStop import FactorPreAtrNStop
from FactorSell.FactorSellBreak import FactorSellBreak
from CoreBase import Env
from CoreBase.Store import ResultTuple
from CoreBase import Store
from Metrics.MetricsBase import MetricsBase
from Util import DbUtil
from CoreBase.Store import EStore
from Trade import PickTimeExecute
from FactorBuy.FactorBuyTrend import UpDownTrend







def run_loop_back(read_cash, buy_factors, sell_factors, stock_picks=None, choice_symbols=None, n_folds=2,
                  start=None,
                  end=None,
                  commission_dict=None,
                  n_process_kl=Env.g_cpu_cnt * 2,
                  n_process_pick=Env.g_cpu_cnt):
    """
    封装执行择时，选股回测。

    推荐在使用.run_loop_back()函数进行全市场回测前使用.run_kl_update()函数首先将数据进行更新，
    在run_kl_update()中它会首选强制使用网络数据进行更新，在更新完毕后，更改数据获取方式为本地缓存，
    使用.run_kl_update()的好处是将数据更新与策略回测分离，在运行效率及问题排查上都会带来正面的提升

    :param read_cash: 初始化资金额度，eg：1000000
    :param buy_factors: 回测使用的买入因子策略序列，
                    eg：
                        buy_factors = [{'xd': 60, 'class': FactorBuyBreak},
                                       {'xd': 42, 'class': FactorBuyBreak}]
    :param sell_factors: 回测使用的卖出因子序列，
                    eg:
                        sell_factors = [{'stop_loss_n': 0.5, 'stop_win_n': 3.0, 'class': FactorAtrNStop},
                                        {'pre_atr_n': 1.0, 'class': FactorPreAtrNStop},
                                        {'close_atr_n': 1.5, 'class': FactorCloseAtrNStop},]
    :param stock_picks: 回测使用的选股因子序列：
                    eg:
                        stock_pickers = [{'class': PickRegressAngMinMax,
                                          'threshold_ang_min': 0.0, 'reversed': False},
                                         {'class': PickStockPriceMinMax,
                                          'threshold_price_min': 50.0,
                                          'reversed': False}]
    :param choice_symbols: 备选股票池, 默认为None，即使用py.env.g_market_target的市场类型进行全市场回测，
                           为None的情况下为symbol序列
                    eg:
                        choice_symbols = ['usNOAH', 'usSFUN', 'usBIDU', 'usAAPL', 'usGOOG',
                                          'usTSLA', 'usWUBA', 'usVIPS']
    :param n_folds: int, 回测n_folds年的历史数据
    :param start: 回测开始的时间, str对象, eg: '2013-07-10'
    :param end: 回测结束的时间, str对象 eg: '2016-07-26'
    :param commission_dict: 透传给Capital，自定义交易手续费的时候时候。
                    eg：
                        def free_commission(trade_cnt, price):
                            # 免手续费
                            return 0
                        commission_dict = {'buy_commission_func': free_commission,
                                         'sell_commission_func': free_commission}
                        Capital(read_cash, benchmark, user_commission_dict=commission_dict)

    :param n_process_kl: 金融时间序列数据收集启动并行的进程数，默认None, 内部根据cpu数量分配
    :param n_process_pick: 择时与选股操作启动并行的进程数，默认None, 内部根据cpu数量分配
    :return: (ResultTuple对象, KLManager对象)
    """
    if start is not None and end is not None and DateUtil.date_str_to_int(end) - DateUtil.date_str_to_int(
            start) <= 0:
        print('end date <= start date!!')
        return None, None

    benchmark = Benchmark(n_folds=n_folds, start=start, end=end)
    # 资金类初始化
    capital = Capital(read_cash, benchmark, user_commission_dict=commission_dict)

    """
         win_to_one:
         1. 如果symbol数量少于20
         2. 并且操作系统是windows，因为windows进程开辟销毁开销都非常大，
         3. 判断cpu不是很快，只能通过cpu数量做判断，4核认为速度一般
         这种情况下不再启动多个进程，只使用一个进程运行所有择时选股操作

         TODO：不能只以symbol数量进行判断，结合策略买入卖出策略数进行综合判断
    """
    # win_to_one = choice_symbols is not None and len(
    #     choice_symbols) < 20 and not Env.g_is_mac_os and Env.g_cpu_cnt <= 4

    # if n_process_pick is None:
    #     # 择时，选股并行操作的进程等于cpu数量, win_to_one满足情况下1个
    #     n_process_pick = 1 if win_to_one else Env.g_cpu_cnt
    # if n_process_kl is None:
    #     # mac系统下金融时间序列数据收集启动两倍进程数, windows只是进程数量，win_to_one满足情况下1个
    #     n_process_kl = 1 if win_to_one else Env.g_cpu_cnt * 2 if Env.g_is_mac_os else Env.g_cpu_cnt

    # # 选股策略执行，多进程方式
    # choice_symbols = PickStockMaster.do_pick_stock_with_process(capital, benchmark,
    #                                                                stock_picks, choice_symbols=choice_symbols,
    #                                                                n_process_pick_stock=n_process_pick)


    # kl数据管理类初始化
    kl_pd_manager = KLManager(benchmark, capital)
    # 批量获取择时kl数据
    kl_pd_manager.batch_get_pick_time_kl_pd(choice_symbols)

    # 在择时之前清理一下输出, 不能wait, windows上一些浏览器会卡死


    # 择时策略运行，多进程方式
    orders_pd, action_pd, all_fit_symbols_cnt = PickTimeMaster.do_symbols_with_same_factors_process(
        choice_symbols, benchmark,
        buy_factors, sell_factors, capital, kl_pd_manager=kl_pd_manager, n_process_kl=n_process_kl,
        n_process_pick_time=n_process_pick)

    # 返回namedtuple， ('orders_pd', 'action_pd', 'capital', 'benchmark')
    result = ResultTuple(orders_pd, action_pd, capital, benchmark)
    #store_result_tuple(result, n_folds)
    return result, kl_pd_manager


def run_kl_update(n_folds=2, start=None, end=None, market=None, n_jobs=16, how='thread'):
    """
    推荐在使用.run_loop_back()函数进行全市场回测前使用.run_kl_update()函数首先将数据进行更新，
    在run_kl_update()中它会首选强制使用网络数据进行更新，在更新完毕后，更改数据获取方式为本地缓存
    在run_kl_update实现根据EMarketTargetType类型即市场类型，进行全市场金融时间序列数据获取，使用多进
    程或者多线程对外执行函数，多任务批量获取时间序列数据。

    使用.run_kl_update()的好处是将数据更新与策略回测分离，在运行效率及问题排查上都会带来正面的提升

    eg：
        from py import ，EMarketTargetType
        # 港股全市场获取
        py.env.g_market_target = EMarketTargetType.E_MARKET_TARGET_HK
        # 更新6年的数据
        .run_kl_update(n_folds=6)

        # A股全市场获取
        py.env.g_market_target = EMarketTargetType.E_MARKET_TARGET_CN
        # 2013-07-10直到2016-07-26的数据
        .run_kl_update(start='2013-07-10', end='2016-07-26')

    :param n_folds: 请求几年的历史回测数据int
    :param start: 请求的开始日期 str对象, eg: '2013-07-10'
    :param end: 请求的结束日期 str对象 eg: '2016-07-26'
    :param market: 需要查询的市场，eg：EMarketTargetType.E_MARKET_TARGET_US
    :param n_jobs: 并行的任务数，对于进程代表进程数，线程代表线程数
    :param how: process：多进程，thread：多线程，main：单进程单线程
    """

    pre_market = None
    if market is not None:
        # 临时缓存之前的市场设置
        pre_market = Env.g_market_target
        Env.g_market_target = market

    # 所有任务数据强制网络更新
    Env.g_data_fetch_mode = EMarketDataFetchMode.E_DATA_FETCH_FORCE_NET
    # index=True, 需要大盘数据
    symbols = all_symbol(index=True)
    result = kl_df_dict_parallel(symbols, n_folds=n_folds, start=start, end=end, n_jobs=n_jobs, how=how)
    # 完成更新后所有认为强制走本地数据
    Env.g_data_fetch_mode = EMarketDataFetchMode.E_DATA_FETCH_FORCE_LOCAL

    if market is not None and pre_market is not None:
        # 还原缓存的市场设置
        Env.g_market_target = pre_market


def store_result_tuple(result_tuple, n_folds=None, store_type=EStore.E_STORE_NORMAL,
                           custom_name=None):
    """
    保存.run_loop_back的回测结果ResultTuple对象，根据n_folds，store_type参数
    来定义存储的文件名称，透传参数使用Store.store__result_tuple执行操作

    :param _result_tuple: ResultTuple对象类型
    :param n_folds: 回测执行了几年，只影响存贮文件名
    :param store_type: 回测保存类型EStore类型，只影响存贮文件名
    :param custom_name: 如果store_type=EStore.E_STORE_CUSTOM_NAME时需要的自定义文件名称
    """
    Store.store_result_tuple(result_tuple, n_folds, store_type=store_type, custom_name=custom_name)


# def load_result_tuple(n_folds=None, store_type=EStore.E_STORE_NORMAL, custom_name=None):
#     """
#     读取使用store__result_tuple保存的回测结果，根据n_folds，store_type参数
#     来定义读取的文件名称，依次读取orders_pd，action_pd，capital，benchmark后构造
#     ResultTuple对象返回，透传参数使用Store.load__result_tuple执行操作

#     :param n_folds: 回测执行了几年，只影响读取的文件名
#     :param store_type: 回测保存类型EStore类型，只影响读取的文件名
#     :param custom_name: 如果store_type=EStore.E_STORE_CUSTOM_NAME时需要的自定义文件名称
#     :return: ResultTuple对象
#     """
#     return Store.load_result_tuple(n_folds, store_type, custom_name=custom_name)


# noinspection PyUnusedLocal
def gen_buy_from_chinese(*args, **kwargs):
    """
    抱歉！由于中文生成策略的方法也需要遵循一定的语法和句式，对于完全不熟悉编程的人可能会产生错误，'
          '造成无谓的经济损失，所以中文自动生成交易策略模块暂时不开放接口以及源代码！
    """

    print('抱歉！由于中文生成策略的方法也需要遵循一定的语法和句式，对于完全不熟悉编程的人可能会产生错误，'
          '造成无谓的经济损失，所以中文自动生成交易策略模块暂时不开放接口以及源代码！')







