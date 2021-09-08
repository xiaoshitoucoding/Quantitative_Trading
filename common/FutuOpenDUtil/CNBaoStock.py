from futu import *

import time
from Util.DateUtil import current_str_date
from Util import DateUtil
from Util import DbUtil





import baostock as bs
import pandas as pd


def cn_historystock_download_data(start_date, end_date):
    bs.login()

    # 获取指定日期的指数、股票数据
    stock_rs = bs.query_all_stock(end_date)
    stock_df = stock_rs.get_data()
    if len(stock_df) == 0:
        stock_rs = bs.query_all_stock(start_date)
    stock_df = stock_rs.get_data()
    if len(stock_df) == 0:
        print('have no date')
        bs.logout()
        return
    for code in stock_df["code"]:
        print("Downloading :" + code)
        cn_historystock_bycode(code, start_date, end_date)
    bs.logout()



def cn_historystock_bycode(code, start_date, end_date):
    data_df = pd.DataFrame()
    k_rs = bs.query_history_k_data_plus(code,\
            "code,date,open,high,low,close,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST", start_date, end_date)
    data_df = data_df.append(k_rs.get_data())
    DbUtil.InsertCNCurDataListToKdataTable(data_df.values.tolist())


def get_allstock_performance_express():
    start_date = "2020-01-01"
    more_start_date = "2010-01-01"
    end_date = "2021-09-02"
    #### 登陆系统 ####
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:'+lg.error_code)
    print('login respond  error_msg:'+lg.error_msg)
    # 获取指定日期的指数、股票数据
    stock_rs = bs.query_all_stock(end_date)
    stock_df = stock_rs.get_data()
    for code in stock_df["code"]:
        print("Downloading :" + code)
        result_list = get_performance_express_cnstock(code=code, start_date=start_date, end_date=end_date)
        if len(result_list) == 0:
            result_list = get_performance_express_cnstock(code=code, start_date=more_start_date, end_date=end_date)
            if len(result_list) == 0:
                print('the ' + code + "have no performane")
        DbUtil.InsertCNStockPerformanceTable(result_list)
    #### 登出系统 ####
    bs.logout()



def get_performance_express_cnstock(code, start_date, end_date):
    #### 获取公司业绩快报 ####
    rs = bs.query_performance_express_report(code, start_date=start_date, end_date=end_date)
    result_list = []
    while (rs.error_code == '0') & rs.next():
        result_list.append(rs.get_row_data())
        # 获取一条记录，将记录合并在一起
    result = pd.DataFrame(result_list, columns=rs.fields)
    return result.values.tolist()


def get_stock_industry_cnstock():
    # 登陆系统
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:'+lg.error_code)
    print('login respond  error_msg:'+lg.error_msg)

    # 获取行业分类数据
    rs = bs.query_stock_industry()
    print('query_stock_industry error_code:'+rs.error_code)
    print('query_stock_industry respond  error_msg:'+rs.error_msg)

    # 打印结果集
    industry_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        industry_list.append(rs.get_row_data())
    result = pd.DataFrame(industry_list, columns=rs.fields)
    result_list = result.values.tolist()
    DbUtil.InsertCNStockIndustryTable(result_list)
    # 登出系统
    bs.logout()


    








