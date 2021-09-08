from datetime import time
from PickStock.PickStockIndicator import PickStockMacdDivergence, PickStockIncreaseVolume, PickStockChiliPepper
from Trade.PickStockWorker import PickStockWorker
from Trade.Capital import Capital
from Trade.Order import Order
from CoreBase.Benchmark import Benchmark
from Trade.KLManager import KLManager
from Util import DbUtil, DateUtil
from PickStockStrategy.SellInfoForPickStock import CalcStratetySellInfo
from Util.MailUtil import SendEmail

def StrategyByMacdDivergence(capital, benchmark, kl_pd_manager, choice_symbols, xd=10):
    choice_symbols = choice_symbols[:1000]
    mail_title = ''
    mail_content = ''
    result_symbols = []
    
    cur_symbols, cur_content = PickStrategyByMacdDivergence(capital=capital, benchmark = benchmark, kl_pd_manager = kl_pd_manager, choice_symbols=choice_symbols, xd=xd)
    if(len(cur_symbols) > 0):
        mail_content += cur_content
        result_symbols += cur_symbols
    
    result_symbols = list(set(result_symbols))
    sellinfo_str = CalcStratetySellInfo.CalcSellAtrNStop(stock_list = result_symbols, kl_pd_manager = kl_pd_manager, xd=xd, stop_win_n =4, stop_loss_n=2)
    mail_content += '\n' + "#"*100 + '\n' + sellinfo_str
    if(len(result_symbols) > 0):
        SendEmail(mail_title, mail_content)


def PickStrategyByMacdDivergence(capital, benchmark, kl_pd_manager, choice_symbols, xd=20, vol_rank_min = -1, vol_rank_max=-0.8, past_factor=6, up_deg_threshold=3):
    stock_pickers = [{'class' : PickStockMacdDivergence,
                        'xd': xd,    
                     }        
                        ]
    
    stock_pick = PickStockWorker(capital, benchmark, kl_pd_manager, 
        choice_symbols = choice_symbols, stock_pickers = stock_pickers)
    stock_pick.fit()
    print('=======================================================================================')
    result_symbols = DbUtil.GetSortedStockByFinancialStock(stock_pick.choice_symbols)
    mail_content = ''
    if len(result_symbols) > 0:
        mail_content = str(stock_pickers) + '\n' + ',  '.join(result_symbols) 
    print(result_symbols)
    mail_content += '\n\n' + '='*100 + '\n'
    return result_symbols, mail_content



##############################################################################################
##############################################################################################
##############################################################################################



def StrategyByIncreaseVolume(capital, benchmark, kl_pd_manager, choice_symbols, long_xd=60, short_xd = 5, times = 5, price_min = 1, price_max=1.1):
    # choice_symbols = choice_symbols[:1]
    mail_title = ''
    mail_content = ''
    result_symbols = []
    
    cur_symbols, cur_content = PickStrategyByIncreaseVolume(capital=capital, benchmark = benchmark, kl_pd_manager = kl_pd_manager,\
         choice_symbols=choice_symbols, long_xd=long_xd, short_xd = short_xd, times= times, price_min = price_min, price_max=price_max)
    # if(len(cur_symbols) > 0):
    #     mail_content += cur_content
    #     result_symbols += cur_symbols
    
    # result_symbols = list(set(result_symbols))
    # sellinfo_str = CalcStratetySellInfo.CalcSellAtrNStop(stock_list = result_symbols, kl_pd_manager = kl_pd_manager, xd=short_xd, stop_win_n =4, stop_loss_n=2)
    # mail_content += '\n' + "#"*100 + '\n' + sellinfo_str
    # if(len(result_symbols) > 0):
    #     # SendEmail(mail_title, mail_content)
    #     print(mail_content)


def PickStrategyByIncreaseVolume(capital, benchmark, kl_pd_manager, choice_symbols, long_xd=60, short_xd = 5, times=5, price_times = 1.5):
    stock_pickers = [{'class' : PickStockIncreaseVolume,
                        'long_xd': long_xd,    
                        'short_xd': short_xd,    
                        'times': times,
                        'price_times': price_times,
                     }        
                        ]
    print('==================================运行结果======================================')
    
    stock_pick = PickStockWorker(capital, benchmark, kl_pd_manager, 
        choice_symbols = choice_symbols, stock_pickers = stock_pickers)
    stock_pick.fit()
    print('=======================================================================================')
    # result_symbols = DbUtil.GetSortedStockByFinancialStock(stock_pick.choice_symbols)
    result_symbols = stock_pick.choice_symbols
    mail_content = ''
    # if len(result_symbols) > 0:
    #     mail_content = str(stock_pickers) + '\n' + ',  '.join(result_symbols) 
    # # print(result_symbols)
    # mail_content += '\n\n' + '='*100 + '\n'
    return result_symbols, mail_content
   




###########################################################################################################################################################
def PickStrategyByChilliPepper(capital, benchmark, kl_pd_manager, choice_symbols, xd=60, up_deg_threshold = 10):
    stock_pickers = [{'class' : PickStockChiliPepper,
                        'xd': xd,    
                        'up_deg_threshold': up_deg_threshold, 
                     }        
                        ]
    print('==================================运行结果======================================')
    
    stock_pick = PickStockWorker(capital, benchmark, kl_pd_manager, 
        choice_symbols = choice_symbols, stock_pickers = stock_pickers)
    stock_pick.fit()
    print('=======================================================================================')
    # result_symbols = DbUtil.GetSortedStockByFinancialStock(stock_pick.choice_symbols)
    result_symbols = stock_pick.choice_symbols
    print(result_symbols)
    mail_content = ''
    # if len(result_symbols) > 0:
    #     mail_content = str(stock_pickers) + '\n' + ',  '.join(result_symbols) 
    # # print(result_symbols)
    # mail_content += '\n\n' + '='*100 + '\n'
    return result_symbols, mail_content
