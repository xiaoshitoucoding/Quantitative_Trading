from PickStock.PickStockIndicator import PickStockVCP
from PickStock.PickStockTrend import PickStockTrend, PickStockDownTrend, PickStockUpTrend, PickStockDownVolume
from Trade.PickStockWorker import PickStockWorker
from Trade.Capital import Capital
from Trade.Order import Order
from CoreBase.Benchmark import Benchmark
from Trade.KLManager import KLManager
from Util import DbUtil, DateUtil
from PickStockStrategy.SellInfoForPickStock import CalcStratetySellInfo
from Util.MailUtil import SendEmail

def StrategyByTrend(capital, benchmark, kl_pd_manager, choice_symbols, xd=5):
    choice_symbols = choice_symbols[:1500]
    mail_title = '今日推荐(长周期涨短周期跌)'
    mail_content = ''
    result_symbols = []
    
    cur_symbols, cur_content = PickStrategyByTrend(capital=capital, benchmark = benchmark, kl_pd_manager = kl_pd_manager, choice_symbols=choice_symbols)
    if(len(cur_symbols) > 0):
        mail_content += cur_content
        result_symbols += cur_symbols
    
    result_symbols = list(set(result_symbols))
    sellinfo_str = CalcStratetySellInfo.CalcSellAtrNStop(stock_list = result_symbols, kl_pd_manager = kl_pd_manager, xd=xd, stop_win_n =4, stop_loss_n=2)
    mail_content += '\n' + "#"*100 + '\n' + sellinfo_str
    if(len(result_symbols) > 0):
        print(mail_content)
        # SendEmail(mail_title, mail_content)


