import datetime
from PickStock.PickRegressAngMinMax import PickRegressAngMinMax
from PickStock.PickStockCrossMean import PickStockCrossMean
from PickStock.PickBreak import PickBreak
from PickStock.PickStockMacd import PickStockMacd
from Trade.PickStockWorker import PickStockWorker
from Trade.Capital import Capital
from Trade.Order import Order
from CoreBase.Benchmark import Benchmark
from Trade.KLManager import KLManager
from Util import DbUtil, DateUtil



# stock_pickers = [{'class' : PickRegressAngMinMax,
#                     'threshold_ang_min': 45.0, 
#                     'xd': 250, 
#                     'reversed': False},
#                     {'class' : PickRegressAngMinMax,
#                     'threshold_ang_max': 0.0, 
#                     'xd': 30, 
#                     'reversed': False}]




# stock_pickers = [{'class' : PickStockMacd,
#                     'short_mean': 5, 
#                     'long_mean': 30, 
#                     'reversed': False}]


def PickByBreak():
    stock_pickers = [{'class' : PickBreak,
                        'xd': 50, 
                        'vol_rank': 0.9,
                        'vol_days': 50,
                        'reversed': False},
                        {'class' : PickBreak,
                        'xd': 21, 
                        'vol_days': 21, 
                        'vol_rank': 0.9,
                        'reversed': False}]



    start='2020-01-01'
    end = DateUtil.datetime_to_str(datetime.datetime.today())

    read_cash = 1000000
    benchmark = Benchmark(start=start, end=end)
    # benchmark = Benchmark(n_folds=2)

    capital = Capital(read_cash, benchmark)



    kl_pd_manager = KLManager(benchmark, capital)

    choice_symbols = DbUtil.GetAllStockCodeIdFromStockTable()
    choice_symbols = DbUtil.GetSortedStockByFinancialStock(choice_symbols)
    choice_symbols = choice_symbols[:1000]
    stock_pick = PickStockWorker(capital, benchmark, kl_pd_manager, 
        choice_symbols = choice_symbols, stock_pickers = stock_pickers)
    stock_pick.fit()
    print('=======================================================================================')
    result_symbols = DbUtil.GetSortedStockByFinancialStock(stock_pick.choice_symbols)
    print(result_symbols)
    ###################################################################################################################
    ###################################################################################################################

    stock_pickers_1 = [{'class' : PickRegressAngMinMax,
                        'threshold_ang_min': 45.0, 
                        'xd': 21, 
                        'reversed': False},
                        {'class' : PickRegressAngMinMax,
                        'threshold_ang_max': 0.0, 
                        'xd': 30, 
                        'reversed': False}]



    stock_pick = PickStockWorker(capital, benchmark, kl_pd_manager, 
        choice_symbols = result_symbols, stock_pickers = stock_pickers_1)
    stock_pick.fit()
    print('=======================================================================================')
    result_symbols = DbUtil.GetSortedStockByFinancialStock(stock_pick.choice_symbols)
    print(result_symbols)


