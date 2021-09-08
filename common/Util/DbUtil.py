#coding=utf-8
import sqlite3
import os.path
import pandas as pd
from Util import DateUtil
from Util.DateUtil import str_to_datetime,date_str_to_int
from itertools import chain
from  Util import DbTable
import datetime
from futu import *
from CoreBase import Env





def ConnectStockDataDb():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, DbTable.stock_data_db)
    conn = sqlite3.connect(db_path)
    return conn

def GetStockDataByCode(conn, code):
    select_cmd = "SELECT * from  " + DbTable.select_table_name + " where CODEID == '" + code +"'"
    cur_sor = conn.cursor()
    select_cursor = cur_sor.execute(select_cmd)
    stock_data_pd = pd.DataFrame(select_cursor.fetchall(), columns=DbTable.select_stock_data_columns)
    return stock_data_pd


def GetStockDataOrderTimeByCode(conn, code):
    select_cmd = "SELECT * from  " + DbTable.select_table_name + " where CODEID == '" + code +"'  order by datetime(TIME) asc"
    cur_sor = conn.cursor()
    select_cursor = cur_sor.execute(select_cmd)
    stock_data_pd = pd.DataFrame(select_cursor.fetchall(), columns=DbTable.select_stock_data_columns)
    if stock_data_pd is not None:
        # 规避重复交易日数据风险，subset只设置date做为滤除重复
        stock_data_pd.drop_duplicates(subset=['time_key'], inplace=True)
    stock_data_pd['time_key'] = pd.to_datetime(stock_data_pd['time_key'])
    stock_data_pd.set_index('time_key', inplace=True)
    stock_data_pd['date'] = [int(ts.date().strftime("%Y%m%d")) for ts in stock_data_pd.index]
    stock_data_pd['date_week'] = stock_data_pd['date'].apply(lambda x: DateUtil.week_of_date(str(x), '%Y%m%d'))
    stock_data_pd['pre_close'] = stock_data_pd.close.shift(1)
    return stock_data_pd



def GetAllStockCodeIdFromStockTable(date_str = ''):
    db_conn = ConnectStockDataDb()
    select_cmd = ''
    if '' == date_str:
        select_cmd = "select distinct CODEID from " + DbTable.select_table_name + ";"
    else:
        select_cmd = "select distinct CODEID from " + DbTable.select_table_name + " where TIME = '" + date_str + "';"
    cur_sor = db_conn.cursor()
    select_cursor = cur_sor.execute(select_cmd)
    result_list = list(chain.from_iterable(select_cursor.fetchall()))
    db_conn.close()
    return result_list


def GetStockByFinancialStockAsset(stock_list, total_asset):
    if Env.g_market_target == Env.EMarketTargetType.E_MARKET_TARGET_US:
        return GetUSAStockByFinancialStockAsset(stock_list, total_asset)
    elif Env.g_market_target == Env.EMarketTargetType.E_MARKET_TARGET_CN:
       return GetCNStockByFinancialStockAsset(stock_list, total_asset)
    else:
        return None
   

####################################################################################################################################################
####################################################STOCK_KDATA 股票日K线数据的db操作函数 START######################################################
def CreateKdataTable(conn):
    conn = ConnectStockDataDb()
    cur_sor = conn.cursor()
    cur_sor.execute(DbTable.stock_kdata_table)
    print("stock kdata Table created successfully")
    conn.commit()
    create_index_cmd = "CREATE INDEX '" + DbTable.stock_index + "' on " + DbTable.stock_table_name + "(" + DbTable.stock_index + ")"
    cur_sor.execute(create_index_cmd)
    conn.commit()

