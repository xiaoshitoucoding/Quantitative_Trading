import requests
import time
import execjs
from bs4 import BeautifulSoup
import re
import numpy as np
import pandas as pd


class FundUtil():
    @staticmethod
    def getUrl(fscode):
        head = 'http://fund.eastmoney.com/pingzhongdata/'
        tail = '.js?v='+ time.strftime("%Y%m%d%H%M%S",time.localtime())
        return head+fscode+tail


    #获取净值
    @staticmethod
    def getWorth(fscode):
        #用requests获取到对应的文件
        content = requests.get(FundUtil.getUrl(fscode))
        #使用execjs获取到相应的数据
        jsContent = execjs.compile(content.text)
        name = jsContent.eval('fS_name')
        code = jsContent.eval('fS_code')
        #单位净值走势
        netWorthTrend = jsContent.eval('Data_netWorthTrend')
        #累计净值走势
        ACWorthTrend = jsContent.eval('Data_ACWorthTrend')
        print(len(netWorthTrend))
        print(len(ACWorthTrend))
        # netWorth = []
        # ACWorth = []
        # #提取出里面的净值
        # for dayWorth in netWorthTrend[::-1]:
        #     netWorth.append(dayWorth['y'])
        # for dayACWorth in ACWorthTrend[::-1]:
        #     ACWorth.append(dayACWorth[1])
        # print(name,code)
        # return netWorth, ACWorth


class FundDataFrameUtil():
    # 抓取网页
    @staticmethod
    def get_url(url, params=None, proxies=None):
        rsp = requests.get(url, params=params, proxies=proxies)
        rsp.raise_for_status()
        return rsp.text

    # 从网页抓取数据
    @staticmethod
    def get_fund_data(code,per=10,sdate='',edate='',proxies=None):
        url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx'
        params = {'type': 'lsjz', 'code': code, 'page':1,'per': per, 'sdate': sdate, 'edate': edate}
        html = FundDataFrameUtil.get_url(url, params, proxies)
        soup = BeautifulSoup(html, 'html.parser')

        # 获取总页数
        pattern=re.compile(r'pages:(.*),')
        result=re.search(pattern,html).group(1)
        pages=int(result)

        # 获取表头
        heads = []
        for head in soup.findAll("th"):
            heads.append(head.contents[0])

        # 数据存取列表
        records = []

        # 从第1页开始抓取所有页面数据
        page=1
        while page<=pages:
            params = {'type': 'lsjz', 'code': code, 'page':page,'per': per, 'sdate': sdate, 'edate': edate}
            html = FundDataFrameUtil.get_url(url, params, proxies)
            soup = BeautifulSoup(html, 'html.parser')

            # 获取数据
            for row in soup.findAll("tbody")[0].findAll("tr"):
                row_records = []
                for record in row.findAll('td'):
                    val = record.contents

                    # 处理空值
                    if val == []:
                        row_records.append(np.nan)
                    else:
                        row_records.append(val[0])

                # 记录数据
                records.append(row_records)

            # 下一页
            page=page+1

        # 数据整理到dataframe
        np_records = np.array(records)
        data= pd.DataFrame()
        for col,col_name in enumerate(heads):
            data[col_name] = np_records[:,col]

        data['净值日期']=pd.to_datetime(data['净值日期'],format='%Y-%m-%d')
        data['单位净值']= data['单位净值'].astype(float)
        data['累计净值']=data['累计净值'].astype(float)
        data['日增长率']=data['日增长率'].str.strip('%').astype(float)
        # 按照日期升序排序并重建索引
        data=data.sort_values(by='净值日期',axis=0,ascending=True).reset_index(drop=True)
        data.to_csv('./FundCsv/' + code + '.csv')
        return data    


