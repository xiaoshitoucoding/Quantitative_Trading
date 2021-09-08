from FactorBuy.FactorBuyDM import DoubleMaBuy 
from FactorSell.FactorAtrNStop import FactorAtrNStop
from FactorSell.FactorCloseAtrNStop import FactorCloseAtrNStop
from FactorSell.FactorPreAtrNStop import FactorPreAtrNStop
from FactorSell.FactorSellBreak import FactorSellBreak
from FactorSell.FactorSellDM import DoubleMaSell
from CoreBase import Env
from CoreBase.Store import ResultTuple
from CoreBase import Store
from Metrics.MetricsBase import MetricsBase
from Util import DbUtil
from CoreBase.Store import EStore
from Trade import PickTimeExecute
from StrategyRunBack.RunBack import run_loop_back
import pandas as pd


    # buy_factors = [{'xd': 5, 'class': UpDownTrend},
    #      
    # buy_factors = [{'xd': 50, 'rsi': 600, 'vol_rank': 0.8, 'vol_daily': 60, 'class': FactorBuyBreak},
    #             {'xd': 21, 'rsi': 600, 'vol_rank': 0.8, 'vol_daily': 42, 'class': FactorBuyBreak}
    #             ]

    # # 卖出因子继续使用上一节使用的因子
    # sell_factors = [
    #     {'stop_loss_n': 5.0, 'stop_win_n': 4.0, 'class': FactorAtrNStop},
    #    # {'class': FactorPreAtrNStop, 'pre_atr_n': 1.5},
    #    # {'class': FactorCloseAtrNStop, 'close_atr_n': 1.5}
    # ]

def BuyDMRunBack():
    csv_datalist = []
    FactorDMRunBack(csv_datalist=csv_datalist, stop_loss_n=2.0, stop_win_n=6.0)
    print(csv_datalist)
    # csv_datalist = []
    # for item_vol_rank in range(0, 11):
    #     item_vol_rank = float(item_vol_rank/10)
    #     for item_stop_loss in range(1, 10):
    #         for item_stop_win in range(1, 10):
    #             try:
    #                 FactorBuyBreakAndAngRunBack(csv_datalist=csv_datalist, vol_rank=item_vol_rank, stop_loss_n=item_stop_loss, stop_win_n=item_stop_win)
    #             except:
    #                 print('item_vol_rank:', item_vol_rank)
    #                 print('item_stop_loss:', item_stop_loss)
    #                 print('item_stop_win:', item_stop_win)
    # csv_dataframe = pd.DataFrame(csv_datalist, columns=['xd_1', 'xd_2', 'vol_rank', 'stop_loss_n', 'stop_win_n', '胜率', '盈亏比', '策略收益','策略年化收益','基准收益','基准年化收益','平均获利期望','平均亏损期望','买入后卖出的交易数量','买入后尚未卖出的交易数量','策略买入成交比例','策略资金利用率比例','策略共执行交易日'])
    # csv_dataframe.to_excel('./Excel/BuyBreakRunBack.xlsx', sheet_name='vol_rank', float_format='%.2f', na_rep=' ')



def FactorDMRunBack(csv_datalist, xd_1 = 20, stop_loss_n = 2.0, stop_win_n = 4.0):
    csv_columnslist = [xd_1, stop_loss_n, stop_win_n]
    # 设置初始资金数
    read_cash = 1000000
    # 设置选股因子，None为不使用选股因子
    stock_pickers = None
    # # 买入因子依然延用向上突破因子

    buy_factors = [{'xd': xd_1,  'class': DoubleMaBuy},
                ]

    # 卖出因子继续使用上一节使用的因子
    # sell_factors = [
    #     {'stop_loss_n': stop_loss_n, 'stop_win_n': stop_win_n, 'class': FactorAtrNStop},
    # ]
    sell_factors = [
        {'xd': xd_1, 'class': DoubleMaSell},
    ]

    # 择时股票池
    choice_symbols = DbUtil.GetAllStockCodeIdFromStockTable()
    # random.shuffle(choice_symbols)
    choice_symbols = DbUtil.GetSortedStockByFinancialStock(choice_symbols)
    # choice_symbols = choice_symbols[:500]
    choice_symbols = choice_symbols[:500]
    # choice_symbols=['MRNA']
    # 使用run_loop_back运行策略
    result_tuple, kl_pd_manger = run_loop_back(read_cash,
                                                    buy_factors,
                                                    sell_factors,
                                                    stock_pickers,
                                                    choice_symbols=choice_symbols,
                                                    n_folds=2)
    result_list = []
    metrics = MetricsBase(*result_tuple)
    metrics.fit_metrics()
    result_metircs = metrics.plot_returns_cmp()
    if result_metircs:
        csv_columnslist += result_metircs
    # metrics.plot_sell_factors()
    # metrics.plot_buy_factors()
    csv_datalist.append(csv_columnslist)