from CoreBase.StockPb import make_kl_df
from CoreBase.Benchmark import *
from CoreBase.Parallel import Parallel, delayed
from futu import *
from FutuOpenDUtil import StockPolygon, UsaNoFinancialStock, CNBaoStock
from Util import DbUtil
from Util.DateUtil import getn_date, diffdays_between, GetToday, GetAfterNDayBydate, GetTomorrow
import time
import sys



cmd_str = ''
if len(sys.argv)<2:
    print('the input is error')
    exit(-1)

cmd_str = sys.argv[1]
print(cmd_str)



######################################################################################################################################################
######################################################################################################################################################
def GetTodayStockDataFromPolygon():
    start_date = DbUtil.GetUSAMaxTimeByCodeId()
    print('start_date:', start_date)
    diff_days = diffdays_between(start_date)
    print("diff_days:", diff_days)
    for num in range(0, diff_days):
        date_str = getn_date(num, "%Y-%m-%d")
        print(num, date_str)
        StockPolygon.get_entire_symbol(date_str)
        time.sleep(30)


def GetHistoryStockDataFromPolygon(end_date):
    start_date = DbUtil.GetUSAMinTimeByCodeId()
    print('start_date:', start_date)
    print('end_date:', end_date)
    start_diff_days = diffdays_between(start_date) + 1 
    end_diff_days = diffdays_between(end_date) + 1
    print("start_diff_days:", start_diff_days)
    print("end_diff_days:", end_diff_days)
    for num in range(start_diff_days, end_diff_days):
        date_str = getn_date(num, "%Y-%m-%d")
        print(num, date_str)
        StockPolygon.get_entire_symbol(date_str)
        time.sleep(15)

def GetStockFinancialFromPolygon():    
    # DbUtil.CreateFinancialsTable()
    choice_symbols = DbUtil.GetAllStockCodeIdFromStockTable()
    already_choice_symbols = DbUtil.GetStockFinancialCodeIdFromStockTable()
    choice_symbols = list(set(choice_symbols).difference(set(already_choice_symbols)))
    choice_symbols = list(set(choice_symbols).difference(set(UsaNoFinancialStock.no_financials)))
    no_financials_1 = []
    for symbol in choice_symbols:
        print(symbol)
        try:
            if not StockPolygon.get_stock_financials(symbol):
                no_financials_1.append(symbol)
            else:
                time.sleep(12)
        except:
            print(no_financials_1)
            time.sleep(12)

def GetHistoryCNStockDataFromBaoStock():
    # DbUtil.CreateCNKdataTable()
    CNBaoStock.cn_historystock_download_data("2019-09-02", "2021-09-02")


def GetCNStockPerformanceFromBaoStock():
    CNBaoStock.get_allstock_performance_express()
    # DbUtil.CreateCNPerformanceTable()

def GetTodayCNStockFromBaoStock():
    start_date = DbUtil.GetCNMaxTimeByCodeId()
    # print('start_date:', start_date)
    # start_date = GetAfterNDayBydate(start_date, 1)
    end_date = GetTomorrow()
    print('start_date:', start_date)
    print('end_date:', end_date)
    CNBaoStock.cn_historystock_download_data(start_date, end_date)


def GetCNStockIndustryFromBaoStock():
    # DbUtil.CreateCNStockIndustryTable()
    CNBaoStock.get_stock_industry_cnstock()
   

######################################################################################################################################################
######################################################################################################################################################

if __name__ == '__main__':    
    if 'stockdata_today' == cmd_str.strip():
        GetTodayStockDataFromPolygon()
    elif 'stockdata_history' == cmd_str.strip():
        if len(sys.argv)<3:
            print('the input is error')
            exit(-1)
        end_date = sys.argv[2]
        GetHistoryStockDataFromPolygon(end_date)
    elif 'stock_financial' == cmd_str.strip():
        GetStockFinancialFromPolygon()
    elif 'cn_stock' == cmd_str.strip():
        GetHistoryCNStockDataFromBaoStock()
    elif 'cn_performance' == cmd_str.strip():
        GetCNStockPerformanceFromBaoStock()
    elif 'cn_today' == cmd_str.strip():
        GetTodayCNStockFromBaoStock()
    elif 'cn_plat' == cmd_str.strip():
        GetCNStockIndustryFromBaoStock()
    else:
        print(cmd_str + ' is error')


