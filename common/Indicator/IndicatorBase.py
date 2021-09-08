
from abc import abstractmethod

class IndicatorBase(object):
    # def __init__(self, kwargs):



    @abstractmethod
    def do_fit(self, today_ind):
        raise NotImplementedError()


    def past_today_kl(self, kl_pd, today, past_day_cnt):
        """
            在fit_day, fit_month, fit_week等时间驱动经过的函数中通过传递今天的数据
            获取过去past_day_cnt天的交易日数据，返回为pd.DataFram数据
            :param today: 当前驱动的交易日金融时间序列数据
            :param past_day_cnt: int，获取今天之前过去past_day_cnt天的金融时间序列数据
        """
        end_ind = kl_pd[kl_pd.date == today.date].key.values[0]
        start_ind = end_ind - past_day_cnt if end_ind - past_day_cnt > 0 else 0
        # 根据当前的交易日，切片过去一段时间金融时间序列
        return self.kl_pd.iloc[start_ind:end_ind]

    def past_todayind_kl(self, kl_pd, today_ind, past_day_cnt):
       
        start_ind = today_ind - past_day_cnt if today_ind - past_day_cnt >0 else 0
        # 根据当前的交易日，切片过去一段时间金融时间序列
        return kl_pd.iloc[start_ind:today_ind]