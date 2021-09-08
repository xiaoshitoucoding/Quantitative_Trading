from datetime import datetime,timedelta
from polygon import RESTClient
# from lib import mysql
import json
import config


key=config.key


def get_date(num,formats='%Y%m%d'):
    return (datetime.today()+timedelta(-num)).strftime(formats)

def get_entire_symbol(date):
    results=[]
    with RESTClient(key) as client:
        resp=client.stocks_equities_grouped_daily(locale="us",market="stocks",date=date)
        if resp.resultsCount!=0:
            for result in resp.results:
                result["t"]=date
                results.append(result)
            print(results[:10])
            # mysql.insert_stock_record.run(results)
        else:
            print("No Trade")

if __name__ == '__main__':
    num=1
    date=get_date(num,"%Y-%m-%d")
    get_entire_symbol(date)

