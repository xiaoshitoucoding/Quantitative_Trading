from FutuOpenDUtil.FundUtil import FundDataFrameUtil
from Util.DateUtil import getn_afterdate, diff

import os
import pandas as pd
import numpy as np

SSEC = '000001'
CSI300 = '000300'
root_dir = './FundCsv/FundData/'
result_dir = './FundCsv/FundResult/'

g_fund_standard = 4500
g_fund_skip = 200
g_buy_rate = 0.01
g_captical = 10000


g_target_fundmap = {
                    '161005': 0.04,
                    '163406': 0.05,
                    '005794': 0.06,
                    '001216': 0.06,
                    '001603': 0.05,
                    '001679': 0.06,
                    '001000': 0.07,
                    '002803': 0.06,
                    '160424': 0.07,
                    '001054': 0.05,
                    '001694': 0.04,
                    '040035': 0.06,
                    '005136': 0.04,
                    '005001': 0.06,
                    '519642': 0.02,
                    '005760': 0.06,
                    '006259': 0.06,
                    '519702': 0.04,
                    '007130': 0.05,
                    '000300': 0
                }   
def GetTargeFundData():
    
    sdate='2017-01-01'
    edate='2021-08-09' 
    for target_fund in g_target_fundmap.keys():
        FundDataFrameUtil.get_fund_data(code=target_fund, sdate=sdate, edate=edate)

def ReadFundDataFromCsv():
    fundata_map = {}
    files= os.listdir(root_dir)
    for filename in files:
        fund_name = os.path.splitext(filename)[0]
        if fund_name not in g_target_fundmap.keys():
            continue
        filename = root_dir + filename
        cur_pd = pd.read_csv(filename, thousands=',')
        fundata_map[fund_name] = cur_pd
    return fundata_map


class FundStrategy():
    def __init__(self, standard_pd):


        standard_pd['date']=pd.to_datetime(standard_pd['日期'],format='%Y年%m月%d日')
        standard_pd['date']=standard_pd['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
        self.m_standard_pd = standard_pd.sort_values(by='date',axis=0,ascending=True).reset_index(drop=True)
        self.m_standard_pd.rename(columns={'开盘':'standard_open'}, inplace = True)
        self.merge_standard_pd = self.m_standard_pd.loc[:,['date','standard_open']]



    
    def GetSkipRateByStandard(self, cur_price):
        return int((cur_price-g_fund_standard)/g_fund_skip)
    
    def BuyMoneyByStandard(self, cur_price, captial):
        n = self.GetSkipRateByStandard(cur_price)
        if n >= 0:
            return -pow(n, 2) * g_buy_rate * captial + captial
        else:
            return pow(n, 2) * g_buy_rate * captial + captial
        # return -((n+1)*n/2) * captial + captial
    
    def GetBuyDateFromPd(self, base_fund_pd):
        start_date = '2017-01-06'
        end_date = '2021-01-06'
        base_fund_pd.rename(columns={'净值日期':'date'}, inplace = True)
        base_fund_pd.rename(columns={'单位净值':'value'}, inplace = True)
        

        #根据base fun对standard fun剪裁
        start_index = self.merge_standard_pd[self.merge_standard_pd['date']== base_fund_pd['date'].iloc[0]].index.tolist()[0]
        end_index =  self.merge_standard_pd[self.merge_standard_pd['date']== base_fund_pd['date'].iloc[-1]].index.tolist()[0]

        merge_standard_pd = self.merge_standard_pd.loc[start_index:end_index,]
        base_fund_pd = pd.merge(base_fund_pd, merge_standard_pd, on = 'date')
        base_fund_pd['buy_date'] = base_fund_pd['date'].apply(lambda x : 1 if diff(start_date, x)%7 == 0 else 0)
        base_fund_pd =  base_fund_pd[base_fund_pd['buy_date'] == 1]
        base_fund_pd = base_fund_pd[['date', 'value', 'standard_open', 'buy_date']]
        return base_fund_pd

        # standard_pb['date']=pd.to_datetime(standard_pb['日期'],format='%Y年%m月%d日')
        # standard_pb['date']=standard_pb['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
        # standard_pb['buy_date'] = standard_pb['date'].apply(lambda x : 1 if diff(start_date, x)%7 == 0 else 0)
        # return standard_pb[standard_pb['buy_date'] == 1]


    
    def CalcFund(self, base_fund_pd, captial, fund_name):
        fund_pd = self.GetBuyDateFromPd(base_fund_pd=base_fund_pd)
        fund_pd['buy_money'] = fund_pd['standard_open'].apply(lambda x: self.BuyMoneyByStandard(x, captial))
        fund_pd['buy_num'] = fund_pd['buy_money']/fund_pd['value']
        fund_file_name = result_dir + fund_name + '.xlsx'
        fund_pd.to_excel(fund_file_name, sheet_name='购买详情', float_format='%.4f', na_rep=' ')
        result_list = []
        result_list.append(fund_name)
        result_list.append(len(fund_pd))
        buy_money = fund_pd['buy_money'].sum()
        result_list.append(buy_money)
        buy_num = fund_pd['buy_num'].sum()
        result_list.append(buy_num)
        cur_price = fund_pd['value'].iloc[-1]
        benfit = cur_price*buy_num - buy_money
        result_list.append(benfit)
        result_list.append(benfit/buy_money)
        return result_list
        

        




if __name__ == "__main__":
    fundata_map = ReadFundDataFromCsv()
    csi300_pd = fundata_map[CSI300]
    fund_strategy = FundStrategy(csi300_pd)
    result_list = []
    for fund_name in fundata_map.keys():
        fund_data = fundata_map[fund_name]
        if fund_name == CSI300 or fund_name == SSEC:
            continue
        cur_captial = g_captical * g_target_fundmap[fund_name]
        result_list.append(fund_strategy.CalcFund(fund_data, cur_captial, fund_name))
    csv_dataframe = pd.DataFrame(result_list, columns=['基金名称', '购买次数', '花费总金额', '购买总数量', '总策略收益', '总收益比率'])
    result_filename = result_dir + 'Benfit.xlsx'
    csv_dataframe.to_excel(result_filename, sheet_name='收益', float_format='%.4f', na_rep=' ')


    #获取基金数据
    # GetTargeFundData()
    