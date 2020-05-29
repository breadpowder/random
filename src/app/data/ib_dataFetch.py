from ib_insync import *
## from pandas import DataFrame
import pandas as pd
from sqlalchemy import create_engine


class IBDataFetch:

    def __init__(self, ib: IB):
        self.ib = ib
        self.engine = create_engine('postgresql://docker:docker@localhost:5432/docker')


    def fetchData(self, contract:Contract, durationStr='30 D', endDateTime ='', barSizeSetting='1 day', whatToShow='close', useRTH = True):
        bars = self.ib.reqHistoricalData(
            contract, endDateTime=endDateTime, durationStr=durationStr,
            barSizeSetting=barSizeSetting, whatToShow = whatToShow, useRTH=useRTH)
        df = util.df(bars)
        print(df)


    def writeToDB(self, df: pd.DataFrame):
        pass


    def readTicker(self, table_name: str):
        conn = self.engine.connect()
        df = pd.read_sql_table(table_name, conn)
        print(df)



