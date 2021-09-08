from typing import Tuple
from numpy import fabs
from Indicator.IndicatorBase import IndicatorBase
from Indicator.NDVolume import _calc_today_volume_rank, _calc_rank
from Indicator.NDMacd import _calc_macd_from_ta
from Indicator.NDRsi import _calc_rsi_from_ta
from Indicator.NDBoll import _calc_boll_from_ta
from CoreBase.PdHelper import pd_rolling_mean, pd_rolling_max, pd_rolling_min
import pandas as pd
from Util import RegUtil
from TLine.TLine import TLine
import numpy as np


class VolumeRankBuyIndicator(IndicatorBase):
    def __init__(self, kwargs):
        self.xd = kwargs['xd']
        self.vol_rank_max = kwargs['vol_rank_max']
        self.vol_rank_min = kwargs['vol_rank_min']
    

    def do_fit(self, kl_pd, today_ind):
        volumes = kl_pd.volume[today_ind-self.xd+1:today_ind+1]
        if len(volumes) == 0:
            return False
        today_vol_rank = _calc_today_volume_rank(volumes)
        if today_vol_rank >= self.vol_rank_min and today_vol_rank <= self.vol_rank_max:
            return True
        return False

class IncreaseVolumeBuyIndicator(IndicatorBase):
    def __init__(self, kwargs):
        self.long_xd = kwargs['long_xd']
        self.short_xd = kwargs['short_xd']
        self.times = kwargs['times']
        self.price_times = kwargs['price_times']
    

    def do_fit(self, kl_pd, today_ind):
        if today_ind < self.long_xd:
            return False
        short_volumes = kl_pd.volume[today_ind-self.short_xd+1:today_ind+1].mean()
        long_volumes = kl_pd.volume[today_ind-self.short_xd - self.long_xd+1:today_ind-self.short_xd+1].mean()
        short_prices = kl_pd.close[today_ind-self.short_xd+1:today_ind+1].mean()
        long_prices = kl_pd.close[today_ind-self.short_xd - self.long_xd+1:today_ind-self.short_xd+1].mean()
        # print('short_volumes', short_volumes)
        # print('long_volumes', long_volumes)
        # print('short_prices', short_prices)
        # print('long_prices', long_prices)
        # print('result', short_volumes/long_volumes)
        long_price_min = long_prices * self.price_times
        volumes_times = short_volumes/long_volumes
        if  long_price_min <= short_prices  and  self.times > 0 and volumes_times > self.times:
            print('股票ID:{}  短期平均成交量大于长期的倍数: {}'.format(kl_pd.code[0], volumes_times))
            return True
        elif  long_price_min <= short_prices and  self.times < 0 and volumes_times < (-self.times):
            print('股票ID:{}  短期平均成交量小于长期的倍数: {}'.format(kl_pd.code[0], volumes_times))
            return True
        return False
        

class RegressAngBuyIndicator(IndicatorBase):
    def __init__(self, kwargs):
        self.xd = kwargs['xd']
        self.threshold_ang_min = kwargs['threshold_ang_min']
        self.threshold_ang_max = kwargs['threshold_ang_max']


    def do_fit(self, kl_pd, today_ind):
        ang_close = kl_pd.close[today_ind-self.xd+1:today_ind+1]
        if len(ang_close) == 0:
            return False
        ang = RegUtil.calc_regress_deg(ang_close, show=False)
        if self.threshold_ang_min < ang < self.threshold_ang_max:
            return True
        return False


