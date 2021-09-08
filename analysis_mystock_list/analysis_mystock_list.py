from futu import *
import pandas as pd
import matplotlib.pyplot as plt
import datetime

def HandleEachStockAndDrawFigure(code_pd, code):
    code_pd['buy_price'] = code_pd.apply(lambda x : x.dealt_avg_price if x.trd_side == 'BUY' else 0, axis =1)
    code_pd['sell_price'] = code_pd.apply(lambda x : x.dealt_avg_price if x.trd_side == 'SELL' else 0, axis =1)
    code_pd['total_buy_price']= code_pd.apply(lambda x : x.buy_price * x.qty, axis = 1)
    code_pd['total_sell_price']= code_pd.apply(lambda x : x.sell_price * x.qty, axis = 1)
    total_value = code_pd['total_sell_price'].sum() - code_pd['total_buy_price'].sum()
    code_pd= code_pd.drop(columns=['trd_side'])
    code_pd= code_pd.drop(columns=['dealt_avg_price'])
    code_pd= code_pd.drop(columns=['total_buy_price'])
    code_pd= code_pd.drop(columns=['total_sell_price'])
    code_pd.set_index(['qty'], inplace=True)
    code_pd_picture = code_pd.plot(kind='bar', title= code + '  profit:' + str(total_value), grid=True)
    code_pd_fig = code_pd_picture.get_figure()
    code_pd_fig.savefig('./figure/' + code + ".png")
    return total_value

def HandleTotalAndDrawFigure(code_pd, code):
    total_profit = code_pd['profit'].sum()
    code_pd.set_index(['code'], inplace=True)
    code_pd_picture = code_pd.plot(kind='bar', title= code + '  total profit:' + str(total_profit), grid=True)
    code_pd_fig = code_pd_picture.get_figure()
    code_pd_fig.savefig('./figure/' + code + ".png")

#############################################################################################################
json_mystock = pd.read_json('my_stock.json', encoding='utf-8', orient='records')
sort_mystock_pd = json_mystock.sort_values(by='create_time', ascending=True)
mystock_map = {}
mystock_codes = set(sort_mystock_pd['code'])

total_profit = pd.DataFrame(columns=('code', 'profit'))
for code in mystock_codes:
    code_pd = sort_mystock_pd[sort_mystock_pd['code'] == code]
    new_code_pd = code_pd.loc[:, ['qty', 'trd_side', 'dealt_avg_price']] 
    mystock_map[code] = new_code_pd 
    cur_profit = HandleEachStockAndDrawFigure(new_code_pd, code)
    total_profit = total_profit.append([{'code': code, 'profit': cur_profit}], ignore_index=True)

print(total_profit.sort_values(by='profit', ascending=True))
HandleTotalAndDrawFigure(total_profit, 'total_profit')
