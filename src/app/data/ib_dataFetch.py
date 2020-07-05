from datetime import datetime
from functools import lru_cache

## from pandas import DataFrame
import pandas as pd
from ib_insync import *
from sqlalchemy import create_engine


class IBDataFetch:

    def __init__(self, ib: IB):
        self.ib = ib
        self.engine = create_engine('postgresql://docker:docker@localhost:5432/docker')
        self.cache = None

    def fetchData(self, contract: Contract, durationStr='30 D', endDateTime='', barSizeSetting='1 day',
                  whatToShow='close', useRTH=True):
        bars = self.ib.reqHistoricalData(
            contract, endDateTime=endDateTime, durationStr=durationStr,
            barSizeSetting=barSizeSetting, whatToShow=whatToShow, useRTH=useRTH)
        df = util.df(bars)
        return df

    @lru_cache(None)
    def readTicker(self, table_name: str = "Tickers") -> pd.DataFrame:
        conn = self.engine.connect()
        df = pd.read_sql_table(table_name, conn)
        return df

    def readTickerData(self, ticker: str) -> pd.DataFrame:
        conn = self.engine.connect()
        ticker_id = self.readTicker().query('name=={}'.format(ticker)).iloc[0]['ticker']
        sql = "select * from Tickers_Data where id={} order by time".format(ticker_id)
        return pd.read_sql(sql, conn)

    def readTickerLastest(self, ticker: str) -> datetime:
        conn = self.engine.connect()
        df = self.readTicker()
        tmp_df = df[df['name'] == ticker]
        ticker_id = tmp_df.iloc[0]['id']

        sql = "SELECT time FROM \"Tickers_Data\" WHERE id={} order by time desc limit 1".format(ticker_id)
        result = pd.read_sql(sql, conn)
        return None if result.empty else result.iloc[0]['time']

    def writeToDB(self, df: pd.DataFrame):
        ### 'date','open','high','low','close' to 'id', 'time','open','high','low','close'

        conn = self.engine.connect()