class CrossMeanBuyIndicator(IndicatorBase):
    def __init__(self, kwargs):
        
        self.short_arg = kwargs['short_arg']
        self.long_arg = kwargs['long_arg']

    def cross(self, short_mean_pd,long_mean_pd):
        '''
        判断短时均线和长时均线的关系。

        Args:
            short_arg 短时均线，长度不应小于3
            long_arg  长时均线，长度不应小于3。

        Returns:
            1 短时均线上穿长时均线
            0 短时均线和长时均线未发生交叉
            -1 短时均线下穿长时均线
        '''
        
        if len(short_mean_pd) < 3 or len(long_mean_pd) < 3:
            return 0
        delta = short_mean_pd[-3:] - long_mean_pd[-3:]
        if (delta[-1] > 0) and ((delta[-2] < 0) or ((delta[-2] == 0) and (delta[-3] < 0))):
            return 1
        elif (delta[-1] < 0) and ((delta[-2] > 0) or ((delta[-2] == 0) and (delta[-3] > 0))):
            return -1
        return 0

    def do_fit(self, kl_pd, today_ind):
        print(today_ind)
        if today_ind < self.long_arg:
            return False
        # kl_close = kl_pd.close[:today_ind]
        # # 长时均线
        # long_mean_pd  = pd_rolling_mean(kl_close, window=self.long_arg, min_periods=self.long_arg)
        # # 短时均线
        # short_mean_pd = pd_rolling_mean(kl_close, window=self.short_arg, min_periods=self.short_arg)

        # # 短时均线上穿长时均线时买入
        # if (self.cross(long_mean_pd,short_mean_pd) > 0):
        #     return True
        # return False

        for i in range(50):
            index = today_ind-i
            print(index)
            kl_close = kl_pd.close[:index]
            # 长时均线
            long_mean_pd  = pd_rolling_mean(kl_close, window=self.long_arg, min_periods=self.long_arg)
            # 短时均线
            short_mean_pd = pd_rolling_mean(kl_close, window=self.short_arg, min_periods=self.short_arg)

            # 短时均线上穿长时均线时买入
            if (self.cross(long_mean_pd,short_mean_pd) > 0):
                return True
            return False


class MacdBuyIndicator(IndicatorBase):
    def __init__(self, kwargs):
        self.short_arg = kwargs['short_arg']
        self.long_arg = kwargs['long_arg']

    def do_fit(self, kl_pd, today_ind):

        dif, dea, hist = _calc_macd_from_ta(kl_pd.close, self.short_arg, self.long_arg)
        self.macd_df = pd.DataFrame({'dif':dif[33:],'dea':dea[33:],'hist':hist[33:]},
                       index=kl_pd['date'][33:],columns=['dif','dea','hist'])
        if today_ind < 1:
            return False
        #MACD金叉
        try:
            if ((self.macd_df.iloc[today_ind-1,0]<=self.macd_df.iloc[today_ind-1,1]) & (self.macd_df.iloc[today_ind,0]>=self.macd_df.iloc[today_ind,1])):
                # print("MACD金叉的日期："+ str(self.macd_df.index[today_ind]))
                return True
            return False
        except:
            return False


class MacdDivergenceIndicator(IndicatorBase):
    def __init__(self, kwargs):
        self.xd = kwargs['xd']
        self.short_arg = kwargs['short_arg']
        self.long_arg = kwargs['long_arg']

    def do_fit(self, kl_pd, today_ind):
        if today_ind <= self.xd:
            return False

        dif, dea, hist = _calc_macd_from_ta(kl_pd.close, self.short_arg, self.long_arg)
        xd_macd = dea[today_ind - self.xd+1:today_ind+1]
        xd_close = kl_pd.close[today_ind - self.xd+1:today_ind+1]
        if np.isnan(xd_macd).sum() > 0 or np.isnan(xd_close).sum() > 0:
            return False
        if kl_pd.close[today_ind] != xd_close.min():
            return False
        xd_macd_ang = RegUtil.calc_regress_deg(xd_macd, show=False)
        xd_close_ang = RegUtil.calc_regress_deg(xd_close, show=False)
        if xd_close_ang < -3 and xd_macd_ang > 3:
            return True
        return False
       


class RsiBuyIndicator(IndicatorBase):
    def __init__(self, kwargs):
        self.rsi = kwargs['rsi']


    def do_fit(self, kl_pd, today_ind):
        if today_ind < 1:
            return False
        kl_close = kl_pd.close[:today_ind]
        
        if self.rsi <= _calc_rsi_from_ta(kl_close):
            return True
        return False


class BreakBuyIndicator(IndicatorBase):
    def __init__(self, kwargs):
        self.xd = kwargs['xd']


    def do_fit(self, kl_pd, today_ind):
        if today_ind - self.xd < 0:
            return False
        try:
            if kl_pd.close[today_ind] == kl_pd.close[today_ind - self.xd+1:today_ind+1].max():
                return True
        except:
            print(kl_pd, 'is error')
            return False
        return False



