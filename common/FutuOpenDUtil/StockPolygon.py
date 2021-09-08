from futu import *

import time
from Trade.KLManager import split_k_market
from Util.DateUtil import current_str_date
from Util import DateUtil
from Util import DbUtil

key="SjQ6xUW0XAivyp3VuRZ8Ld_WWjDhScfv"

from datetime import datetime,timedelta
from polygon import RESTClient
# from lib import mysql
import json





def get_entire_symbol(date):
    results=[]
    with RESTClient(key) as client:
        resp=client.stocks_equities_grouped_daily(locale="us",market="stocks",date=date)
        if resp.resultsCount!=0:
            stock_data_lists = []
            for result in resp.results:
                stock_data = [result['T'], SubType.K_DAY, date, result['o'], result['c'], result['h'], result['l'], result['v']]
                stock_data_lists.append(stock_data)
            print(len(stock_data_lists))
            DbUtil.InsertUSACurDataListToKdataTable(stock_data_lists)
        else:
            print("No Trade")





def get_stock_financials(symbol):
    with RESTClient(key) as client:
        resp=client.reference_stock_financials(symbol=symbol, limit=1, type='T')
        if 'OK' == resp.status:
            if 0 == len(resp.results):
                print('the ' + symbol + ' have no financials')
                return False
            for stockfinan_map in resp.results:
                DbUtil.InsertStockFinancialToTable(stockfinan_map)
                return True
        else:
            print('the ' + symbol + ' have no financials')
            return False
    return False




# if __name__ == '__main__':
#     results = get_stock_financials('AAPL')
#     content_line = []
#     for item_map in results:
#         for key in item_map:
#             print(key + '    CHAR ,')





