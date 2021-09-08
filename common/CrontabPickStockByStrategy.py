

from PickStockStrategy.PickStrategytByBreakAndAng import StrategyByBreakAndAng
from PickStockStrategy.PickStrategyByTrend import StrategyByTrend, StrategyByDownTrend, StrategyByUpTrend,StrategyByVCP
from PickStockStrategy.PickStrategyByIndicator import StrategyByMacdDivergence

from Trade.Capital import Capital
from Trade.Order import Order
from CoreBase.Benchmark import Benchmark
from Trade.KLManager import KLManager
from Util import DbUtil, DateUtil
from Util.DateUtil import getn_date
import datetime
from Util import DbTable



DbTable.select_table_name = DbTable.usa_stock_table_name
DbTable.select_stock_data_columns = DbTable.usa_stock_data_columns


if __name__ == '__main__':
   

    start='2020-01-01'
    end = DateUtil.datetime_to_str(datetime.datetime.today())
    yesterday = getn_date(1, "%Y-%m-%d")
    read_cash = 1000000
    benchmark = Benchmark(start=start, end=end)
    capital = Capital(read_cash, benchmark)
    kl_pd_manager = KLManager(benchmark, capital)

    choice_symbols = DbUtil.GetAllStockCodeIdFromStockTable(yesterday)
    choice_symbols = DbUtil.GetSortedStockByFinancialStock(choice_symbols)
    print(choice_symbols)
    # #21天突破
    StrategyByBreakAndAng(capital, benchmark, kl_pd_manager, choice_symbols, xd=21)
    # #50天突破
    StrategyByBreakAndAng(capital, benchmark, kl_pd_manager, choice_symbols, xd=50)

    #长周期涨短周期跌
    StrategyByTrend(capital, benchmark, kl_pd_manager, choice_symbols)

    #缩量下跌
    StrategyByDownTrend(capital, benchmark, kl_pd_manager, choice_symbols)


    #长期上涨
    StrategyByUpTrend(capital, benchmark, kl_pd_manager, choice_symbols)

    StrategyByVCP(capital, benchmark, kl_pd_manager, choice_symbols)
    # #macd背离
    # StrategyByMacdDivergence(capital, benchmark, kl_pd_manager, choice_symbols)

    
    
