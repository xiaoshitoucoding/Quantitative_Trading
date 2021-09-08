# -*- encoding:utf-8 -*-
from __future__ import absolute_import

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from Util.DbUtil import ConnectStockDataDb, GetStockDataOrderTimeByCode
from Util.DateUtil import _calc_start_end_date, week_of_date, str_to_datetime
from Util import DateUtil
from Indicator import ATR
from Indicator import NDRsi
from CoreBase import Env
from CoreBase.Parallel import Parallel, delayed
from collections import Iterable
from Trade.KLManager import split_k_market
from functools import partial



def _benchmark(df, benchmark, symbol):
    """
    在内部使用kline_pd获取金融时间序列pd.DataFrame后，如果参数中
    基准benchmark（pd.DataFrame对象）存在，使用基准benchmark的
    时间范围切割kline_pd返回的金融时间序列
    :param df: 金融时间序列pd.DataFrame对象
    :param benchmark: 资金回测时间标尺，Benchmark实例对象
    :param symbol: Symbol对象
    :return: 使用基准的时间范围切割返回的金融时间序列
    """
    if len(df.index & benchmark.kl_pd.index) <= 0:
        # 如果基准benchmark时间范围和输入的df没有交集，直接返回None
        return None

    # 两个金融时间序列通过loc寻找交集
    kl_pd = df.loc[benchmark.kl_pd.index]
    # nan的date个数即为不相交的个数
    nan_cnt = kl_pd['date'].isnull().value_counts()
    # 两个金融序列是否相同的结束日期
    same_end = df.index[-1] == benchmark.kl_pd.index[-1]
    # 两个金融序列是否相同的开始日期
    same_head = df.index[0] == benchmark.kl_pd.index[0]

    # 如果nan_cnt即不相交个数大于benchmark基准个数的1/3，放弃
    base_keep_div = 3
    if same_end or same_head:
        # 如果两个序列有相同的开始或者结束改为1/2，也就是如果数据头尾日起的标尺有一个对的上的话，放宽na数量
        base_keep_div = 2
    if same_end and same_head:
        # 如果两个序列同时有相同的开始和结束改为1，也就是如果数据头尾日起的标尺都对的上的话，na数量忽略不计
        base_keep_div = 1

    if symbol.is_a_stock():
        # 如果是A股市场的目标，由于停盘频率和周期都会长与其它市场所以再放宽一些
        base_keep_div *= 0.7

    if nan_cnt.index.shape[0] > 0 and nan_cnt.index.tolist().count(True) > 0 \
            and nan_cnt.loc[True] > benchmark.kl_pd.shape[0] / base_keep_div:
        # nan 个数 > 基准base_keep_div分之一放弃
        return None

    # 来到这里说明没有放弃，那么就填充nan
    # 首先nan的交易量是0
    kl_pd.volume.fillna(value=0, inplace=True)
    # nan的p_change是0
    kl_pd.p_change.fillna(value=0, inplace=True)
    # 先把close填充了，然后用close填充其它的
    kl_pd.close.fillna(method='pad', inplace=True)
    kl_pd.close.fillna(method='bfill', inplace=True)
    # 用close填充open
    kl_pd.open.fillna(value=kl_pd.close, inplace=True)
    # 用close填充high
    kl_pd.high.fillna(value=kl_pd.close, inplace=True)
    # 用close填充low
    kl_pd.low.fillna(value=kl_pd.close, inplace=True)
    # 用close填充pre_close
    kl_pd.pre_close.fillna(value=kl_pd.close, inplace=True)

    # 细节nan处理完成后，把剩下的nan都填充了
    kl_pd = kl_pd.fillna(method='pad')
    # bfill再来一遍只是为了填充最前面的nan
    kl_pd.fillna(method='bfill', inplace=True)

    # pad了数据所以，交易日期date的值需要根据time index重新来一遍
    kl_pd['date'] = [int(ts.date().strftime("%Y%m%d")) for ts in kl_pd.index]
    kl_pd['date_week'] = kl_pd['date'].apply(lambda x: week_of_date(str(x), '%Y%m%d'))

    return kl_pd

def combine_pre_kl_pd(kl_pd, n_folds=1):
    """
    通过传一个kl_pd获取这个kl_pd之前n_folds年时间的kl，默认n_folds=1,
    eg. kl_pd 从2014-07-26至2016-07-26，首先get 2013-07-26至2014-07-25
    之后合并两段数据，最终返回的数据为2013-07-26至2016-07-26
    :param kl_pd: 金融时间序列pd.DataFrame对象
    :param n_folds: 获取之前n_folds年的数据
    :return: 结果是和输入kl_pd合并后的总kl
    """

    # 获取kl_pd的起始时间
    end = DateUtil.timestamp_to_str(kl_pd.index[0])
    # kl_pd的起始时间做为end参数通过make_kl_df和n_folds参数获取之前的一段时间序列
    pre_kl_pd = make_kl_df(kl_pd.name,  n_folds=n_folds,
                           end=end)
    # 再合并两段时间序列，pre_kl_pd[:-1]跳过重复的end
    combine_kl = kl_pd if pre_kl_pd is None else pre_kl_pd[:-1].append(kl_pd)
    # 根据combine_kl长度重新进行key计算
    combine_kl['key'] = list(range(0, len(combine_kl)))
    return combine_kl