def InsertDataToKdataTable(conn, code, k_type, time_key, open, close, high, low, pe_ratio, turnover_rate, volume,  turnover, change_rate, last_code):
    values_str = "VALUES ('" + code + "', '" + k_type + "' , '" + time_key + "', " + str(open) + ", " + str(close) + ", " + str(high) + ", " + str(low) + ", " + str(pe_ratio) + ", " + str(turnover_rate) + ", " + str(volume) + ", " + str(turnover) + ", " + str(change_rate) + ", " + str(last_code) + ")"
    insert_cmd_str = "INSERT INTO STOCK_KDATA(CODEID, K_TYPE, TIME, OPEN, CLOSE, HIGH, LOW, PERATIO, TURNOVERRATE, VOLUME, TURNOVER, CHANGERATE, LASTCLOSE) " + values_str
    cur_sor = conn.cursor()
    cur_sor.execute(insert_cmd_str)
    conn.commit()


def InsertDataListToKdataTable(data_list):
    conn = ConnectStockDataDb()
    cur_sor = conn.cursor()
    for code, k_type, time_key, open, close, high, low, pe_ratio, turnover_rate, volume,  turnover, change_rate, last_code in data_list:
        values_str = "VALUES ('" + code + "', '" + k_type + "' , '" + time_key + "', " + str(open) + ", " + str(close) + ", " + str(high) + ", " + str(low) + ", " + str(pe_ratio) + ", " + str(turnover_rate) + ", " + str(volume) + ", " + str(turnover) + ", " + str(change_rate) + ", " + str(last_code) + ")"
        insert_cmd_str = "INSERT INTO STOCK_KDATA(CODEID, K_TYPE, TIME, OPEN, CLOSE, HIGH, LOW, PERATIO, TURNOVERRATE, VOLUME, TURNOVER, CHANGERATE, LASTCLOSE) " + values_str
        try:
            cur_sor.execute(insert_cmd_str)
        except:
            print(insert_cmd_str + '  error!!!!')
    conn.commit()
    conn.close()


def InsertCurDataListToKdataTable(data_list):
    db_conn = ConnectStockDataDb()
    cur_sor = db_conn.cursor()
    for code, k_type, time_key, open, close, high, low, volume,  turnover, pe_ratio, turnover_rate, last_code in data_list:
        values_str = "VALUES ('" + code + "', '" + k_type + "' , '" + time_key + "', " + str(open) + ", " + str(close) + ", " + str(high) + ", " + str(low) + ", " + str(pe_ratio) + ", " + str(turnover_rate) + ", " + str(volume) + ", " + str(turnover) + ", 0, " + str(last_code) + ")"
        insert_cmd_str = "INSERT INTO STOCK_KDATA(CODEID, K_TYPE, TIME, OPEN, CLOSE, HIGH, LOW, PERATIO, TURNOVERRATE, VOLUME, TURNOVER, CHANGERATE, LASTCLOSE) " + values_str
        try:
            cur_sor.execute(insert_cmd_str)
        except:
            print(insert_cmd_str + '  error!!!!')
    db_conn.commit()
    db_conn.close()

####################################################################################################################################################
####################################################STOCK_KDATA 股票日K线数据的db操作函数 END########################################################





####################################################################################################################################################
####################################################USA_STOCK_KDATA 美股股票日K线数据的db操作函数 START##############################################
def CreateUSAKdataTable():
    conn = ConnectStockDataDb()
    cur_sor = conn.cursor()
    try:
        cur_sor.execute(DbTable.usa_stock_kdata_table)
        conn.commit()
        create_index_cmd = "CREATE INDEX '" + DbTable.usa_stock_index + "' on " + DbTable.usa_stock_table_name + "(" + DbTable.usa_stock_index + ")"
        cur_sor.execute(create_index_cmd)
        conn.commit()
        print("stock kdata Table created successfully")
    except:
        print('the USA_STOCK_KDATA has created')


def InsertUSACurDataListToKdataTable(data_list):
    db_conn = ConnectStockDataDb()
    cur_sor = db_conn.cursor()
    for code, k_type, time_key, open, close, high, low, volume in data_list:
        values_str = "VALUES ('" + code + "', '" + k_type + "' , '" + time_key + "', " + str(open) + ", " + str(close) + ", " + str(high) + ", " + str(low) + ", " + str(volume) +")"
        insert_cmd_str = "INSERT INTO USA_STOCK_KDATA(CODEID, K_TYPE, TIME, OPEN, CLOSE, HIGH, LOW, VOLUME) " + values_str
        try:
            cur_sor.execute(insert_cmd_str)
        except:
            print(insert_cmd_str + '  error!!!!')
    db_conn.commit()
    db_conn.close()

