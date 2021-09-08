import time, sys
import matplotlib.pyplot as plt
import numpy as np
from futu import *
from get_option import * 

if len(sys.argv) < 2:
    print("please input option code and price:")

option_code = sys.argv[1]
stock_price = float(sys.argv[2])

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
data_filter = OptionDataFilter()
data_filter.vol_min = 100
data_filter.vol_max = 10000
data = GetOptionChain(quote_ctx, option_code, '2021-04-01', '2021-04-30', OptionType.PUT, OptionCondType.ALL, data_filter)
option_code_list = data['code'].tolist()
option_price_list = data.loc[:, ['code', 'strike_price']]
sort_option_price_list = option_price_list.sort_values(by='code', ascending=True)

option_price_data = GetOptionOrStockPriceData(quote_ctx, option_code_list, [SubType.QUOTE], subscribe_push=False) 

option_price_data['need_rise_rate'] = option_price_data.apply(lambda x : x.last_price / stock_price * 100 , axis =1)
new_option_price_data = option_price_data.loc[:, ['code', 'last_price', 'need_rise_rate']]
sort_option_price_data = new_option_price_data.sort_values(by='code', ascending=True)
sort_option_price_data['strike_price'] = sort_option_price_list['strike_price']
sort_option_price_data = sort_option_price_data.sort_values(by='last_price', ascending=True)
sort_option_price_data['max_cost'] = sort_option_price_data.apply(lambda x : stock_price - x.strike_price + x.last_price if x.strike_price <= stock_price else x.last_price - (x.strike_price - stock_price), axis =1)
print(sort_option_price_data)

x = np.arange(0, 100, 0.01)
plt.figure()
for index, line in sort_option_price_data.iterrows():
    strike_price = float(line['strike_price'])
    last_price = float(line['last_price'])
    if strike_price <= stock_price:
        interval1_0 = [1.0 if (i <= strike_price) else 0 for i in x]
        interval1_2 = [0 if (i > strike_price) else 0 for i in x]
        y = interval1_0 + (x - stock_price) * interval1_2 - last_price
    else:
        interval2_0 = [1.0 if (i <= stock_price) else 0 for i in x]
        interval2_1 = [strike_price - stock_price if (i > stock_price and i <= strike_price) else 0 for i in x]
        interval2_2 = [1.0 if (i > strike_price) else 0.0 for i in x]
        y = (strike_price - x) * interval2_0 + interval2_1 + (x - stock_price) * interval2_2 - last_price
    plt.plot(x,y)
plt.savefig('./test2.jpg')  
quote_ctx.close()  # 关闭当条连接，FutuOpenD 会在1分钟后自动取消相应股票相应类型的订阅
