# -*- encoding:utf-8 -*-
"""
    选股示例因子：价格拟合角度选股因子
"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from common.Indicator import BuyIndicatorFactory

import numpy as np

from Util import RegUtil
from PickStock.PickStockBase import PickStockBase, reversed_result





class PickRegressAngMinMax(PickStockBase):gb
    """拟合角度选股因子示例类"""
    def _init_self(self, **kwargs):
        """通过kwargs设置拟合角度边际条件，配置因子参数"""

       
        self.pickindicator_list.append(BuyIndicatorFactory.AddRegressAngBuyIndicator(kl_pd=self.kl_pd, **kwargs))

    @reversed_result
    def fit_pick(self, kl_pd, target_symbol):
        """开始根据自定义拟合角度边际参数进行选股"""
        today_ind = len(kl_pd.close) - 1

        for indicator_item in self.buyindicator_list:
                if not indicator_item.do_fit(today_ind):
                   return False
        return True

    def fit_first_choice(self, pick_worker, choice_symbols, *args, **kwargs):
        raise NotImplementedError('PickRegressAng fit_first_choice unsupported now!')
