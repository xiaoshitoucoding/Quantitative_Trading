

from PickStockStrategy.PickStrategytByBreakAndAng import PickStrategyByBreakAndAng
from PickStockStrategy.PickStrategyByTrend import StrategyByTrend, StrategyByDownTrend, StrategyByUpTrend, StrategyByDownVolume, PickStrategyByVCP
from PickStockStrategy.PickStrategyByIndicator import StrategyByMacdDivergence, PickStrategyByIncreaseVolume, PickStrategyByChilliPepper
from Indicator.PlatIndicator import GetStockInfoByIndustry

from Trade.Capital import Capital
from Trade.Order import Order
from CoreBase.Benchmark import Benchmark
from Trade.KLManager import KLManager
from Util import DbUtil, DateUtil
from Util.DateUtil import getn_date
from CoreBase import Env
import datetime
import sys

def HtmlStrategyByIncreaseVolume(capital, benchmark, kl_pd_manager, choice_symbols):
    short_xd = int(sys.argv[4])
    long_xd = int(sys.argv[5])
    times = float(sys.argv[6])
    price_times = float(sys.argv[7])
    
    PickStrategyByIncreaseVolume(capital, benchmark, kl_pd_manager, choice_symbols, long_xd=long_xd, short_xd=short_xd, times=times, price_times = price_times)

def HtmlStrategyByBreakAndVolume(capital, benchmark, kl_pd_manager, choice_symbols):
    xd = int(sys.argv[4])
    volume_min = float(sys.argv[5])
    volume_max = float(sys.argv[6])
    if volume_min > volume_max or volume_min < -1 or volume_min > 1 or volume_max < -1 or volume_max > 1:
        print('输入参数错误')
        return
    PickStrategyByBreakAndAng(capital, benchmark, kl_pd_manager, choice_symbols, xd=xd, vol_rank_min=volume_min, vol_rank_max=volume_max)

def HtmlStrategyByStockShape(capital, benchmark, kl_pd_manager, choice_symbols):
    xd = int(sys.argv[4])
    shape_type = sys.argv[5].strip()
    if shape_type == 'VCP':
        PickStrategyByVCP(capital, benchmark, kl_pd_manager, choice_symbols, xd=xd)


def HtmlStrategyByChilliPepper(capital, benchmark, kl_pd_manager, choice_symbols):
    xd = int(sys.argv[4])
    up_deg_threshold = float(sys.argv[5].strip())

    PickStrategyByChilliPepper(capital, benchmark, kl_pd_manager, choice_symbols, xd=xd, up_deg_threshold=up_deg_threshold)


def HtmlIndustryInfo():
    xd = int(sys.argv[3])
    
    GetStockInfoByIndustry(xd=xd)


#制定环境是A股
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('输入参数错误')
    market_env = sys.argv[1].strip()
    start='2020-01-01'
    if market_env == 'USA':
        Env.g_market_target = Env.EMarketTargetType.E_MARKET_TARGET_US
    elif market_env == 'CN':
        Env.g_market_target = Env.EMarketTargetType.E_MARKET_TARGET_CN

    strategy_type = sys.argv[2].strip()

    if strategy_type == 'IndustryInfo':
        HtmlIndustryInfo()
        exit()

    total_asset = int(sys.argv[3]) * 100000000
    
    

    end = DateUtil.datetime_to_str(datetime.datetime.today())
    yesterday =  DbUtil.GetCNMaxTimeByCodeId()

    read_cash = 1000000
    benchmark = Benchmark(start=start, end=end)
    capital = Capital(read_cash, benchmark)
    kl_pd_manager = KLManager(benchmark, capital)
    choice_symbols = DbUtil.GetAllStockCodeIdFromStockTable(yesterday)
    choice_symbols = DbUtil.GetStockByFinancialStockAsset(choice_symbols, total_asset)
    
    print("=============================================================================")
    if strategy_type == 'IncreaseVolume':
        HtmlStrategyByIncreaseVolume(capital, benchmark, kl_pd_manager, choice_symbols)
    elif strategy_type == 'BreakAndVolume':
        HtmlStrategyByBreakAndVolume(capital, benchmark, kl_pd_manager, choice_symbols)
    elif strategy_type == 'StockShape':
        HtmlStrategyByStockShape(capital, benchmark, kl_pd_manager, choice_symbols)
    elif strategy_type == 'ChilliPepper':
        HtmlStrategyByChilliPepper(capital, benchmark, kl_pd_manager, choice_symbols)

    



    
    
