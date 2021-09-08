from futu import *
import pandas as pd



def GetOptionChain(quote_ctx, option_code, start_time, end_time, option_type, option_conf_type, data_filter):
    ret, data = quote_ctx.get_option_chain(option_code, IndexOptionType.NORMAL, start_time, end_time, option_type, option_conf_type, data_filter)
    if ret == RET_OK:
        return data
    else:
        print('error:', data)


def GetOptionOrStockPriceData(quote_ctx, option_code_list, sub_type_list, subscribe_push=False):
    # 先订阅 K 线类型。订阅成功后 FutuOpenD 将持续收到服务器的推送，False 代表暂时不需要推送给脚本
    ret_sub, err_message = quote_ctx.subscribe(option_code_list, sub_type_list, subscribe_push=False)
    if ret_sub == RET_OK:  # 订阅成功
        ret, data = quote_ctx.get_stock_quote(option_code_list)  # 获取订阅股票报价的实时数据
        if ret == RET_OK:
            return data
        else:
            print('error:', data)
    else:
        print('subscription failed', err_message)

if __name__ == '__main__':
    print(type(OptionCondType))
    print(OptionCondType.WITHIN)
    #quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    #data_filter = OptionDataFilter()
    #data_filter.vol_min = 50 
    #data_filter.vol_max = 10000 
    #data = GetOptionChain('US.INTC', '2021-05-01', '2021-05-30', OptionType.PUT, OptionCondType.OUTSIDE, data_filter)
    #print(data)
    #quote_ctx.close()





