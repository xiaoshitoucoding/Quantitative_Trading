from futu import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import six, sys
sys.path.append('../')
from common.db_util import *
from common.stock_util import *

def GetUserSecurityGroup(quote_ctx, group_type):
    ret, data = quote_ctx.get_user_security_group(group_type = UserSecurityGroupType.ALL)
    return data


def GetUserSecurity(quote_ctx, gruop_name):
    ret, data = quote_ctx.get_user_security(gruop_name)
    return data

def GetStockHistoryKline(quote_ctx, stock_list, kline_type, start_time, end_time, autype = AuType.QFQ):
    klinetype_list = [kline_type for n in range(len(stock_list))]
    kline_map = {}
   
    for stockitem in stock_list:
        cur_stockdata = []
        ret, data, page_req_key = quote_ctx.request_history_kline(stockitem, start=start_time, end=end_time, ktype = kline_type, autype=autype, max_count=20)  # 每页5个，请求第一页
        if ret == RET_OK:
            cur_stockdata.append(data)
        else:
            print('error:', data)
            continue
        while page_req_key != None:  # 请求后面的所有结果
            ret, data, page_req_key = quote_ctx.request_history_kline(stockitem, start=start_time, end=end_time, ktype = kline_type, autype=autype, max_count=20, page_req_key=page_req_key) # 请求翻页后的数据
            if ret == RET_OK:
                cur_stockdata.append(data)
            else:
                print('error:', data)
                continue
        all_stockdata = pd.concat(cur_stockdata)
        kline_map[stockitem] = all_stockdata

    return kline_map


if __name__ == '__main__':
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    my_stock_list = GetUserSecurity(quote_ctx, '港股')['code'].to_list()
    db_conn = ConnectStockDataDb()
    all_stock_kline_data = GetStockHistoryKline(quote_ctx, my_stock_list, SubType.K_DAY, '2019-01-01', '2020-12-31')
    for stock_name, stock_data in all_stock_kline_data.items():
        stock_list = stock_data.values.tolist()
        for stock_line in stock_list:
            stock_line.insert(1, SubType.K_DAY)
        InsertDataListToKdataTable(db_conn, stock_list)
    
    db_conn.close()
    quote_ctx.close()


