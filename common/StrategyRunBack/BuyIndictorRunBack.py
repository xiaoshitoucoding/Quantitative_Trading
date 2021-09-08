from FactorBuy.FactorBuyTrend import UpDownTrend, UpDownGolden, DownUpTrend
from FactorBuy.FactorIndictorBuy import FactorIndictorBuy
from FactorSell.FactorAtrNStop import FactorAtrNStop
from FactorSell.FactorCloseAtrNStop import FactorCloseAtrNStop
from FactorSell.FactorPreAtrNStop import FactorPreAtrNStop
from FactorSell.FactorSellBreak import FactorSellBreak
from FactorSell.FactorSellIndictor import FactorSellIndictor
from CoreBase import Env
from CoreBase.Store import ResultTuple
from CoreBase import Store
from Metrics.MetricsBase import MetricsBase
from Util import DbUtil
from CoreBase.Store import EStore
from Trade import PickTimeExecute
from FactorBuy.FactorBuyTrend import UpDownTrend
from StrategyRunBack.RunBack import run_loop_back
import pandas as pd




def BuyIndictorRunBack():
    csv_datalist = []
    FactorBuyIndictorRunBack(csv_datalist=csv_datalist, xd=10, stop_loss_n=1.0, stop_win_n=2.0)
    # print(csv_datalist)
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



def FactorBuyIndictorRunBack(csv_datalist, xd=20, stop_loss_n=2.0, stop_win_n=1.0, short_arg = 12, long_arg = 26):
    csv_columnslist = [short_arg, long_arg]
    # 设置初始资金数
    read_cash = 1000000
    # 设置选股因子，None为不使用选股因子
    stock_pickers = None
    # # 买入因子依然延用向上突破因子

    # buy_factors = [{'xd': xd, 'short_arg': short_arg, 'long_mean': long_arg, 'class': FactorIndictorBuy},
    #             ]


    buy_factors = [{'xd': xd, 'short_xd': 5, 'long_xd': 60, 'times':5, 'class': FactorIndictorBuy},
                ]

    # 卖出因子继续使用上一节使用的因子
    sell_factors = [
        {'stop_loss_n': stop_loss_n, 'stop_win_n': stop_win_n, 'class': FactorAtrNStop},
    ]

    # sell_factors = [{'short_arg': short_arg, 'long_mean': long_arg, 'class': FactorSellIndictor},
    #             ]
    # 择时股票池
    choice_symbols = DbUtil.GetAllStockCodeIdFromStockTable()
    # random.shuffle(choice_symbols)
    choice_symbols = DbUtil.GetCNStockByFinancialStockAsset(choice_symbols, 1000000000)
    print(choice_symbols)
    # choice_symbols = DbUtil.GetSortedStockByFinancialStock(choice_symbols)
    # choice_symbols = choice_symbols[:500]
    # choice_symbols = choice_symbols[:500]
    # choice_symbols=['MRNA']
    # 使用run_loop_back运行策略
    result_tuple, kl_pd_manger = run_loop_back(read_cash,
                                                    buy_factors,
                                                    sell_factors,
                                                    stock_pickers,
                                                    choice_symbols=choice_symbols,
                                                    n_folds=1)
    print(str(buy_factors))                                                
    print(str(sell_factors))  
    result_list = []
    metrics = MetricsBase(*result_tuple)
    metrics.fit_metrics()
    result_metircs = metrics.plot_returns_cmp()
    if result_metircs:
        csv_columnslist += result_metircs
    # metrics.plot_sell_factors()
    # metrics.plot_buy_factors()
    csv_datalist.append(csv_columnslist)