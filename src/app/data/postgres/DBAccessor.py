from datetime import datetime
from functools import lru_cache

import pandas as pd
from sqlalchemy import create_engine


class DBAccessor:
    DATA_TABLE = 'Tickers_Data'
    TICKER_TABLE = 'Tickers'

    def __init__(self):
        self.engine = create_engine('postgresql://docker:docker@localhost:5432/docker')

    @lru_cache(None)
    def readTicker(self, table_name: str = TICKER_TABLE) -> pd.DataFrame:
        conn = self.engine.connect()
        df = pd.read_sql_table(table_name, conn)
        return df

    ### No volume now since it is not avaiable
    def readTickerData(self, ticker: str) -> pd.DataFrame:
        conn = self.engine.connect()
        ticker_id = self._getTickerId(ticker)
        sql = "select time, open, high, low, close from \"{}\" where id={} order by time".format(DBAccessor.DATA_TABLE,
                                                                                                 ticker_id)
        return pd.read_sql(sql, conn, index_col='time')

    def readTickerLastest(self, ticker: str) -> datetime:
        conn = self.engine.connect()
        ticker_id = self._getTickerId(ticker)

        sql = "SELECT time FROM \"{}\" WHERE id={} order by time desc limit 1".format(DBAccessor.DATA_TABLE, ticker_id)
        result = pd.read_sql(sql, conn)
        return None if result.empty else result.iloc[0]['time']

    def writeToDB(self, ticker: str, df: pd.DataFrame):
        ### 'date','open','high','low','close' to 'id', 'time','open','high','low','close'

        conn = self.engine.connect()

        ticker_id = self._getTickerId(ticker)

        df.rename(columns={'date': 'time'}, inplace=True)
        df['id'] = ticker_id

        df.to_sql(DBAccessor.DATA_TABLE, index=False, con=conn, if_exists='append')

    def _getTickerId(self, ticker: str) -> int:
        df = self.readTicker()
        tmp_df = df[df['name'] == ticker]
        return tmp_df.iloc[0]['id']
