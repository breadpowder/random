# util.startLoop()  # uncomment this line when in a notebook
import logging

from ib_insync import *

from data.ib_dataFetch import IBDataFetch


class DataService:

    def __init__(self):
        self.ib = IB()
        self.ib.connect('127.0.0.1', 7496, clientId=1)
        self.fetch = IBDataFetch(self.ib)

    ## populate data for 3 month, 15 minutes for last
    def populateData(self):
        df = self.fetch.readTicker()

        for name in df['name']:
            lastTimestamp = self.fetch.readTickerLastest(name)

            logging.info("lastTimestamp is: " + str(lastTimestamp))

            ## get date range to fetch from lasttimestamp

            contract = Forex(name)
            bars = self.ib.reqHistoricalData(
                contract, endDateTime='', durationStr='1 D',
                barSizeSetting='8 hours', whatToShow='MIDPOINT', useRTH=True)

            # convert to pandas dataframe:
            df = util.df(bars)[['date', 'open', 'high', 'low', 'close']]

            self.fetch.writeToDB(df)


dataService = DataService()

dataService.populateData()
