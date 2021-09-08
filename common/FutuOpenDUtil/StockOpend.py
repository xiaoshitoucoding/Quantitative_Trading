from futu import *
from Util import DbUtil
import time
from Trade.KLManager import split_k_market
from Util.DateUtil import current_str_date
from Util import DateUtil



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


def GetCurStockKline(quote_ctx, stock_list, kline_num, kline_type = SubType.K_DAY, autype = AuType.QFQ):
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




def SetStockNameByPlateToDb(db_conn, market_type, plate_class = Plate.CONCEPT):
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    ret, data = quote_ctx.get_plate_list(market_type, plate_class)
    if ret == RET_OK:
        for index, row in data.iterrows():
            stockname_ret, stockname_data = quote_ctx.get_plate_stock(row['code'])
            if stockname_ret == RET_OK:
                stockname_data.drop(['stock_owner', 'stock_child_type'], axis=1,inplace=True)
                stockname_data['plate_name'] = row['plate_name']
                stockname_data['plate_id'] = row['plate_id']
                stockname_data['market_type'] = market_type
                stockname_list = stockname_data.values.tolist() 
                DbUtil.InsertStockNameTodataTable(db_conn, stockname_list)   
            else:
                print("plat stock erro:", stockname_data)    
            time.sleep(3)
    else:
        print('error:', data)
    quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽


#根据板块股票的codeid导入对应的股票数据
def GetAllStockDataByPlate(start_date, end_date):
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    stockname_pb = DbUtil.GetAllStockNameFromTable()
    stockname_list = stockname_pb['code'].values.tolist()
    #过滤掉已有的股票
    already_stockid = DbUtil.GetAllStockCodeIdFromStockTable()
    stockname_list = list(set(stockname_list).difference(set(already_stockid)))
    split_stockname_list = split_k_market(10, stockname_list)
    for stockname_item in split_stockname_list:
        print(stockname_item)
        all_stock_kline_data = GetStockHistoryKline(quote_ctx, stockname_item, SubType.K_DAY, start_date, end_date)
        # all_stock_kline_data = GetStockHistoryKline(quote_ctx, stockname_item, SubType.K_DAY, '2019-01-01', '2020-12-31')
        for stock_name, stock_data in all_stock_kline_data.items():
            stock_list = stock_data.values.tolist()
            for stock_line in stock_list:
                stock_line.insert(1, SubType.K_DAY)
            DbUtil.InsertDataListToKdataTable(stock_list)
        time.sleep(5)
    quote_ctx.close()



#跟新db中所有股票的k线数据
def UpdateAllStockDataToDb(db_conn, start_date, end_date):
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    already_stockid = DbUtil.GetAllStockCodeIdFromStockTable()
    split_stockname_list = split_k_market(100, already_stockid) 
    for stockname_item in split_stockname_list:
        print(stockname_item)
        all_stock_kline_data = GetStockHistoryKline(quote_ctx, stockname_item, SubType.K_DAY, start_date, end_date)
        for stock_name, stock_data in all_stock_kline_data.items():
            stock_list = stock_data.values.tolist()
            for stock_line in stock_list:
                stock_line.insert(1, SubType.K_DAY)
            DbUtil.InsertDataListToKdataTable(db_conn, stock_list)
        time.sleep(5)
    quote_ctx.close()


#跟新db中所有股票的k线数据
def UpdateCurAllStockDataToDb(kline_num):
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    stockname_list = DbUtil.GetAllStockCodeIdFromStockTable()
    already_stockid = DbUtil.GetAllStockCodeIdFromStockTable('2021-06-18 00:00:00')
    stockname_list = list(set(stockname_list).difference(set(already_stockid)))
    split_stockname_list = split_k_market(10, stockname_list) 
    print(split_stockname_list)
    for stockname_item in split_stockname_list:
        stockname_item = list(stockname_item)
        all_stock_kline_data = GetCurStockKline(quote_ctx, stockname_item, kline_num, SubType.K_DAY)
        for stock_name, stock_data in all_stock_kline_data.items():
            stock_list = stock_data.values.tolist()
            for stock_line in stock_list:
                stock_line.insert(1, SubType.K_DAY)
            DbUtil.InsertCurDataListToKdataTable(stock_list)
        time.sleep(5)
    quote_ctx.close()



def UpdateAllStockToCurDate():
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    str_curdate = current_str_date()
    stockname_list = DbUtil.GetAllStockCodeIdFromStockTable()
    already_stockid = DbUtil.GetAllStockCodeIdFromStockTable(str_curdate + ' 00:00:00')
    stockname_list = list(set(stockname_list).difference(set(already_stockid)))
    split_stockname_list = split_k_market(10, stockname_list) 
    standard_stock_time = DbUtil.GetMaxTimeByCodeId('HK.800000')
    print('str_curdate', str_curdate, 'standard_stock_time', standard_stock_time)
    # diff_days = DateUtil.workdays_diff(standard_stock_time, str_curdate)
    diff_days = 10

    for stockname_item in split_stockname_list:
        stockname_item = list(stockname_item)
        all_stock_kline_data = GetCurStockKline(quote_ctx, stockname_item, diff_days, SubType.K_DAY)
        for stock_name, stock_data in all_stock_kline_data.items():
            stock_list = stock_data.values.tolist()
            for stock_line in stock_list:
                stock_line.insert(1, SubType.K_DAY)
            DbUtil.InsertCurDataListToKdataTable(stock_list)
        time.sleep(5)
    quote_ctx.close()
    



