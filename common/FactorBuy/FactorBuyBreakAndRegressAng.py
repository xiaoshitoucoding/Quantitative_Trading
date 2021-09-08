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
class FactorBuyBreakAndRegressAng(FactorBuyBase, BuyCallMixin):
    """示例正向突破买入择时类，混入BuyCallMixin，即向上突破触发买入event"""

    def _init_self(self, **kwargs):
        """kwargs中必须包含: 突破参数xd 比如20，30，40天...突破"""
        # 突破参数 xd， 比如20，30，40天...突破, 不要使用kwargs.pop('xd', 20), 明确需要参数xq
        # super._init_self(self, **kwargs)
        self.xd = kwargs['xd']
        
        self.buyindicator_list.append(BuyIndicatorFactory.AddVolumeRankBuyIndicator(**kwargs))
        self.buyindicator_list.append(BuyIndicatorFactory.AddRegressAngBuyIndicator(**kwargs))
        self.buyindicator_list.append(BuyIndicatorFactory.AddBreakBuyIndicator(**kwargs))
        
        # 在输出生成的orders_pd中显示的名字
        str_fator_name = "{name}:  xd:{xd}, vol_rank:{vol_rank}, vol_daily:{vol_daily}, threshold_ang_min:{threshold_ang_min}, threshold_ang_max:{threshold_ang_max}"
        self.factor_name = str_fator_name.format(name=self.__class__.__name__, xd=self.xd, vol_rank=kwargs['vol_rank'], \
            vol_daily=kwargs['vol_daily'], threshold_ang_min=kwargs['threshold_ang_min'], threshold_ang_max=kwargs['threshold_ang_max'])

    def fit_day(self, today):
        """
        针对每一个交易日拟合买入交易策略，寻找向上突破买入机会
        :param today: 当前驱动的交易日金融时间序列数据
        :return:
        """
        # 忽略不符合买入的天（统计周期内前xd天）
        if self.today_ind < self.xd - 1:
            return None

        yesterday = self.kl_pd.iloc[self.today_ind - 1]
     
        # 今天的收盘价格达到xd天内最高价格则符合买入条件
        # if today.close == self.kl_pd.close[self.today_ind - self.xd + 1:self.today_ind + 1].max() and today.vol_rank >= self.vol_rank and yesterday.vol_rank < today.vol_rank:
        # if today.close == self.kl_pd.close[self.today_ind - self.xd + 1:self.today_ind + 1].max():

        for indicator_item in self.buyindicator_list:
            if not indicator_item.do_fit(self.kl_pd, self.today_ind):
                return None
        # 把突破新高参数赋值skip_days，这里也可以考虑make_buy_order确定是否买单成立，但是如果停盘太长时间等也不好
        self.skip_days = self.xd
        # 生成买入订单, 由于使用了今天的收盘价格做为策略信号判断，所以信号发出后，只能明天买
        return self.buy_tomorrow()


