from futu import *
import pandas as pd
import sys, datetime
from dateutil.relativedelta import relativedelta

if len(sys.argv) < 2:
    print('input error')
    exit(0)
cmd = sys.argv[1]
if cmd == '--h':
    print('please input argv:')
    print('python get_mystock.py stockstat pwd_unlock:  show my stock postion')
    print('python get_mystock.py order pwd_unlock SH.510050  3 : show my stock history order')
    print('python get_mystock.py allorder pwd_unlock')
    print('python get_mystock.py deal pwd_unlock SH.510050')
    exit(0)

pwd_unlock = sys.argv[2] 


now_today = datetime.date.today()
def before_month(detal_month):
    return datetime.date.today() - relativedelta(months=detal_month)

def get_my_stock_position(quote_ctx):
    result, data = quote_ctx.position_list_query()
    return data

def get_stock_order(quote_ctx, stock_code, detal_month):
    end = str(before_month(detal_month))
    print(end)
    ret, data, page_req_key = quote_ctx.request_history_kline(stock_code, str(start), end,max_count=100)
    return data

def get_history_deal(quote_ctx, stock_code):
    result, data = quote_ctx.history_deal_list_query(stock_code)
    return data



if __name__ == '__main__':
    quote_ctx = OpenUSTradeContext(host='127.0.0.1', port=11111)
    quote_ctx.unlock_trade(pwd_unlock)
    if cmd == 'stockstat':
        data = get_my_stock_position(quote_ctx)
        print(data)
    elif cmd == 'order':
        stock_code = sys.argv[3]
        before_mon = sys.argv[4]
        data = get_stock_order(quote_ctx, stock_code, before_mon)
        print(data)
    elif cmd == 'allorder':
        result, data = quote_ctx.history_order_list_query(status_filter_list=['FILLED_ALL', 'FILLED_PART']);
        file_fd = open('my_stock.json', 'w')
        file_fd.write(str(data.to_json(orient='records')))
    elif cmd == 'deal':
        stock_code = sys.argv[3]
        data = get_history_deal(quote_ctx, stock_code)
        print(data)
    quote_ctx.close()

