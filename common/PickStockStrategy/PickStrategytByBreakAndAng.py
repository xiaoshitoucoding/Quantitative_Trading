from PickStock.PickBreakAndAng import PickBreakAndAng
from Trade.PickStockWorker import PickStockWorker
from Trade.Capital import Capital
from Trade.Order import Order
from CoreBase.Benchmark import Benchmark
from Trade.KLManager import KLManager
from Util import DbUtil, DateUtil
from PickStockStrategy.SellInfoForPickStock import CalcStratetySellInfo
from Util.MailUtil import SendEmail



def StrategyByBreakAndAng(capital, benchmark, kl_pd_manager, choice_symbols, xd=21):
    choice_symbols = choice_symbols[:500]
    mail_title = '今日推荐（突破）'
    mail_content = ''
    result_symbols = []
    for vol_rank in [0.8, 0.9, 1]:
        for threshold_ang_max in [1.0, 10.0, 45, 100.0]:
            cur_symbols, cur_content = PickStrategyByBreakAndAng(capital, benchmark, kl_pd_manager, choice_symbols, xd=xd, vol_rank_min=vol_rank, vol_rank_max=1, threshold_ang_max=threshold_ang_max)
            if(len(cur_symbols) > 0):
                mail_content += cur_content
                result_symbols += cur_symbols
    
    result_symbols = list(set(result_symbols))
    sellinfo_str = CalcStratetySellInfo.CalcSellAtrNStop(stock_list = result_symbols, kl_pd_manager = kl_pd_manager, xd=xd, stop_win_n =6, stop_loss_n=2)
    mail_content += '\n' + "#"*100 + '\n' + sellinfo_str
    if(len(result_symbols) > 0):
        SendEmail(mail_title, mail_content)


def PickStrategyByBreakAndAng(capital, benchmark, kl_pd_manager, choice_symbols, xd=21, vol_rank_min=0, vol_rank_max=1, threshold_ang_max=10.0):
    stock_pickers = [{'class' : PickBreakAndAng,
                        'xd': xd, 
                        'vol_rank_min': vol_rank_min,
                        'vol_rank_max': vol_rank_max,
                        'threshold_ang_min': 0.0, 
                        'threshold_ang_max': threshold_ang_max,
                        'reversed': False},
                        # {'class' : PickBreakAndAng,
                        # 'xd': 21, zx
                        # 'vol_days': 21, 
                        # 'vol_rank': 0.5,
                        # 'threshold_ang_min': 0.0, 
                        # 'threshold_ang_max': 10.0,
                        # 'reversed': False}
                        ]



    
    
    stock_pick = PickStockWorker(capital, benchmark, kl_pd_manager, 
        choice_symbols = choice_symbols, stock_pickers = stock_pickers)
    stock_pick.fit()
    print('=======================================================================================')
    # result_symbols = DbUtil.GetSortedStockByFinancialStock(stock_pick.choice_symbols)
    result_symbols = stock_pick.choice_symbols
    mail_content = ''
    if len(result_symbols) > 0:
        mail_content = str(stock_pickers) + '\n' + ',  '.join(result_symbols) 
    mail_content += '\n\n' + '='*100 + '\n'
    return result_symbols, mail_content
   