def GetUSAMaxTimeByCodeId(stock_id = ''):
    db_conn = ConnectStockDataDb()
    cur_sor = db_conn.cursor()
    select_cmd = ''
    if '' == stock_id:
        select_cmd = "SELECT MAX(TIME)  from   " + DbTable.usa_stock_table_name + ";"
    else:
        select_cmd = "SELECT MAX(TIME)  from   " + DbTable.usa_stock_table_name + "  where CODEID='" + stock_id +"';"
    select_cursor = cur_sor.execute(select_cmd)
    result_str = ''
    for row in select_cursor:
        if(len(row) > 0):
            result_str = row[0].split()[0]
    db_conn.close()
    return result_str


def GetUSAMinTimeByCodeId(stock_id = ''):
    db_conn = ConnectStockDataDb()
    cur_sor = db_conn.cursor()
    select_cmd = ''
    if '' == stock_id:
        select_cmd = "SELECT MIN(TIME)  from   " + DbTable.usa_stock_table_name + ";"
    else:
        select_cmd = "SELECT MIN(TIME)  from   " + DbTable.usa_stock_table_name + "  where CODEID='" + stock_id +"';"
    select_cursor = cur_sor.execute(select_cmd)
    result_str = ''
    for row in select_cursor:
        if(len(row) > 0):
            result_str = row[0].split()[0]
    db_conn.close()
    return result_str
####################################################################################################################################################
####################################################USA_STOCK_KDATA 美股股票日K线数据的db操作函数 END################################################




####################################################################################################################################################
####################################################PLATE_STOCKNAME 股票板块数据的db操作函数 START###################################################

def CreatePlateStocknameTable(conn):
    try:
        cur_sor = conn.cursor()
        cur_sor.execute(DbTable.plate_stockname_table)
        conn.commit()
        print("stock PlateStockname Table created successfully")
    except:
        print("stock PlateStockname Table created failed")
    try:
        create_index_cmd = "CREATE INDEX '" + DbTable.plate_stockname_index + "' on " + DbTable.plate_stockname_table_name + "(" + DbTable.plate_stockname_index + ")"
        cur_sor.execute(create_index_cmd)
        conn.commit()
        print("stock PlateStockname Table idex successfully")
    except:
        print("stock PlateStockname Table idex failed")



def InsertStockNameTodataTable(conn, data_list):
    cur_sor = conn.cursor()
    for code, lot_size, stock_name, stock_type, list_time, stock_id, main_contract, last_trade_time, plate_name, plate_id, market_type in data_list:
        values_str = "VALUES ('" + code + "', " + str(lot_size) + " , '" + stock_name + "', '" + str(stock_type) + "', '" + list_time + "', '" + str(stock_id) + "', " + str(main_contract) + ", '" + str(last_trade_time) + "', '" + plate_name + "', '" + plate_id + "', '" + market_type +"')"
        insert_cmd_str = "INSERT INTO PLATE_STOCKNAME(" + DbTable.plate_stockname_table_columns + ") " + values_str
        try:
            cur_sor.execute(insert_cmd_str)
        except:
            print(insert_cmd_str + '  error!!!!')
    conn.commit()

def GetAllStockNameFromTable():
    db_conn = ConnectStockDataDb()
    select_cmd = "SELECT * from  " + DbTable.plate_stockname_table_name
    cur_sor = db_conn.cursor()
    select_cursor = cur_sor.execute(select_cmd)
    stockname_data_pd = pd.DataFrame(select_cursor.fetchall(), columns=DbTable.plate_stockname_columns)
    db_conn.close()
    return stockname_data_pd

####################################################################################################################################################
####################################################PLATE_STOCKNAME 股票板块数据的db操作函数 END#####################################################




####################################################################################################################################################
####################################################USA_STOCK_FINANCIALS 股票基本面数据的db操作函数 START############################################

