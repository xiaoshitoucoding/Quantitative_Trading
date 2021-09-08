from Util import DbUtil, DbTable
from CoreBase.StockPb import _make_kl_df
from CoreBase import Env

# g_plat300_map = {'sh.000908': '300能源',	
#                 'sh.000909': '300材料',	
#                 'sh.000910': '300工业',	
#                 'sh.000911': '300可选',	
#                 'sh.000912': '300消费',	
#                 'sh.000913': '300医药',
#                 'sh.000914': '300金融',
#                 'sh.000917': '300公用',
#                 }

def CalcChangeRateByStock(industry, stock_list, xd, result_data, mean_map):
    total_mean_pctchg = 0
    head_num = 0
    head_stock_map = {}
    for stock_item in stock_list:
        stock_pd, kl_key = _make_kl_df(stock_item)
        if stock_pd is None  or len(stock_pd) < xd:
            continue
        stock_mean = stock_pd.pctChg[-xd:].mean()
        total_mean_pctchg += stock_mean
        if head_num < 5:
            head_stock_map[stock_item] = stock_mean
            head_num += 1
    result_data[industry]['mean'] = total_mean_pctchg/len(stock_list)
    result_data[industry]['head'] = head_stock_map
    mean_map[industry] = total_mean_pctchg/len(stock_list)
    



def GetStockInfoByIndustry(xd = 1):
    Env.g_market_target = Env.EMarketTargetType.E_MARKET_TARGET_CN
    DbTable.select_table_name = DbTable.cn_stock_table_name
    DbTable.select_stock_data_columns = DbTable.cn_stock_data_columns
    industry_list = DbUtil.GetAllIndustryFromStockTable()
    result_data = {}
    mean_map = {}
    for industry_item in industry_list:
        stock_list = DbUtil.GetStockCodeByIndustry(industry=industry_item)
        sorted_stock_list = DbUtil.GetCNSortedStockByFinancialStock(stock_list)[:10]
        if len(sorted_stock_list) < 5:
            continue
        result_data[industry_item] = {}
        CalcChangeRateByStock(industry_item, stock_list, xd, result_data, mean_map)
    mean_map = sorted(mean_map.items(),key = lambda x:x[1],reverse = True)
    for industry in mean_map.keys():
        print('板块: {}  最近{}天的平均涨幅: {}  该板块市值排名前五的平均涨幅: \n'.format(industry, xd, result_data[industry]['mean']))
        for stock_item in result_data[industry]['head'].keys():
            print('     股票: {}   涨幅: {}'.format(stock_item, result_data[industry]['head'][stock_item]))
        print('===============================================================================')



