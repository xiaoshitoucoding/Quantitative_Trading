# -*- encoding:utf-8 -*-
"""
    买入择时示例因子：突破买入择时因子
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from Indicator.SimpleBuyIndicator import VolumeRankBuyIndicator, RegressAngBuyIndicator
from Indicator.BuyIndicatorFactory import BuyIndicatorFactory
from numpy import add
import numpy as np

from FactorBuy.FactorBuyBase import FactorBuyBase, FactorBuyXD, BuyCallMixin, BuyPutMixin
from Indicator.NDVolume import _calc_today_volume_rank
from Util import RegUtil



# noinspection PyAttributeOutsideInit
class FactorIndictorBuy(FactorBuyBase, BuyCallMixin):
    """示例正向突破买入择时类，混入BuyCallMixin，即向上突破触发买入event"""

    def _init_self(self, **kwargs):
        """kwargs中必须包含: 突破参数xd 比如20，30，40天...突破"""
        # 突破参数 xd， 比如20，30，40天...突破, 不要使用kwargs.pop('xd', 20), 明确需要参数xq
        # super._init_self(self, **kwargs)
    
        
        # self.buyindicator_list.append(BuyIndicatorFactory.AddMacdBuyIndicator(**kwargs))
        # self.buyindicator_list.append(BuyIndicatorFactory.AddMacdDivergenceIndicator(**kwargs))
        # self.buyindicator_list.append(BuyIndicatorFactory.AddVCPBuyFactor(**kwargs))
        self.buyindicator_list.append(BuyIndicatorFactory.AddIncreaseVolumeBuyIndicator(**kwargs))
        # self.buyindicator_list.append(BuyIndicatorFactory.AddCrossMeanBuyIndicator(**kwargs))
        self.short_xd = kwargs['short_xd']
        
        
        # # 在输出生成的orders_pd中显示的名字
        # str_fator_name = "{name}:  short_mean:{short_mean}, long_mean:{long_mean}"
        # self.factor_name = str_fator_name.format(name=self.__class__.__name__, xd=self.xd, vol_rank=kwargs['vol_rank'], \
        #     vol_daily=kwargs['vol_daily'], threshold_ang_min=kwargs['threshold_ang_min'], threshold_ang_max=kwargs['threshold_ang_max'])

    def fit_day(self, today):
        """
        针对每一个交易日拟合买入交易策略，寻找向上突破买入机会
        :param today: 当前驱动的交易日金融时间序列数据
        :return:
        """


        for indicator_item in self.buyindicator_list:
            if not indicator_item.do_fit(self.kl_pd, self.today_ind):
                return None
        # 生成买入订单, 由于使用了今天的收盘价格做为策略信号判断，所以信号发出后，只能明天买
        print(today)
        self.skip_days = self.short_xd
        return self.buy_tomorrow()