def CreateFinancialsTable():
    conn = ConnectStockDataDb()
    cur_sor = conn.cursor()
    cur_sor.execute(DbTable.usa_stock_financials_table)
    print("USA_STOCK_FINANCIALS created successfully")
    conn.commit()
    create_index_cmd = "CREATE INDEX '" + DbTable.usa_stock_financials_index + "' on " + DbTable.usa_stock_financials_table_name + "(" + DbTable.usa_stock_financials_index + ")"
    cur_sor.execute(create_index_cmd)
    conn.commit()


def InsertStockFinancialToTable(data_map):
    db_conn = ConnectStockDataDb()
    cur_sor = db_conn.cursor()
    keys = ', '.join(data_map.keys())
    values = ', '.join("'%s'"%data_map[i] for i in data_map.keys())
    insert_cmd_str = 'INSERT INTO {table} ({keys}) VALUES ({values})'.format(table=DbTable.usa_stock_financials_table_name, keys=keys, values=values)
    try:
        cur_sor.execute(insert_cmd_str)
    except:
        print(insert_cmd_str + '  error!!!!')
    db_conn.commit()
    db_conn.close()


def GetStockFinancialCodeIdFromStockTable(date_str = ''):
    db_conn = ConnectStockDataDb()
    select_cmd = ''
    if '' == date_str:
        select_cmd = "select distinct ticker from " + DbTable.usa_stock_financials_table_name + ";"
    else:
        select_cmd = "select distinct ticker from " + DbTable.usa_stock_financials_table_name + " where updated = '" + date_str + "';"
    cur_sor = db_conn.cursor()
    select_cursor = cur_sor.execute(select_cmd)
    result_list = list(chain.from_iterable(select_cursor.fetchall()))
    db_conn.close()
    return result_list


def GetAllStockFinancialMap():
    db_conn = ConnectStockDataDb()
    cur_sor = db_conn.cursor()
    select_cmd = "SELECT ticker, marketCapitalization, MAX(updated) from   " + DbTable.usa_stock_financials_table_name + "   GROUP BY ticker;"
    select_cursor = cur_sor.execute(select_cmd)
    stockfinancial_map = {}
    for row in select_cursor:
        if len(row) >= 3:
            stockfinancial_map[row[0]] = row[1]
    db_conn.close()
    return stockfinancial_map

def GetAllSortedStockByFinancial():
    db_conn = ConnectStockDataDb()
    cur_sor = db_conn.cursor()
    select_cmd = "SELECT ticker, marketCapitalization, MAX(updated) from   " + DbTable.usa_stock_financials_table_name + "   GROUP BY ticker;"
    select_cursor = cur_sor.execute(select_cmd)
    stockfinancial_map = {}
    for row in select_cursor:
        if len(row) >= 3 and None != row[1]:
            print(row[1])
            stockfinancial_map[row[0]] = int(row[1])
    db_conn.close()
    sorted_tuple = sorted(stockfinancial_map.items(), key = lambda kv : kv[1], reverse=True)
    sorted_stockid = [item[0] for item in sorted_tuple]
    return sorted_stockid


def GetSortedStockByFinancialStock(stock_list):
    db_conn = ConnectStockDataDb()
    cur_sor = db_conn.cursor()
    stock_str = '(' + ', '.join("'%s'"%item for item in stock_list) + ')'
    select_cmd = "SELECT ticker, marketCapitalization, MAX(updated) from   " + DbTable.usa_stock_financials_table_name + "  WHERE ticker in  " + stock_str + '   GROUP BY ticker;'
    select_cursor = cur_sor.execute(select_cmd) 
    stockfinancial_map = {}
    for row in select_cursor:
        if len(row) >= 3 and None != row[1]:
            stockfinancial_map[row[0]] = int(row[1])
    db_conn.close()
    sorted_tuple = sorted(stockfinancial_map.items(), key = lambda kv : kv[1], reverse=True)
    sorted_stockid = [item[0] for item in sorted_tuple]
    return sorted_stockid



