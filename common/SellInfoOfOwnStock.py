from Util.MailUtil import SendEmail
from Trade.Capital import Capital
from Trade.Order import Order
from CoreBase.Benchmark import Benchmark
from Trade.KLManager import KLManager
from Util import DbUtil, DateUtil
from Util.DateUtil import getn_date
import datetime
from FactorSell.FactorAtrNStop import FactorAtrNStop



g_stockinfo_map = {'REGN':{'date':20210806, 'price': 600.82},
            'INFO':{'date':20210806, 'price': 119.42},
            'TRI':{'date':20210809, 'price': 110.98},
            'MUFG':{'date':20210810, 'price': 5.46},
            'CVNA':{'date':20210810, 'price': 352.77},
            'CTVA':{'date':20210810, 'price': 45.18},
            'TRI':{'date':20210809, 'price': 110.98},
            'KSU':{'date':20210811, 'price': 293.5},
            'COF':{'date':20210812, 'price': 176.93},
            'NEE':{'date':20210813, 'price': 82.97},
            'CSX':{'date':20210813, 'price': 34.15},
            'SPLK':{'date':20210813, 'price': 147.57},
}


def CalcStockSellInfo(stockinfo_map, stop_win_n=6, stop_loss_n=2):
    start='2020-01-01'
    end = DateUtil.datetime_to_str(datetime.datetime.today())
    read_cash = 1000000
    benchmark = Benchmark(start=start, end=end)
    capital = Capital(read_cash, benchmark)
    kl_pd_manager = KLManager(benchmark, capital)
    stock_sellinfo_map = {}
    for key_symbol in stockinfo_map.keys():
        kl_pd = kl_pd_manager.get_pick_stock_kl_pd(key_symbol)

        cur_kl_pd = kl_pd[kl_pd['date'] < stockinfo_map[key_symbol]['date']]
        today_pd = cur_kl_pd.iloc[-1]
        cur_stock_map = FactorAtrNStop.calc_sell_price(today_pd, stockinfo_map[key_symbol]['price'], stop_win_n, stop_loss_n)
        stock_sellinfo_map[key_symbol] = cur_stock_map
    result_str = ''
    for key, value in stock_sellinfo_map.items():
        result_str += '{key}:{value}\n'.format(key=key, value=value)
    return(result_str)




if __name__ == "__main__":
    mail_title = '已买股票的止盈止损点'
    mail_content = CalcStockSellInfo(g_stockinfo_map, 6, 2)

    if(len(mail_content) > 0):
        SendEmail(mail_title, mail_content)

