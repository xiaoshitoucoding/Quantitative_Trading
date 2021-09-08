
from FactorSell.FactorAtrNStop import FactorAtrNStop
class CalcStratetySellInfo():   
    @staticmethod
    def CalcSellAtrNStop(stock_list, kl_pd_manager, xd, stop_win_n, stop_loss_n):
        stock_sellinfo_map = {}
        for stock in stock_list:
            kl_pd = kl_pd_manager.get_pick_stock_kl_pd(stock, xd, xd/2)
            today_pd = kl_pd.iloc[-1]
            cur_stock_map = FactorAtrNStop.calc_sell_price(today_pd, today_pd.close, stop_win_n, stop_loss_n)
            stock_sellinfo_map[stock] = cur_stock_map
        result_str = ''
        for key, value in stock_sellinfo_map.items():
            result_str += '{key}:{value}\n'.format(key=key, value=value)
        return(result_str)