def GetUSAStockByFinancialStockAsset(stock_list, total_asset):
    db_conn = ConnectStockDataDb()
    cur_sor = db_conn.cursor()
    stock_str = '(' + ', '.join("'%s'"%item for item in stock_list) + ')'
    select_cmd = "SELECT ticker, marketCapitalization, MAX(updated) from   " + DbTable.usa_stock_financials_table_name + "  WHERE ticker in  " + stock_str + '   GROUP BY ticker;'
    select_cursor = cur_sor.execute(select_cmd) 
    stockfinancial_map = {}
    for row in select_cursor:
        if len(row) >= 3 and None != row[1]:
            if float(row[1]) < total_asset:
                continue
            stockfinancial_map[row[0]] = float(row[1])
    db_conn.close()
    sorted_tuple = sorted(stockfinancial_map.items(), key = lambda kv : kv[1], reverse=True)
    sorted_stockid = [item[0] for item in sorted_tuple]
    return sorted_stockid

####################################################################################################################################################
####################################################USA_STOCK_FINANCIALS 股票基本面数据的db操作函数 END##############################################


####################################################################################################################################################
####################################################CN_STOCK_KDATA 美股股票日K线数据的db操作函数 START##############################################
def CreateCNKdataTable():
    conn = ConnectStockDataDb()
    cur_sor = conn.cursor()
    try:
        cur_sor.execute(DbTable.cn_stock_kdata_table)
        conn.commit()
        create_index_cmd = "CREATE INDEX '" + DbTable.cn_stock_index + "' on " + DbTable.cn_stock_table_name + "(" + DbTable.cn_stock_index + ")"
        cur_sor.execute(create_index_cmd)
        conn.commit()
        print("stock kdata Table created successfully")
    except:
        print('the CN_STOCK_KDATA has created')


def InsertCNCurDataListToKdataTable(data_list):
    db_conn = ConnectStockDataDb()
    cur_sor = db_conn.cursor()
    for code, time_key, open, high, low, close, volume, amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST in data_list:
        values_str = "VALUES ('" + code + "', '" + SubType.K_DAY + "' , '" + time_key + "', " + str(open) + ", " + str(close) + ", " + str(high) + ", " + str(low) + ", " + str(volume) \
            + ", " + str(amount) + ", " + str(adjustflag) + ", " + str(turn) + ", " + str(tradestatus) + ", " + str(pctChg) + ", " + str(peTTM) + ", " + str(pbMRQ) + ", " + str(psTTM)\
                + ", " + str(pcfNcfTTM) + ", " + str(isST)+")"
        insert_cmd_str = "INSERT INTO CN_STOCK_KDATA(CODEID, K_TYPE, TIME, OPEN, CLOSE, HIGH, LOW, VOLUME, AMOUNT, ADJUSTFLAG, TURN, TRADESTATUS,PCTCHG, PETTM, PBMRQ, PSTTM, PCFNCFTTM, ISST) " + values_str
        try:
            cur_sor.execute(insert_cmd_str)
        except:
            print(insert_cmd_str + '  error!!!!')
    db_conn.commit()
    db_conn.close()


def GetCNMaxTimeByCodeId(stock_id = ''):
    db_conn = ConnectStockDataDb()
    cur_sor = db_conn.cursor()
    select_cmd = ''
    if '' == stock_id:
        select_cmd = "SELECT MAX(TIME)  from   " + DbTable.cn_stock_table_name + ";"
    else:
        select_cmd = "SELECT MAX(TIME)  from   " + DbTable.cn_stock_table_name + "  where CODEID='" + stock_id +"';"
    select_cursor = cur_sor.execute(select_cmd)
    result_str = ''
    for row in select_cursor:
        if(len(row) > 0):
            result_str = row[0].split()[0]
    db_conn.close()
    return result_str


