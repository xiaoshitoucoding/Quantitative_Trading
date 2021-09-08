# -*- encoding:utf-8 -*-
"""
    选股示例因子：价格拟合角度选股因子
"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import numpy as np

from Util import RegUtil
from PickStock.PickStockBase import PickStockBase, reversed_result
from Indicator.NDVolume import _calc_today_volume_rank




class PickBreak(PickStockBase):
    """拟合角度选股因子示例类"""
    def _init_self(self, **kwargs):
        """通过kwargs设置拟合角度边际条件，配置因子参数"""

        # 暂时与base保持一致不使用kwargs.pop('a', default)方式
        # fit_pick中 ang > threshold_ang_min, 默认负无穷，即默认所有都符合
        self.xd = 0
        self.vol_rank = -1.0
        self.vol_days = 0
        if 'xd' in kwargs:
            # 设置最小角度阀值
            self.xd = kwargs['xd']
        if 'vol_rank' in kwargs:
            self.vol_rank = kwargs['vol_rank']
        if 'vol_days' in kwargs:
            self.vol_days = kwargs['vol_days']



    @reversed_result
    def fit_pick(self, kl_pd, target_symbol):
        """开始根据自定义拟合角度边际参数进行选股"""
        if len(kl_pd.close) < self.xd - 1:
            return False
        today_ind = len(kl_pd.close) - 1
        volumes = kl_pd.volume[-self.vol_days:]
        today_vol_rank = _calc_today_volume_rank(volumes)
        # 今天的收盘价格达到xd天内最高价格则符合买入条件
        if kl_pd.close[today_ind] == kl_pd.close[today_ind - self.xd + 1:today_ind + 1].max() and today_vol_rank >= self.vol_rank:
            return True
        return False
    

    def fit_first_choice(self, pick_worker, choice_symbols, *args, **kwargs):
        raise NotImplementedError('PickRegressAng fit_first_choice unsupported now!')
