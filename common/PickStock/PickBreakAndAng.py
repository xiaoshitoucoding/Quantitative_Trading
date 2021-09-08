# -*- encoding:utf-8 -*-
"""
    选股示例因子：价格拟合角度选股因子
"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import numpy as np


from PickStock.PickStockBase import PickStockBase, reversed_result
from Indicator.SimpleBuyIndicator import VolumeRankBuyIndicator, RegressAngBuyIndicator
from Indicator.BuyIndicatorFactory import BuyIndicatorFactory




class PickBreakAndAng(PickStockBase):
    """拟合角度选股因子示例类"""
    def _init_self(self, **kwargs):
        """通过kwargs设置拟合角度边际条件，配置因子参数"""


        self.kwargs = kwargs
       

    @reversed_result
    def fit_pick(self, kl_pd, target_symbol):
        self.pickindicator_list.append(BuyIndicatorFactory.AddVolumeRankBuyIndicator(**self.kwargs))
        self.pickindicator_list.append(BuyIndicatorFactory.AddRegressAngBuyIndicator(**self.kwargs))
        self.pickindicator_list.append(BuyIndicatorFactory.AddBreakBuyIndicator(**self.kwargs))
        today_ind = len(kl_pd) -1

        for indicator_item in self.pickindicator_list:
            if not indicator_item.do_fit(kl_pd, today_ind):
                return False
        print('股票ID:{}     当前收盘价:{}'.format(kl_pd.code[0], kl_pd.close[today_ind]))
        return True
    

    def fit_first_choice(self, pick_worker, choice_symbols, *args, **kwargs):
        raise NotImplementedError('PickRegressAng fit_first_choice unsupported now!')