class UpDownTrendFactor(IndicatorBase):
    def __init__(self, kwargs):
        self.xd = kwargs['xd']
        self.past_factor = kwargs['past_factor']
        self.up_deg_threshold = kwargs['up_deg_threshold']


    def do_fit(self, kl_pd, today_ind):
        long_days = self.past_factor * self.xd
        today = kl_pd.iloc[today_ind]
        if today_ind < self.xd -1:
            return False


        long_kl = self.past_todayind_kl(kl_pd, today_ind, long_days)
        xd_kl = kl_pd[today_ind - self.xd + 1:today_ind + 1]
        long_ang = RegUtil.calc_regress_deg(long_kl.close, show=False)
        # 判断长周期是否属于上涨趋势
        if long_ang > self.up_deg_threshold:
            # 今天收盘价为最近xd天内最低价格，且短线xd天的价格走势为下跌趋势
            # if today.close == xd_kl.close.min() and TLine(
            #     xd_kl.close, 'short').is_down_trend(down_deg_threshold=-self.up_deg_threshold, show=False):
            short_ang = RegUtil.calc_regress_deg(xd_kl.close, show=False)
            if short_ang < -self.up_deg_threshold:
                return True
        return False



class DownTrendFactor(IndicatorBase):
    def __init__(self, kwargs):
        self.xd = kwargs['xd']
        self.up_deg_threshold = kwargs['up_deg_threshold']
    def do_fit(self, kl_pd, today_ind):
        today = kl_pd.iloc[today_ind]
        if today_ind < self.xd -1:
            return False
        xd_kl = kl_pd[today_ind - self.xd:today_ind]
        # 判断长周期是否属于上涨趋势
        if TLine(xd_kl.close, 'long').is_down_trend(down_deg_threshold=-self.up_deg_threshold, show=False):
            # 今天收盘价为最近xd天内最低价格，且短线xd天的价格走势为下跌趋势
                return True
        
        # if today.close == xd_kl.close.min() and TLine(
        #         xd_kl.close, 'short').is_down_trend(down_deg_threshold=-self.up_deg_threshold, show=False):
        #     # 今天收盘价为最近xd天内最低价格，且短线xd天的价格走势为下跌趋势
        #         return True
        return False

class DownVolumeFactor(IndicatorBase):
    def __init__(self, kwargs):
        self.xd = kwargs['xd']
        self.up_deg_threshold = kwargs['up_deg_threshold']
    def do_fit(self, kl_pd, today_ind):
        today = kl_pd.iloc[today_ind]
        if today_ind < self.xd -1:
            return False
        xd_kl = kl_pd[today_ind - self.xd + 1:today_ind + 1]
        # 判断长周期是否属于上涨趋势
        if TLine(xd_kl.volume, 'long').is_down_trend(down_deg_threshold=-self.up_deg_threshold, show=False):
            # 今天收盘价为最近xd天内最低价格，且短线xd天的价格走势为下跌趋势
                return True
        
        # if today.close == xd_kl.close.min() and TLine(
        #         xd_kl.close, 'short').is_down_trend(down_deg_threshold=-self.up_deg_threshold, show=False):
        #     # 今天收盘价为最近xd天内最低价格，且短线xd天的价格走势为下跌趋势
        #         return True
        return False



class DownUpFactor(IndicatorBase):
    def __init__(self, kwargs):
        self.xd = kwargs['xd']
        self.up_deg_threshold = kwargs['up_deg_threshold']
    def do_fit(self, kl_pd, today_ind):
        today = kl_pd.iloc[today_ind]
        if today_ind < self.xd -1:
            return False
        xd_kl = kl_pd[today_ind - self.xd + 1:today_ind + 1]
        # 判断长周期是否属于上涨趋势
        if TLine(xd_kl.close, 'long').is_down_trend(down_deg_threshold=-self.up_deg_threshold, show=False):
            # 今天收盘价为最近xd天内最低价格，且短线xd天的价格走势为下跌趋势
                return True
        
        # if today.close == xd_kl.close.min() and TLine(
        #         xd_kl.close, 'short').is_down_trend(down_deg_threshold=-self.up_deg_threshold, show=False):
        #     # 今天收盘价为最近xd天内最低价格，且短线xd天的价格走势为下跌趋势
        #         return True
        return False
    

class UpTrendFactor(IndicatorBase):
    def __init__(self, kwargs):
        self.xd = kwargs['xd']
        self.up_deg_threshold = kwargs['up_deg_threshold']
    def do_fit(self, kl_pd, today_ind):
        today = kl_pd.iloc[today_ind]
        if today_ind < self.xd -1:
            return False
        xd_kl = kl_pd[today_ind - self.xd + 1:today_ind + 1]
        # 判断长周期是否属于上涨趋势
        if TLine(xd_kl.close, 'long').is_up_trend(up_deg_threshold=self.up_deg_threshold, show=False):
            # 今天收盘价为最近xd天内最低价格，且短线xd天的价格走势为下跌趋势
                return True
        return False

