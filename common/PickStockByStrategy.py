

from PickStockStrategy.PickStrategytByBreakAndAng import StrategyByBreakAndAng
from PickStockStrategy.PickStrategyByTrend import StrategyByTrend, StrategyByDownTrend, StrategyByUpTrend, StrategyByDownVolume, StrategyByVCP
from PickStockStrategy.PickStrategyByIndicator import StrategyByMacdDivergence, StrategyByIncreaseVolume

from Trade.Capital import Capital
from Trade.Order import Order
from CoreBase.Benchmark import Benchmark
from Trade.KLManager import KLManager
from Util import DbUtil, DateUtil
from Util.DateUtil import getn_date
import datetime






if __name__ == '__main__':
   

    start='2020-01-01'
    end = DateUtil.datetime_to_str(datetime.datetime.today())
    yesterday = getn_date(2, "%Y-%m-%d")
    read_cash = 1000000
    benchmark = Benchmark(start=start, end=end)
    capital = Capital(read_cash, benchmark)
    kl_pd_manager = KLManager(benchmark, capital)

    choice_symbols = DbUtil.GetAllStockCodeIdFromStockTable(yesterday)
    choice_symbols = DbUtil.GetSortedStockByFinancialStock(choice_symbols)
    # choice_symbols = DbUtil.GetCNStockByFinancialStockAsset(choice_symbols, 10000000000)
    # choice_symbols = ['sz.002001']
    # # #21天突破
    # StrategyByBreakAndAng(capital, benchmark, kl_pd_manager, choice_symbols, xd=21)
    # # #50天突破
    # StrategyByBreakAndAng(capital, benchmark, kl_pd_manager, choice_symbols, xd=50)

    # #长周期涨短周期跌
    # StrategyByTrend(capital, benchmark, kl_pd_manager, choice_symbols)

    # #缩量下跌
    # StrategyByDownTrend(capital, benchmark, kl_pd_manager, choice_symbols)

    #长期上涨
    # StrategyByUpTrend(capital, benchmark, kl_pd_manager, choice_symbols)

    # StrategyByDownVolume(capital, benchmark, kl_pd_manager, choice_symbols)

    # StrategyByMacdDivergence(capital, benchmark, kl_pd_manager, choice_symbols)



    # StrategyByVCP(capital, benchmark, kl_pd_manager, choice_symbols)
    StrategyByIncreaseVolume(capital, benchmark, kl_pd_manager, choice_symbols, long_xd=60, short_xd = 10, times = 5)



    
    
