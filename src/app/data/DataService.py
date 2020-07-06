# util.startLoop()  # uncomment this line when in a notebook
import logging
from ib_insync import *
from data.postgres.DBAccessor import DBAccessor
import pandas as pd
from backtesting.lib import resample_apply



class DataService:
    logging.getLogger().setLevel(logging.INFO)

    def __init__(self):
        pd.set_option('display.max_rows', 3000)
        self.ib = IB()
        self.fetch = DBAccessor()

    ## populate data for 3 month, 10 minutes for last
    def populateData(self):

        ## lazy connection
        self.ib.connect('127.0.0.1', 7496, clientId=1)
        df = self.fetch.readTicker()

        for ticker_name in df['name']:
            lastTimestamp = self.fetch.readTickerLastest(ticker_name)
            logging.info("lastTimestamp is: " + str(lastTimestamp))

            ## get data from up now, max range 3 months, convert to pandas dataframe:
            contract = Forex(ticker_name)
            bars = self.ib.reqHistoricalData(
                contract, endDateTime='', durationStr='3 M',
                barSizeSetting='10 mins', whatToShow='MIDPOINT', useRTH=True)
            df = util.df(bars)[['date', 'open', 'high', 'low', 'close']]

            if lastTimestamp:
                df = df.loc[df['date'] > lastTimestamp]

            self.fetch.writeToDB(ticker_name, df)


    ### convert and resample data to OHLC
    def prepareData(self, ticker: str, resampleFreq='10 mins') -> pd.DataFrame:

            resample_dict = {'10 mins': '10Min', '30 mins': '30Min', '1 hour': 'H', '2 hour':'2H', '4 hour':'4H', '8 hour':'8H'}
            assert resampleFreq in resample_dict.keys()


            df = self.fetch.readTickerData(ticker)

            df.rename(columns={'open': 'Open', 'high': 'High', 'low':'Low', 'close': 'Close'}, inplace=True)
            ohlc_dict = {
                'Open':'first',
                'High':'max',
                'Low':'min',
                'Close': 'last'
            }


            result = df.resample(resample_dict[resampleFreq]).agg(ohlc_dict).dropna()
            logging.info("Total number of points: " + str(result.shape[0]))

            return result



dataService = DataService()
dataService.populateData()