def calc_atr(kline_df):
    """
    为输入的kline_df金融时间序列计算atr21和atr14，计算结果直接加到kline_df的atr21列和atr14列中
    :param kline_df: 金融时间序列pd.DataFrame对象
    """
    if kline_df is None:
        return
    kline_df['atr21'] = 0
    if kline_df.shape[0] > 21:
        # 大于21d计算atr21
        kline_df['atr21'] = ATR.atr21(kline_df['high'].values, kline_df['low'].values, kline_df['close'].values)
        # 将前面的bfill
        kline_df['atr21'].fillna(method='bfill', inplace=True)
    kline_df['atr14'] = 0
    if kline_df.shape[0] > 14:
        # 大于14d计算atr14
        kline_df['atr14'] = ATR.atr14(kline_df['high'].values, kline_df['low'].values, kline_df['close'].values)
        # 将前面的bfill
        kline_df['atr14'].fillna(method='bfill', inplace=True)

def calc_rsi(kline_df):
    if kline_df is None:
        return
    kline_df['rsi'] = NDRsi._calc_rsi_from_ta(kline_df.close)
    kline_df['rsi'].fillna(method='bfill', inplace=True)

def calc_volumerank(kline_df):
    if kline_df is None:
        return
    kline_df['vol_rank'] = kline_df.volume.rank(method='first')
    list_len = len(kline_df.vol_rank)
    kline_df['vol_rank'] = kline_df['vol_rank'].map(lambda x: float((2*x - list_len)/list_len))
    kline_df['price_rate'] = (kline_df['close'] - kline_df['open'])/kline_df['close'] * 100

    

# noinspection PyDeprecation
def _make_kl_df(stock_id, n_folds=2, start=None, end=None, benchmark=None):
    """
    外部获取金融时间序列接口
    eg: n_fold=2, start=None, end=None ，从今天起往前数两年
        n_fold=2, start='2015-02-14', end=None， 从2015-02-14到现在，n_fold无效
        n_fold=2, start=None, end='2016-02-14'，从2016-02-14起往前数两年
        n_fold=2, start='2015-02-14', end='2016-02-14'，从start到end

    :param data_mode: EMarketDataSplitMode对象
    :param symbol: list or Series or str or Symbol
                    e.g :['TSLA','SFUN'] or 'TSLA' or Symbol(MType.US,'TSLA')
    :param n_folds: 请求几年的历史回测数据int
    :param start: 请求的开始日期 str对象
    :param end: 请求的结束日期 str对象
    :param benchmark: 资金回测时间标尺，Benchmark实例对象

    :param parallel: 是否并行获取
    :param parallel_save: 是否并行后进行统一批量保存
    """

    db_conn = ConnectStockDataDb()

    stock_data = GetStockDataOrderTimeByCode(db_conn, stock_id)
    db_conn.close()
    end, end_int, df_end_int, start, start_int, df_start_int = _calc_start_end_date(stock_data, 0, n_folds, start, end)
    save_kl_key = (stock_id, df_start_int, df_end_int)
     # 检测本地缓存数据是否满足需要，如果需要的数据在存储的数据之间，则可切片放回


    match = False


    if start_int >= df_start_int and end_int <= df_end_int:
        match = True
    if match:
        # 如果满足，且模式需要根据切割df的进行切割筛选
        stock_data = stock_data[(start_int <= stock_data.date) & (stock_data.date <= end_int)]


    if stock_data is not None and stock_data.shape[0] == 0:
        # 把行数＝0的归结为＝None, 方便后续统一处理
        stock_data = None

    # if benchmark is not None and stock_data is not None:
    #     # 如果有标尺，进行标尺切割，进行标尺切割后也可能变成none
    #     temp_symbol = save_kl_key[0]
    #     stock_data = _benchmark(stock_data, benchmark, temp_symbol)   

    if stock_data is not None:
        calc_atr(stock_data)
        calc_rsi(stock_data)
        calc_volumerank(stock_data)

        # 根据df长度重新进行key计算
        stock_data['key'] = list(range(0, len(stock_data)))
    return stock_data, save_kl_key



    # noinspection PyDeprecation
