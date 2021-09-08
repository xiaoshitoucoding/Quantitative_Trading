from __future__ import absolute_import


from CoreBase.StockPb import make_kl_df
from CoreBase.Benchmark import *
from CoreBase.Parallel import Parallel, delayed
from futu import *
from FutuOpenDUtil import StockOpend
from Util import DbUtil



#根据板块导入股票的名字
# if __name__ == '__main__':    
#     db_conn = DbUtil.ConnectStockDataDb()   
#     #DbUtil.CreatePlateStocknameTable(db_conn)
#     StockOpend.SetStockNameByPlateToDb(db_conn, Market.HK)


# # #根据板块股票的codeid导入对应的股票数据
# if __name__ == '__main__':    
#     db_conn = DbUtil.ConnectStockDataDb()   
#     StockOpend.UpdateAllStockDataToDb(db_conn, '2021-01-01', '2021-06-07')
#     db_conn.close()



# #根据板块股票的codeid导入对应的股票数据
if __name__ == '__main__':    
    # StockOpend.UpdateCurAllStockDataToDb(11)
    # StockOpend.UpdateAllStockToCurDate()
    StockOpend.GetAllStockDataByPlate('2018-01-01', '2021-06-29')
    



    




