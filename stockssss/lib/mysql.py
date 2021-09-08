import time
import asyncio
import aiomysql
import pymysql
from datetime import datetime
from config import mysqldb_conn


def retry(func):
    def retrys(*args, **kwargs):
        for times in range(3):
            try:
                return func(*args, **kwargs)
                break
            except Exception as e:
                print(e)
                time.sleep(10)

    return retrys


def add_run(func):
    def run(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop = asyncio.get_event_loop()
        mysql = loop.run_until_complete(getAmysqlobj())
        if args:
            results = []
            tmp_list = []
            for ip in args[0]:
                tmp_list.append(ip)
                if (len(tmp_list) == 6000):
                    tasks = asyncio.gather(*[func(mysql, info) for info in tmp_list])
                    loop.run_until_complete(tasks)
                    result = tasks.result()
                    results.extend(result)
                    tmp_list = []
            tasks = asyncio.gather(*[func(mysql, info) for info in tmp_list])
            loop.run_until_complete(tasks)
            result = tasks.result()
            results.extend(result)

        if kwargs:
            tasks = asyncio.gather(*[func(mysql=mysql, **kwargs)])
            loop.run_until_complete(tasks)
            results = tasks.result()[0]
        if not kwargs and not args:
            tasks = asyncio.gather(*[func(mysql)])
            loop.run_until_complete(tasks)
            results = tasks.result()[0]
        loop.run_until_complete(mysql.close_pool())
        loop.close()
        return results

    def wrapper(func):
        func.run = run
        return func

    return wrapper(func)


class Mysql:
    def __init__(self,db="stock"):
        self.pool = None
        self.db=db

    async def initpool(self):
        self.pool = await aiomysql.create_pool(host=mysqldb_conn["host"], port=mysqldb_conn["port"],
                                          user=mysqldb_conn["user"], password=mysqldb_conn["password"], db=self.db,
                                          minsize=30,maxsize=100,autocommit=True,echo=True)

    @retry
    async def insert(self, table, data):
        """mysql insert() function"""
        async with self.pool.acquire() as connection:
            async with connection.cursor() as cur:
                params = self.join_field_value(data);
                sql = "INSERT INTO {table} SET {params}".format(table=table, params=params)
                try:
                    await cur.execute(sql)
                    #print(sql)
                    #print(cur.lastrowid)
                except Exception as e :
                    print(sql)
                    print(e)
                    return 0

    @retry
    async def replace(self, table,data):
        """mysql insert() function"""
        async with  self.pool.acquire() as connection:
            async with connection.cursor() as cur:
                try:
                    sql = 'INSERT INTO {table} VALUES ("{cmpy}")'.format(table=table,cmpy=cmpy)
                    resut=await cur.execute(sql)
                    print("***********************")
                    print(cur.lastrowid)
                except Exception as e:
                    print(e)

    @retry
    async def delete(self, table, condition=None, limit=None):
        async with  self.pool.acquire() as connection:
            async with connection.cursor() as cursor:
                if not condition:
                    where = '1';
                elif isinstance(condition, dict):
                    where = self.join_field_value(condition, ' AND ')
                else:
                    where = condition

                limits = "LIMIT {limit}".format(limit=limit) if limit else ""

                sql = "DELETE FROM {table} WHERE {where} {limits}".format(
                    table=table, where=where, limits=limits)
                await cursor.execute(sql)

    @retry
    async def update(self, table, data, condition):
        """mysql update() function"""
        async with  self.pool.acquire() as connection:
            async with connection.cursor() as cursor:
                params = self.join_field_value(data)
                if not condition:
                    where = '1';
                elif isinstance(condition, dict):
                    where = self.join_field_value(condition, ' AND ')
                else:
                    where = condition

                sql = "UPDATE {table} SET {params} WHERE {where}".format(
                    table=table, params=params, where=where)

                await cursor.execute(sql)

    @retry
    async def fetch_rows(self, table, fields=None, condition=None, order=None, limit=None, fetchone=False):
        """mysql select() function"""
        async with  self.pool.acquire() as connection:
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                # SELECT FIELDS
                if not fields:
                    fields = '*'
                elif isinstance(fields, tuple) or isinstance(fields, list):
                    fields = '`, `'.join(fields)
                    fields = '`{fields}`'.format(fields=fields)
                else:
                    fields = fields

                # WHERE CONDITION
                if not condition:
                    where = '1';
                elif isinstance(condition, dict):
                    where = self.join_field_value(condition, ' AND ')
                else:
                    where = condition

                # ORDER BY OPTIONS
                if not order:
                    orderby = ''
                else:
                    orderby = 'ORDER BY {order}'.format(order=order)

                # LIMIT NUMS
                limits = "LIMIT {limit}".format(limit=limit) if limit else ""
                sql = "SELECT {fields} FROM {table} WHERE {where} {orderby} {limits}".format(
                    fields=fields,
                    table=table,
                    where=where,
                    orderby=orderby,
                    limits=limits)
                await cursor.execute(sql)

            if fetchone:
                return await cursor.fetchone()
            else:
                return await cursor.fetchall()

    @retry
    async def query(self, sql, fetchone=False):
        """execute custom sql query"""
        async with  self.pool.acquire() as connection:
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                if not sql:
                    return
                await cursor.execute(sql)

                if fetchone:
                    return await cursor.fetchone()
                else:
                    return await cursor.fetchall()

    @retry
    async def clear(self, table):
        """execute custom sql query"""
        async with  self.pool.acquire() as connection:
            async with connection.cursor() as cursor:
                if not table:
                    return
                sql = "truncate {table}".format(table=table)
                await cursor.execute(sql)

        return True

    def join_field_value(self, data, glue=', '):
        sql = comma = ''
        for key, value in data.items():
            if isinstance(value, str):
                value = pymysql.escape_string(value)
            if value is not None:
                sql= sql+"{}`{}` = '{}'".format(comma, key, value)
            else:
                sql =sql+ "{}`{}` = {}".format(comma, key, "NULL")
            #sql += "{}`{}` = '{}'".format(comma, key, value)
            comma = glue
        return sql

    async def close_pool(self):
        if self.pool:
            self.pool.close()
            await self.pool.clear()
            await self.pool.wait_closed()


@retry
async def getAmysqlobj():
    mysqlobj = Mysql()
    await mysqlobj.initpool()
    return mysqlobj



@add_run
@retry
async def insert_stock_record(mysql, result):
    symbol=result['T']
    volume=result['v']
    open_price=result['o']
    close_price=result['c']
    high=result['h']
    low=result['l']
    update_time=result['t'] 
    try:
        result=await mysql.query('SELECT close FROM us_day_ohlc WHERE updateTime in (SELECT MAX(updateTime) FROM us_day_ohlc where symbol="{}") and symbol="{}"'.format(symbol,symbol),True)
        preclose=result["close"]
        dayPercent=(float(close_price)-float(preclose))/float(preclose)*100
    except Exception as e:
        dayPercent=0
        preclose=0
    try:
        average_price=result['vw']
    except:
        average_price=0
    tradePercent=(float(close_price)-float(open_price))/float(open_price)*100
    trade=(float(close_price)+float(open_price))*volume/2
    highPercent=(high-((float(close_price)+float(open_price))/2))/((float(close_price)+float(open_price))/2)*100
    data= {"tradePercent":tradePercent,"dayPercent":dayPercent,"average":average_price,"volume":volume,"open":open_price,"close":close_price,"low":low,"symbol":symbol,"high":high,"updateTime":update_time,"preclose":preclose,"trade":trade}
    #print(data)
    await mysql.insert( "us_day_ohlc", data)

