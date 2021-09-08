# -*- encoding:utf-8 -*-

"""
相对强弱指数（kdj）是通过比较一段时期内的平均收盘涨数和平均收盘跌数来分析市场买沽盘的意向和实力，
从而作出未来市场的走势

计算方法：

具体计算实现可阅读代码中_calc_kdj_from_pd()的实现
1. 根据收盘价格计算价格变动可以使用diff()也可以使用pct_change()
2. 分别筛选gain交易日的价格变动序列gain，和loss交易日的价格变动序列loss
3. 分别计算gain和loss的N日移动平均
4. rs = gain_mean / loss_mean
5. kdj = 100 - 100 / (1 + rs)

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



"""_calc_kdj_from_pd计算rs时使用gain，否则使用change"""
g_kdj_gain = True


# noinspection PyUnresolvedReferences
def _calc_kdj_from_ta(kl_pb, fastk_period=9, slowk_period=3):
    """
    使用talib计算kdj, 即透传talib.kdj计算结果
    :param prices: 收盘价格序列，pd.Series或者np.array
    :param time_period: kdj的N日参数, 默认14
    """
    dw = pd.DataFrame()
    import talib
    dw['slowk'], dw['slowd'] = talib.STOCH(
			kl_pb['high'].values, 
			kl_pb['low'].values, 
			kl_pb['close'].values, fastk_period, slowk_period,
                        slowk_matype=0,
                        slowd_period=3,
                        slowd_matype=0)
                        
    dw['slowj'] = list(map(lambda x,y: 3*x-2*y, dw['slowk'], dw['slowd']))
    dw.set_index(kl_pb.index, inplace=True)
    return dw




