from futu import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import six, sys
sys.path.append('../')
from common.db_util import *
from common.stock_util import *


def render_mpl_table(data, col_width=3.0, row_height=0.625, font_size=14,
                     header_color='#40466e', row_colors=['#f1f1f2', 'w'], edge_color='w',
                     bbox=[0, 0, 1, 1], header_columns=0,
                     ax=None, **kwargs):
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')

    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)

    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in  six.iteritems(mpl_table._cells):
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
    return ax



def GetUserSecurityGroup(quote_ctx, group_type):
    ret, data = quote_ctx.get_user_security_group(group_type = UserSecurityGroupType.ALL)
    return data


def GetUserSecurity(quote_ctx, gruop_name):
    ret, data = quote_ctx.get_user_security(gruop_name)
    return data

def GetStockKline(quote_ctx, stock_list, kline_type, kline_num, autype = AuType.QFQ):
    klinetype_list = [kline_type for n in range(len(stock_list))]
    kline_map = {}
    ret_sub, err_message = quote_ctx.subscribe(stock_list, klinetype_list, subscribe_push=False)
    if ret_sub == RET_OK:  # 订阅成功
        for stockitem in stock_list:
            ret, data = quote_ctx.get_cur_kline(stockitem, kline_num, kline_type, autype)
            if ret == RET_OK:
                kline_map[stockitem] = data
            else:
                print('error:', data)
                continue
    else:
        print('subscription failed', err_message)
    return kline_map


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

#根据收盘价计算涨跌幅列表
def CalcStockCloseChangeRatio(stock_data_pd):
    return stock_data.close.pct_change()

#根据成交量计算涨跌幅列表
def CalcStockVolumeChangeRatio(stock_data_pd):
    return stock_data.volume.pct_change()
    
def RiseWithVolume(stock_data_pd, durations):
    close_ration_list = CalcStockCloseChangeRatio(stock_data_pd)
    volume_ration_list = CalcStockVolumeChangeRatio(stock_data_pd)
    cur_durations = 0
    for i in range(len(close_ration_list)):
        if close_ration_list[i] and volume_ration_list[i]:
            if close_ration_list[i] > 0 and volume_ration_list[i] > 0:
                cur_durations += 1
                if(cur_durations >= durations):
                    print(stock_data_pd.iloc[i])
                    cur_durations = 0



#def GetGoldenCross


if __name__ == '__main__':
    # quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    # my_stock_list = GetUserSecurity(quote_ctx, '港股')['code'].to_list()
    # db_conn = ConnectStockDataDb()
    # all_stock_kline_data = GetStockHistoryKline(quote_ctx, my_stock_list, SubType.K_DAY, '2020-01-01', '2020-03-31')
    # for stock_name, stock_data in all_stock_kline_data.items():
    #     stock_list = stock_data.values.tolist()
    #     for stock_line in stock_list:
    #         stock_line.insert(1, SubType.K_DAY)
    #     InsertDataListToKdataTable(db_conn, stock_list)
    
    # db_conn.close()
        #print(stock_data)
    # all_stock_datadf = pd.DataFrame(all_stock_result, columns = ['stock_name', 'cur_stock_close_price', 'max_stock_close_price', 'cur_fall_rate', 'min_stock_close_price', 'cur_rise_rate'])
    # all_stock_datadf.to_csv('my_stock_data.csv')


    #quote_ctx.close()
    db_conn = ConnectStockDataDb()
    stock_data = GetStockDataOrderTimeByCode(db_conn, 'HK.800000')
    print(stock_data)

    db_conn.close()