class DecrementFactor(IndicatorBase):
    def __init__(self, kwargs):
        self.xd = kwargs['xd']
        self.decre_days = kwargs['decre_days']
        self.vol_rank_max = kwargs['vol_rank_max']
        self.vol_rank_min = kwargs['vol_rank_min']

    def do_fit(self, kl_pd, today_ind):
        today = kl_pd.iloc[today_ind]
        if today_ind < self.decre_days -1:
            return False
        decre_kl = kl_pd[today_ind - self.xd + 1:today_ind + 1]
        decre_volume_rank = _calc_rank(decre_kl.volume)
        # decre_pricerate_rank = _calc_rank(decre_kl.price_rate.abs())
        for index in range(1, self.decre_days +1):
            # if not (self.vol_rank_min <= decre_volume_rank[-index] <= self.vol_rank_max  and self.vol_rank_min <= decre_pricerate_rank[-index] <= self.vol_rank_max):
            if not (self.vol_rank_min <= decre_volume_rank[-index] <= self.vol_rank_max):
                return False
        return True


class BollBuyFactor(IndicatorBase):
    def __init__(self, kwargs):
        self.xd = kwargs['xd']


    def do_fit(self, kl_pd, today_ind):
        today = kl_pd.iloc[today_ind]
        if today_ind < self.xd -1:
            return False
        xd_price = kl_pd[:today_ind+1].close
        upper, middle, lower = _calc_boll_from_ta(xd_price, self.xd)

        if today.close >= upper[-1]:
            return True
        return False

class ChiliPepper(IndicatorBase):
    def __init__(self, kwargs):
        self.xd = kwargs['xd']

    def do_fit(self, kl_pd, today_ind):
        if today_ind < 30:
            return False
        today = kl_pd.iloc[today_ind]
        kl_close = kl_pd.close
        kl_before_volume = kl_pd.volume[-2]
        # mean_5days  = kl_pd[-5:].close
        mean_10days  = kl_close[-10:].mean()
        mean_30days  = kl_close[-30:].mean()
        # print('codeid', today.code)
        # print('today.close', today.close)
        # print('mean_10days', mean_10days)
        # print('mean_30days', mean_30days)
        if today.volume > kl_before_volume * 2\
            and today.close > mean_10days and today.close > mean_30days:
            return True

        return False





class VCPBuyFactor(IndicatorBase):
    def __init__(self, kwargs):
        self.xd = kwargs['xd']


    def do_fit(self, kl_pd, today_ind):
        today = kl_pd.iloc[today_ind]
        if today_ind < self.xd -1:
            return False
        xd_pd = kl_pd[:today_ind+1]
        xd_high = xd_pd.high
        xd_low = xd_pd.low
        window = self.xd
        xd_high_max = pd_rolling_max(xd_high, window=window)
        xd_low_min = pd_rolling_min(xd_low, window=window)
        upper_extre = []
        low_extre = []
        for i in range(2,len(xd_pd)-1-window):
            if xd_high[-i] == xd_high_max[-i] \
                and (xd_high[-i-1] < xd_high[-i] and xd_high[-i+1] < xd_high[-i]):
                upper_extre.append(-i)
            
            if len(upper_extre) > 3:
                break
        if len(upper_extre) < 3:
            return False
        upper_range_start = np.array(upper_extre).min()
        range_vloumes = xd_pd.volume[upper_range_start:today_ind+1]
        if RegUtil.calc_regress_deg(range_vloumes) > 0:
            return False
        for i in range(-2, upper_range_start, -1):
            if xd_low[i] == xd_low_min[i] \
                and (xd_low[i-1] > xd_low[i] and xd_low[i+1] > xd_low[i]):
                low_extre.append(i)

        if len(low_extre) < 3:
            return False
        upper_extre.reverse()
        low_extre.reverse()
        upper_extre_value = np.array([xd_high[i] for i in upper_extre])
        low_extre_value = np.array([xd_low[i] for i in low_extre])
        # print('upper_extre_value', upper_extre_value)
        # print('low_extre_value', low_extre_value)
        upper_ang = RegUtil.calc_regress_deg(upper_extre_value)
        low_ang = RegUtil.calc_regress_deg(low_extre_value)
        
        # print([xd_pd.iloc[i] for i in low_extre])
        if upper_ang < 0 and low_ang > 0:
            # print('upper_ang', upper_ang)
            # print('low_ang', low_ang)
            # print([xd_pd.iloc[i] for i in upper_extre])
            return True
        return False
        



        
