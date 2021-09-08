import time, sys
import matplotlib.pyplot as plt
import numpy as np
from futu import *
from get_option import * 
sys.path.append('../')
from common.cs_time_util import *
import pandas as pd

if len(sys.argv) < 3:
    print("please input option code , price and month:")

option_code = sys.argv[1]
stock_price = float(sys.argv[2])
month = int(sys.argv[3])

today = datetime.date.today()
def handle_spread_arbitrage_data(option_price_data, stock_price):
    result_data = []
    result_coulmns = ['max_cost', 'max_fit', 'start_fit_rate', 'A_code', 'A_strike_price', 'A_fall_rate', 'A_last_price', 'B_code', 'B_strike_price', 'B_rise_rate', 'B_last_price']
    option_price_data = option_price_data.sort_values(by='strike_price', ascending=True)
    for A_index, A_row in option_price_data.iterrows():
        if float(A_row['strike_price']) > stock_price:
            continue
        for B_index, B_row in option_price_data.iterrows():
            if A_index == B_index or float(B_row['strike_price']) <= stock_price or A_row['strike_time'] != B_row['strike_time']:
                continue
            result_line = []
            result_line.append(float(A_row['last_price']) - float(B_row['last_price']))
            result_line.append(float(B_row['strike_price']) - float(A_row['strike_price']) + float(B_row['last_price'])) 
            result_line.append((float(A_row['strike_price']) + float(A_row['last_price']) - stock_price)/ stock_price * 100) 
            result_line.append(A_row['code'])
            result_line.append(A_row['strike_price'])
            result_line.append((stock_price - float(A_row['strike_price']))/ stock_price * 100)
            result_line.append(A_row['last_price'])
            result_line.append(B_row['code'])
            result_line.append(B_row['strike_price'])
            result_line.append((float(B_row['strike_price']) - stock_price)/ stock_price * 100)
            result_line.append(B_row['last_price'])
            result_data.append(result_line)
    result_df = pd.DataFrame(result_data, columns=result_coulmns)
    return result_df

def get_spread_arbitrage(quote_ctx, option_code, month, option_type, option_condtype, data_filter):
    month_first, month_last = GetFirstAndLastDay(today.year, month) 
    call_data = GetOptionChain(quote_ctx, option_code, str(month_first), str(month_last), option_type, OptionCondType.ALL, data_filter)
    call_option_price_list = call_data.loc[:, ['code', 'strike_price', 'strike_time']].sort_values(by='code', ascending=True)
    call_option_price_data = GetOptionOrStockPriceData(quote_ctx, call_data['code'].tolist(), [SubType.QUOTE], subscribe_push=False).sort_values(by='code', ascending=True)
    call_option_price_data = call_option_price_data.loc[:, ['code', 'last_price']]
    call_option_price_data['strike_price'] = call_option_price_list['strike_price']
    call_option_price_data['strike_time'] = call_option_price_list['strike_time']
    return call_option_price_data


if __name__ == '__main__':
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111) 
    data_filter = OptionDataFilter()
    data_filter.vol_min = 50
    data_filter.vol_max = 10000
    call_option_data = get_spread_arbitrage(quote_ctx, option_code, month, OptionType.CALL, OptionCondType.ALL, data_filter)
    call_spread_arbitrage_data = handle_spread_arbitrage_data(call_option_data, stock_price)
    call_spread_arbitrage_data = call_spread_arbitrage_data[call_spread_arbitrage_data['A_fall_rate'] > 2.0]
    print(call_spread_arbitrage_data.sort_values(by='max_cost', ascending=True))
    quote_ctx.close()  # 关闭当条连接，FutuOpenD 会在1分钟后自动取消相应股票相应类型的订阅
