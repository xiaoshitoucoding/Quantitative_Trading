# -*- encoding:utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from matplotlib.pyplot import show


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
from FactorBuy.FactorBuyTrend import UpDownTrend
from CoreBase import Env
from CoreBase.Store import ResultTuple
from CoreBase import Store
from Metrics.MetricsBase import MetricsBase
from Util import DbUtil
from CoreBase.Store import EStore
from Trade import PickTimeExecute


if __name__ == '__main__':
    # 设置初始资金数
    read_cash = 1000000
    # 设置选股因子，None为不使用选股因子
    stock_pickers = None
    # 买入因子依然延用向上突破因子
    # buy_factors = [{'xd': 60, 'class': FactorBuyBreak},
    #             {'xd': 42, 'class': FactorBuyBreak}
    #             ]

    buy_factors = [{'xd': 5, 'class': UpDownTrend},
                ]

    # 卖出因子继续使用上一节使用的因子
    sell_factors = [
        {'stop_loss_n': 10.0, 'stop_win_n': 10.0, 'class': FactorAtrNStop},
        # {'class': FactorCloseAtrNStop, 'close_atr_n': 1.5}
    ]
 
    # 择时股票池
    # choice_symbols = ['HK.02202', 'HK.01816', 'HK.00005', 'HK.00388', 'HK.00700']
    # choice_symbols = ['HK.00700']
    choice_symbols = ['HK.02202', 'HK.01816', 'HK.00005', 'HK.00388', 'HK.00700']
    benchmark = Benchmark(n_folds=2)
    # 资金类初始化
    capital = Capital(read_cash, benchmark)
    # choice_symbols = DbUtil.GetAllStockCodeIdFromStockTable()
    # choice_symbols = all_stockid_list[:100]
    # 使用run_loop_back运行策略
    orders_pd, action_pd, all_fit_symbols_cnt = PickTimeExecute.do_symbols_with_same_factors(choice_symbols, benchmark, 
            buy_factors, sell_factors, capital = capital, show=False)
    result = ResultTuple(orders_pd, action_pd, capital, benchmark)
    metrics = MetricsBase(*result)
    metrics.fit_metrics()
    metrics.plot_returns_cmp()
    metrics.plot_sell_factors()
    metrics.plot_buy_factors()