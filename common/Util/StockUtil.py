import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import talib

#用来处理股票数据的类
class StockUtil:
    def __init__(self, stock_pd_data):
        self.m_stock_pd_data = stock_pd_data

    #用来获取移动平均线
    def GetMA(self, days):
        return self.m_stock_pd_data.close.rolling(days).mean()

    def GetGolderCross(self, short_days, long_days):
        short_ma = self.GetMA(short_days)
        long_ma = self.GetMA(long_days)
        s1 = short_ma < long_ma
        s2 = long_ma < short_ma
        return self.m_stock_pd_data[s1 & s2.shift(1)]


    def GetDeathCross(self, short_days, long_ma):
        short_ma = self.GetMA(short_days)
        long_ma = self.GetMA(long_ma)
        s1 = short_ma < long_ma
        s2 = long_ma < short_ma
        return self.m_stock_pd_data[~(s1 | s2.shift(1))]

    #使用talib计算atr，即透传talib.ATR计算结果
    def CalcATR(self, time_period=14):
        high = self.m_stock_pd_data.high
        low = self.m_stock_pd_data.low
        close = self.m_stock_pd_data.close
        atr = talib.ATR(high, low, close, timeperiod=time_period)
        return atr
