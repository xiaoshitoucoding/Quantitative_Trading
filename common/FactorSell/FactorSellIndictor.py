# -*- encoding:utf-8 -*-
"""
    卖出择时示例因子：突破卖出择时因子
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from FactorSell.FactorSellBase import FactorSellBase, FactorSellXD, ESupportDirection
from Indicator.SellIndicatorFactory import SellIndicatorFactory



class FactorSellIndictor(FactorSellBase):
    """示例向下突破卖出择时因子"""

    def _init_self(self, **kwargs):
        self.sellindicator_list.append(SellIndicatorFactory.AddMacdSellIndicator(**kwargs))


    def support_direction(self):
        """支持的方向，只支持正向"""
        return [ESupportDirection.DIRECTION_CAll.value]

    def fit_day(self, today, orders):
       
        # 满足一个条件就卖
        sell_flag = False
        for indicator_item in self.sellindicator_list:
            if indicator_item.do_fit(self.kl_pd, self.today_ind):
                sell_flag = True
        if sell_flag:
            for order in orders:        
                self.sell_tomorrow(order)
            


