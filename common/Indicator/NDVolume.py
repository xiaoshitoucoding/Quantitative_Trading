# -*- encoding:utf-8 -*-

"""
相对强弱指数（RSI）是通过比较一段时期内的平均收盘涨数和平均收盘跌数来分析市场买沽盘的意向和实力，
从而作出未来市场的走势

计算方法：

具体计算实现可阅读代码中_calc_rsi_from_pd()的实现
1. 根据收盘价格计算价格变动可以使用diff()也可以使用pct_change()
2. 分别筛选gain交易日的价格变动序列gain，和loss交易日的价格变动序列loss
3. 分别计算gain和loss的N日移动平均
4. rs = gain_mean / loss_mean
5. rsi = 100 - 100 / (1 + rs)

"""
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from Indicator.NDBase import plot_from_order, g_calc_type, ECalcType
from Util import ScalerUtil
from CoreBase.PdHelper import pd_rolling_mean



"""_calc_rsi_from_pd计算rs时使用gain，否则使用change"""
g_rsi_gain = True


# noinspection PyUnresolvedReferences
def _calc_volume_rank(volumes, time_period=21):
    if len(volumes) < time_period:
        return None
    volumes_list = volumes[-time_period:]
    return volumes_list.rank(method='first').map(lambda x: float((2*x - time_period)/time_period))


def _calc_today_volume_rank(volumes):
    time_period = len(volumes)
    volumes_rank = volumes.rank(method='first').map(lambda x: float((2*x - time_period)/time_period))
    return volumes_rank[-1]

def _calc_rank(volumes):
    time_period = len(volumes)
    volumes_rank = volumes.rank(method='first').map(lambda x: float((2*x - time_period)/time_period))
    return volumes_rank




   