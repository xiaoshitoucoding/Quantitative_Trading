# -*- encoding:utf-8 -*-
"""
    选股示例因子：价格拟合角度选股因子
"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import numpy as np
import pandas as pd

from Util import RegUtil
from PickStock.PickStockBase import PickStockBase, reversed_result
from CoreBase.PdHelper import pd_rolling_mean
from Indicator.NDBoll import _calc_boll_from_ta, _calc_boll_from_pd




class PickStockCrossMean(PickStockBase):
    """拟合角度选股因子示例类"""
    def _init_self(self, **kwargs):
        """通过kwargs设置拟合角度边际条件，配置因子参数"""

        # 暂时与base保持一致不使用kwargs.pop('a', default)方式
        self.short_mean = 5
        if 'threshold_ang_min' in kwargs:
            # 设置最小角度阀值
            self.short_mean = kwargs['short_mean']

        self.long_mean = 30
        if 'threshold_ang_max' in kwargs:
            # 设置最大角度阀值
            self.long_mean = kwargs['long_mean']

    @reversed_result
    def fit_pick(self, kl_pd, target_symbol):
        """开始根据自定义拟合角度边际参数进行选股"""

        # 长时均线
        long_mean  = pd_rolling_mean(kl_pd.close, window=self.long_mean, min_periods=self.long_mean)
        # 短时均线
        short_mean = pd_rolling_mean(kl_pd.close, window=self.long_mean, min_periods=self.long_mean)

        boll_uper, boll_midd, boll_low = _calc_boll_from_pd(kl_pd.close)
        print('boll_uper:', boll_uper, len(boll_uper))
        print('boll_midd:', boll_midd, len(boll_midd))
        print('boll_low:', boll_low, len(boll_low))
        print('close', kl_pd.close, len(kl_pd.close))
        # 短时均线上穿长时均线时买入
        if (self.cross(short_mean,long_mean) > 0):
            return True
        return False

    def fit_first_choice(self, pick_worker, choice_symbols, *args, **kwargs):
        raise NotImplementedError('PickRegressAng fit_first_choice unsupported now!')

    def cross(self,short_mean,long_mean):
        '''
        判断短时均线和长时均线的关系。

        Args:
            short_mean 短时均线，长度不应小于3
            long_mean  长时均线，长度不应小于3。

        Returns:
            1 短时均线上穿长时均线
            0 短时均线和长时均线未发生交叉
            -1 短时均线下穿长时均线
        '''
        delta = short_mean[-3:] - long_mean[-3:]
        if (delta[-1] > 0) and ((delta[-2] < 0) or ((delta[-2] == 0) and (delta[-3] < 0))):
            return 1
        elif (delta[-1] < 0) and ((delta[-2] > 0) or ((delta[-2] == 0) and (delta[-3] > 0))):
            return -1
        return 0
