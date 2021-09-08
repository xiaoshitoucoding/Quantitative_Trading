# -*- encoding:utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from matplotlib.pyplot import show
import random

from StrategyRunBack.BuyBreakRunBack import BuyBreakRunBack
from StrategyRunBack.BuyBreakAndAngRunBack import BuyBreakAndAngRunBack
from StrategyRunBack.BuyIndictorRunBack import BuyIndictorRunBack
from StrategyRunBack.BuyTrendRunBack import BuyTrendRunBack
from StrategyRunBack.BuyDMRunBack import BuyDMRunBack
from Util import DbTable


DbTable.select_table_name = DbTable.cn_stock_table_name
DbTable.select_stock_data_columns = DbTable.cn_stock_data_columns


if __name__ == '__main__':
    #突破+成交量+拟合角度
    #BuyBreakAndAngRunBack()
    #macd的金叉
    BuyIndictorRunBack()
    #趋势回测
    # BuyTrendRunBack()
    # BuyDMRunBack()