def GetCNMinTimeByCodeId(stock_id = ''):
    db_conn = ConnectStockDataDb()
    cur_sor = db_conn.cursor()
    select_cmd = ''
    if '' == stock_id:
        select_cmd = "SELECT MIN(TIME)  from   " + DbTable.cn_stock_table_name + ";"
    else:
        select_cmd = "SELECT MIN(TIME)  from   " + DbTable.cn_stock_table_name + "  where CODEID='" + stock_id +"';"
    select_cursor = cur_sor.execute(select_cmd)
    result_str = ''
    for row in select_cursor:
        if(len(row) > 0):
            result_str = row[0].split()[0]
    db_conn.close()
    return result_str


####################################################################################################################################################
####################################################CN_STOCK_KDATA A股股票日K线数据的db操作函数 END################################################


####################################################################################################################################################
####################################################CN_STOCK_FINANCIALS A股股票金融的db操作函数 START##############################################
def CreateCNPerformanceTable():
    conn = ConnectStockDataDb()
    cur_sor = conn.cursor()
    try:
        cur_sor.execute(DbTable.cn_stock_financials_table)
        conn.commit()
        create_index_cmd = "CREATE INDEX '" + DbTable.cn_stock_financials_index + "' on " + DbTable.cn_stock_financials_table_name + "(" + DbTable.cn_stock_financials_index + ")"
        cur_sor.execute(create_index_cmd)
        conn.commit()
        print("stock kdata Table created successfully")
    except:
        print('the CN_STOCK_FINANCIALS has created')


def InsertCNStockPerformanceTable(data_list):
    db_conn = ConnectStockDataDb()
    cur_sor = db_conn.cursor()
    for code, performanceExpPubDate, performanceExpStatDate, performanceExpUpdateDate, performanceExpressTotalAsset, performanceExpressNetAsset, performanceExpressEPSChgPct, performanceExpressROEWa,performanceExpressEPSDiluted,performanceExpressGRYOY,performanceExpressOPYOY in data_list:
        values_str = "VALUES ('" + code +  "' , '" + performanceExpPubDate + "', " + str(performanceExpStatDate) + ", " + str(performanceExpUpdateDate) + ", " + str(performanceExpressTotalAsset) + ", " + str(performanceExpressNetAsset) + ", " + str(performanceExpressEPSChgPct) \
            + ", " + str(performanceExpressROEWa) + ", " + str(performanceExpressEPSDiluted) + ", " + str(performanceExpressGRYOY) + ", " + str(performanceExpressOPYOY) + ")"
        insert_cmd_str = "INSERT INTO CN_STOCK_FINANCIALS(CODEID, performanceExpPubDate, performanceExpStatDate, performanceExpUpdateDate, performanceExpressTotalAsset, performanceExpressNetAsset, performanceExpressEPSChgPct, performanceExpressROEWa, performanceExpressEPSDiluted, performanceExpressGRYOY, performanceExpressOPYOY) " + values_str
        try:
            cur_sor.execute(insert_cmd_str)
        except:
            print(insert_cmd_str + '  error!!!!')
    db_conn.commit()
    db_conn.close()


    




def GetCNAllSortedStockByFinancial():
    db_conn = ConnectStockDataDb()
    cur_sor = db_conn.cursor()
    select_cmd = "SELECT CODEID, performanceExpressTotalAsset, MAX(performanceExpPubDate) from   " + DbTable.cn_stock_financials_table_name + "   GROUP BY CODEID;"
    select_cursor = cur_sor.execute(select_cmd)
    stockfinancial_map = {}
    for row in select_cursor:
        if len(row) >= 3 and None != row[1]:
            print(row[1])
            stockfinancial_map[row[0]] = int(row[1])
    db_conn.close()
    sorted_tuple = sorted(stockfinancial_map.items(), key = lambda kv : kv[1], reverse=True)
    sorted_stockid = [item[0] for item in sorted_tuple]
    return sorted_stockid


