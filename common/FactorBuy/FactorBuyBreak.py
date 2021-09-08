# -*- encoding:utf-8 -*-
"""
    买入择时示例因子：突破买入择时因子
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from numpy import add

from FactorBuy.FactorBuyBase import FactorBuyBase, FactorBuyXD, BuyCallMixin, BuyPutMixin
from Indicator.NDVolume import _calc_today_volume_rank



# noinspection PyAttributeOutsideInit
class FactorBuyBreak(FactorBuyBase, BuyCallMixin):
    """示例正向突破买入择时类，混入BuyCallMixin，即向上突破触发买入event"""

    def _init_self(self, **kwargs):
        """kwargs中必须包含: 突破参数xd 比如20，30，40天...突破"""
        # 突破参数 xd， 比如20，30，40天...突破, 不要使用kwargs.pop('xd', 20), 明确需要参数xq
        # super._init_self(self, **kwargs)
        self.xd = kwargs['xd']
        self.vol_rank = kwargs['vol_rank']
        self.vol_daily = kwargs['vol_daily']
        # 在输出生成的orders_pd中显示的名字
        self.factor_name = '{}:{}'.format(self.__class__.__name__, self.xd)

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
        volumes = self.kl_pd.volume[-self.vol_daily:]
        today_vol_rank = _calc_today_volume_rank(volumes)
        # 今天的收盘价格达到xd天内最高价格则符合买入条件
        # if today.close == self.kl_pd.close[self.today_ind - self.xd + 1:self.today_ind + 1].max() and today.vol_rank >= self.vol_rank and yesterday.vol_rank < today.vol_rank:
        if today.close == self.kl_pd.close[self.today_ind - self.xd + 1:self.today_ind + 1].max() and today_vol_rank >= self.vol_rank:
            # 把突破新高参数赋值skip_days，这里也可以考虑make_buy_order确定是否买单成立，但是如果停盘太长时间等也不好
            self.skip_days = self.xd
            # 生成买入订单, 由于使用了今天的收盘价格做为策略信号判断，所以信号发出后，只能明天买
            return self.buy_tomorrow()
        return None


# noinspection PyAttributeOutsideInit
class FactorBuyXDBK(FactorBuyXD, BuyCallMixin):
    """示例继承FactorBuyXD完成正向突破买入择时类"""
    def fit_day(self, today):
        """
        针对每一个交易日拟合买入交易策略，寻找向上突破买入机会
        :param today: 当前驱动的交易日金融时间序列数据
        :return:
        """
        # 今天的收盘价格达到xd天内最高价格则符合买入条件
        if today.close == self.xd_kl.close.max():
            return self.buy_tomorrow()
        return None


# noinspection PyAttributeOutsideInit
class FactorBuyPutBreak(FactorBuyBase, BuyPutMixin):
    """示例反向突破买入择时类，混入BuyPutMixin，即向下突破触发买入event，详情请查阅期货回测示例demo"""

    def _init_self(self, **kwargs):
        """kwargs中必须包含: 突破参数xd 比如20，30，40天...突破"""

        # 突破参数 xd， 比如20，30，40天...突破, 不要使用kwargs.pop('xd', 20), 明确需要参数xq
        self.xd = kwargs['xd']
        self.factor_name = '{}:{}'.format(self.__class__.__name__, self.xd)

    def fit_day(self, today):
        """
        针对每一个交易日拟合买入交易策略，寻找向下突破买入机会
        :param today: 当前驱动的交易日金融时间序列数据
        :return:
        """
        # 忽略不符合买入的天（统计周期内前xd天）
        if self.today_ind < self.xd - 1:
            return None
        """
            与FactorBuyBreak区别就是买向下突破的，即min()
        """
        if today.close == self.kl_pd.close[self.today_ind - self.xd + 1:self.today_ind + 1].min():
            self.skip_days = self.xd
            return self.buy_tomorrow()
        return None


# noinspection PyAttributeOutsideInit
class FactorBuyPutXDBK(FactorBuyXD, BuyPutMixin):
    """示例继承FactorBuyXD完成反向突破买入择时类"""
    def fit_day(self, today):
        """
        针对每一个交易日拟合买入交易策略，寻找向上突破买入机会
        :param today: 当前驱动的交易日金融时间序列数据
        :return:
        """
        # 与FactorBuyBreak区别就是买向下突破的，即min()
        if today.close == self.xd_kl.close.min():
            return self.buy_tomorrow()
        return None