def make_kl_df(symbol, n_folds=2, start=None, end=None, benchmark=None, parallel=False):
    """
    外部获取金融时间序列接口
    eg: n_fold=2, start=None, end=None ，从今天起往前数两年
        n_fold=2, start='2015-02-14', end=None， 从2015-02-14到现在，n_fold无效
        n_fold=2, start=None, end='2016-02-14'，从2016-02-14起往前数两年
        n_fold=2, start='2015-02-14', end='2016-02-14'，从start到end

    :param data_mode: EMarketDataSplitMode对象
    :param symbol: list or Series or str or Symbol
                    e.g :['TSLA','SFUN'] or 'TSLA' or Symbol(MType.US,'TSLA')
    :param n_folds: 请求几年的历史回测数据int
    :param start: 请求的开始日期 str对象
    :param end: 请求的结束日期 str对象
    :param benchmark: 资金回测时间标尺，Benchmark实例对象
    :param show_progress: 是否显示进度条
    :param parallel: 是否并行获取
    :param parallel_save: 是否并行后进行统一批量保存
    """

    if isinstance(symbol, (list, tuple, pd.Series, pd.Index)):
        # 如果symbol是可迭代的序列对象，最终返回三维面板数据pd.Panel
        panel = dict()
        if parallel:
            df_dicts = kl_df_dict_parallel(symbol, n_folds=n_folds, start=start, end=end,
                                           benchmark=benchmark, how='process')
            for df_dict in df_dicts:
                for key_tuple, df in df_dict.values():
                    if df is None or df.shape[0] == 0:
                        continue
                    panel[key_tuple[0].value] = df
        else:
            def _batch_make_kl_df():         
                for pos, _symbol in enumerate(symbol):
                    _df, _ = _make_kl_df(_symbol, n_folds=n_folds, start=start, end=end, 
                                            benchmark=benchmark)
        
                    # TODO 做pd.Panel数据应该保证每一个元素的行数和列数都相等，不是简单的有数据就行
                    if _df is None or _df.shape[0] == 0:
                        continue

                    panel[symbol[pos]] = _df

            _batch_make_kl_df()
        # TODO pd.Panel过时
        return pd.Panel(panel)

    else:
        # 对单个symbol进行数据获取
        df, _ = _make_kl_df(symbol, n_folds=n_folds, start=start, end=end, benchmark=benchmark)
        return df




def _kl_df_dict_parallel(choice_symbols, n_folds, start, end, benchmark):
    """
    多进程或者多线程被委托的任务函数，多任务批量获取时间序列数据
    :param choice_symbols: symbol序列
    :param data_mode: EMarketDataSplitMode enum对象
    :param n_folds: 请求几年的历史回测数据int
    :param start: 请求的开始日期 str对象
    :param end: 请求的结束日期 str对象
    :param benchmark: 资金回测时间标尺，Benchmark实例对象
    :return: df_dict字典中key=请求symbol的str对象，value＝(save_kl_key: 提供外部进行保存, df: 金融时间序列pd.DataFrame对象)
    """
    df_dict = {}
    # 注意save=False

    for epoch, symbol in enumerate(choice_symbols):
        # 迭代choice_symbols进行_make_kl_df, 注意_make_kl_df的参数save=False，即并行获取，不在内部save，要在外部save
        df, key_tuple = _make_kl_df(symbol, n_folds=n_folds, start=start, end=end, 
                                    benchmark=benchmark)
        if isinstance(key_tuple, tuple) and len(key_tuple) == 3:
            # key=请求symbol的str对象，value＝(save_kl_key: 提供外部进行保存, df: 金融时间序列pd.DataFrame对象)
            df_dict[key_tuple[0].value] = (key_tuple, df)
    return df_dict




def kl_df_dict_parallel(symbols, n_folds=2, start=None, end=None, benchmark=None, n_jobs=16, how='process'):
    """
    多进程或者多线程对外执行函数，多任务批量获取时间序列数据
    :param symbols: symbol序列
    :param data_mode: EMarketDataSplitMode enum对象
    :param n_folds: 请求几年的历史回测数据int
    :param start: 请求的开始日期 str对象
    :param end: 请求的结束日期 str对象
    :param benchmark: 资金回测时间标尺，Benchmark实例对象
    :param n_jobs: 并行的任务数，对于进程代表进程数，线程代表线程数
    :param save: 是否统一进行批量保存，即在批量获取金融时间序列后，统一进行批量保存，默认True
    :param how: process：多进程，thread：多线程，main：单进程单线程
    """

    # TODO Iterable和six.string_types的判断抽出来放在一个模块，做为Iterable的判断来使用
    if not isinstance(symbols, Iterable) or isinstance(symbols, six.string_types):
        # symbols必须是可迭代的序列对象
        raise TypeError('symbols must a Iterable obj!')
    # 可迭代的symbols序列分成n_jobs个子序列
    parallel_symbols = split_k_market(n_jobs, market_symbols=symbols)
    # 使用partial对并行函数_kl_df_dict_parallel进行委托
    parallel_func = partial(_kl_df_dict_parallel, n_folds=n_folds, start=start, end=end,
                            benchmark=benchmark)
    # 因为切割会有余数，所以将原始设置的进程数切换为分割好的个数, 即32 -> 33 16 -> 17
    n_jobs = len(parallel_symbols)
    if how == 'process':


        parallel = Parallel(
            n_jobs=n_jobs, verbose=0, pre_dispatch='2*n_jobs')
        df_dicts = parallel(delayed(parallel_func)(choice_symbols)
                            for choice_symbols in parallel_symbols)
    elif how == 'main':
        # 单进程单线程
        df_dicts = [parallel_func(symbols) for symbols in parallel_symbols]
    else:
        raise TypeError('ONLY process OR thread!')

   
    return df_dicts

    