def PickStrategyByTrend(capital, benchmark, kl_pd_manager, choice_symbols, xd=20, vol_rank_min = -1, vol_rank_max=-0.5, past_factor=6, up_deg_threshold=3):
    stock_pickers = [{'class' : PickStockTrend,
                        'xd': xd,
                        'past_factor': past_factor,
                        'up_deg_threshold': up_deg_threshold, 
                        'vol_rank_min': vol_rank_min, 
                        'vol_rank_max': vol_rank_max, 
                        'reversed': False},               
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
   
##################################################################################################
##################################################################################################
##################################################################################################

def StrategyByDownTrend(capital, benchmark, kl_pd_manager, choice_symbols, xd=10):
    choice_symbols = choice_symbols[:1000]
    mail_title = '今日推荐(缩量下跌)'
    mail_content = ''
    result_symbols = []
    
    cur_symbols, cur_content = PickStrategyByDownTrend(capital=capital, benchmark = benchmark, kl_pd_manager = kl_pd_manager, choice_symbols=choice_symbols, xd=xd)
    if(len(cur_symbols) > 0):
        mail_content += cur_content
        result_symbols += cur_symbols
    
    result_symbols = list(set(result_symbols))
    sellinfo_str = CalcStratetySellInfo.CalcSellAtrNStop(stock_list = result_symbols, kl_pd_manager = kl_pd_manager, xd=xd, stop_win_n =4, stop_loss_n=2)
    mail_content += '\n' + "#"*100 + '\n' + sellinfo_str
    if(len(result_symbols) > 0):
        SendEmail(mail_title, mail_content)


def PickStrategyByDownTrend(capital, benchmark, kl_pd_manager, choice_symbols, xd=20, vol_rank_min = -1, vol_rank_max=0, up_deg_threshold=3, decre_days=3):
    stock_pickers = [{'class' : PickStockDownTrend,
                        'xd': xd,
                        'vol_rank_min': vol_rank_min, 
                        'vol_rank_max': vol_rank_max, 
                        'up_deg_threshold': up_deg_threshold, 
                        'decre_days': decre_days,
                        'reversed': False},               
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



##################################################################################################
##################################################################################################
##################################################################################################

def StrategyByUpTrend(capital, benchmark, kl_pd_manager, choice_symbols):
    choice_symbols = choice_symbols[:1000]
    mail_title = '今日推荐(持续上涨)'
    mail_content = ''
    result_symbols = []
    xd = 50
    for xd in [30, 60, 120, 240]:
        for up_deg_threshold in [30, 45, 60]:
            cur_symbols, cur_content = PickStrategyByUpTrend(capital=capital, benchmark = benchmark, kl_pd_manager = kl_pd_manager, choice_symbols=choice_symbols, xd=xd, up_deg_threshold=up_deg_threshold)
            if(len(cur_symbols) > 0):
                mail_content += cur_content
                result_symbols += cur_symbols
   
    
    result_symbols = list(set(result_symbols))
    sellinfo_str = CalcStratetySellInfo.CalcSellAtrNStop(stock_list = result_symbols, kl_pd_manager = kl_pd_manager, xd=xd, stop_win_n =4, stop_loss_n=2)
    mail_content += '\n' + "#"*100 + '\n' + sellinfo_str
    if(len(result_symbols) > 0):
        SendEmail(mail_title, mail_content)


def PickStrategyByUpTrend(capital, benchmark, kl_pd_manager, choice_symbols, xd=20, up_deg_threshold=3):
    stock_pickers = [{'class' : PickStockUpTrend,
                        'xd': xd,
                        'up_deg_threshold': up_deg_threshold, 
                        'reversed': False},               
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


##################################################################################################
##################################################################################################
##################################################################################################

def StrategyByDownVolume(capital, benchmark, kl_pd_manager, choice_symbols):
    choice_symbols = choice_symbols[:500]
    mail_title = '三角形态(VCP)'
    mail_content = ''
    result_symbols = []
    xd = 50
    for xd in [5]:
        for up_deg_threshold in [3]:
            cur_symbols, cur_content = PickStrategyByUpTrend(capital=capital, benchmark = benchmark, kl_pd_manager = kl_pd_manager, choice_symbols=choice_symbols, xd=xd, up_deg_threshold=up_deg_threshold)
            if(len(cur_symbols) > 0):
                mail_content += cur_content
                result_symbols += cur_symbols
   
    
    result_symbols = list(set(result_symbols))
    sellinfo_str = CalcStratetySellInfo.CalcSellAtrNStop(stock_list = result_symbols, kl_pd_manager = kl_pd_manager, xd=xd, stop_win_n =4, stop_loss_n=2)
    mail_content += '\n' + "#"*100 + '\n' + sellinfo_str
    if(len(result_symbols) > 0):
        SendEmail(mail_title, mail_content)


def PickStrategyByDownVolume(capital, benchmark, kl_pd_manager, choice_symbols, xd=20, up_deg_threshold=3):
    stock_pickers = [{'class' : PickStockDownVolume,
                        'xd': xd,
                        'up_deg_threshold': up_deg_threshold, 
                        'reversed': False},               
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





##################################################################################################
##################################################################################################
##################################################################################################

def StrategyByVCP(capital, benchmark, kl_pd_manager, choice_symbols):
    choice_symbols = choice_symbols[:400]
    mail_title = '三角形态(VCP)'
    mail_content = ''
    result_symbols = []
    xd = 50
    for xd in [5]:
        for up_deg_threshold in [3]:
            cur_symbols, cur_content = PickStrategyByVCP(capital=capital, benchmark = benchmark, kl_pd_manager = kl_pd_manager, choice_symbols=choice_symbols, xd=xd, up_deg_threshold=up_deg_threshold)
            if(len(cur_symbols) > 0):
                mail_content += cur_content
                result_symbols += cur_symbols
   
    
    result_symbols = list(set(result_symbols))
    sellinfo_str = CalcStratetySellInfo.CalcSellAtrNStop(stock_list = result_symbols, kl_pd_manager = kl_pd_manager, xd=xd, stop_win_n =4, stop_loss_n=2)
    mail_content += '\n' + "#"*100 + '\n' + sellinfo_str
    if(len(result_symbols) > 0):
        SendEmail(mail_title, mail_content)
        print(mail_content)


def PickStrategyByVCP(capital, benchmark, kl_pd_manager, choice_symbols, xd=20, up_deg_threshold=3):
    stock_pickers = [{'class' : PickStockVCP,
                        'xd': xd,
                        'up_deg_threshold': up_deg_threshold, 
                        'reversed': False},               
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