def GetCNSortedStockByFinancialStock(stock_list):
    db_conn = ConnectStockDataDb()
    cur_sor = db_conn.cursor()
    stock_str = '(' + ', '.join("'%s'"%item for item in stock_list) + ')'
    select_cmd = "SELECT CODEID, performanceExpressTotalAsset, MAX(performanceExpPubDate) from   " + DbTable.cn_stock_financials_table_name + "  WHERE CODEID in  " + stock_str + '   GROUP BY CODEID;'
    select_cursor = cur_sor.execute(select_cmd) 
    stockfinancial_map = {}
    for row in select_cursor:
        if len(row) >= 3 and None != row[1]:
            stockfinancial_map[row[0]] = float(row[1])
    db_conn.close()
    sorted_tuple = sorted(stockfinancial_map.items(), key = lambda kv : kv[1], reverse=True)
    sorted_stockid = [item[0] for item in sorted_tuple]
    return sorted_stockid


def GetCNStockByFinancialStockAsset(stock_list, total_asset):
    db_conn = ConnectStockDataDb()
    cur_sor = db_conn.cursor()
    stock_str = '(' + ', '.join("'%s'"%item for item in stock_list) + ')'
    select_cmd = "SELECT CODEID, performanceExpressTotalAsset, MAX(performanceExpPubDate) from   " + DbTable.cn_stock_financials_table_name + "  WHERE CODEID in  " + stock_str + '   GROUP BY CODEID;'
    select_cursor = cur_sor.execute(select_cmd) 
    stockfinancial_map = {}
    for row in select_cursor:
        if len(row) >= 3 and None != row[1]:
            if float(row[1]) < total_asset:
                continue
            stockfinancial_map[row[0]] = float(row[1])
    db_conn.close()
    sorted_tuple = sorted(stockfinancial_map.items(), key = lambda kv : kv[1], reverse=True)
    sorted_stockid = [item[0] for item in sorted_tuple]
    return sorted_stockid



####################################################################################################################################################
####################################################CN_STOCK_FINANCIALS A股股票日K线数据的db操作函数 END################################################



####################################################################################################################################################
####################################################CN_STOCK_PLATINFO A股行业的db操作函数 START##############################################
def CreateCNStockIndustryTable():
    conn = ConnectStockDataDb()
    cur_sor = conn.cursor()
    try:
        cur_sor.execute(DbTable.cn_stock_plat_table)
        conn.commit()
        create_index_cmd = "CREATE INDEX '" + DbTable.cn_stock_plat_index + "' on " + DbTable.cn_stock_plat_table_name + "(" + DbTable.cn_stock_plat_index + ")"
        cur_sor.execute(create_index_cmd)
        conn.commit()
        print("stock kdata Table created successfully")
    except:
        print('the CN_STOCK_PLATINFO has created')


def InsertCNStockIndustryTable(data_list):
    db_conn = ConnectStockDataDb()
    cur_sor = db_conn.cursor()
    for updateDate, code, code_name, industry, industryClassification in data_list:
        values_str = "VALUES ('" + code +  "' , '" + updateDate + "', '" + str(code_name) + "', '" + str(industry) + "', '" + str(industryClassification) + "')"
        insert_cmd_str = "INSERT INTO CN_STOCK_PLATINFO(CODEID, updateDate, code_name, industry, industryClassification) " + values_str
        try:
            cur_sor.execute(insert_cmd_str)
        except:
            print(insert_cmd_str + '  error!!!!')
    db_conn.commit()
    db_conn.close()



def GetAllIndustryFromStockTable():
    db_conn = ConnectStockDataDb()
    select_cmd = "select distinct industry from " + DbTable.cn_stock_plat_table_name + ";"
    cur_sor = db_conn.cursor()
    select_cursor = cur_sor.execute(select_cmd)
    result_list = list(chain.from_iterable(select_cursor.fetchall()))
    db_conn.close()
    return result_list


def GetStockCodeByIndustry(industry):
    db_conn = ConnectStockDataDb()
    select_cmd = "select CODEID from " + DbTable.cn_stock_plat_table_name + " where industry='" + industry +"';"
    cur_sor = db_conn.cursor()
    select_cursor = cur_sor.execute(select_cmd)
    result_list = list(chain.from_iterable(select_cursor.fetchall()))
    db_conn.close()
    return result_list

####################################################################################################################################################
####################################################CN_STOCK_PLATINFO A股行业数据的db操作函数 END################################################