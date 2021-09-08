from numpy import fabs
from Indicator.IndicatorBase import IndicatorBase
from Indicator.NDVolume import _calc_today_volume_rank
from Indicator.NDMacd import _calc_macd_from_ta
from CoreBase.PdHelper import pd_rolling_mean
import pandas as pd
from Util import RegUtil


class MacdSellIndicator(IndicatorBase):
    def __init__(self, kwargs):
        self.short_arg = kwargs['short_arg']
        self.long_arg = kwargs['long_arg']

    def do_fit(self, kl_pd, today_ind):
        dif, dea, hist = _calc_macd_from_ta(kl_pd.close, self.short_arg, self.long_arg)
        self.macd_df = pd.DataFrame({'dif':dif[33:],'dea':dea[33:],'hist':hist[33:]},
                       index=kl_pd['date'][33:],columns=['dif','dea','hist'])
        if today_ind < 1:
            return False
        #MACD死叉
        try:
            if ((self.macd_df.iloc[today_ind-1,0]>=self.macd_df.iloc[today_ind-1,1]) & (self.macd_df.iloc[today_ind,0]<=self.macd_df.iloc[today_ind,1])):
                # print("MACD死叉的日期："+ str(self.macd_df.index[today_ind]))
                return True
            return False
        except:
            return False
    