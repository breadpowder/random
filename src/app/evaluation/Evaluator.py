from backtesting import Backtest
from data.DataService import DataService
import collections

from strategy.CustomerStrategy import CustomerStrategy
from strategy.TrendContinuationStrategy import TrendContinuation
from strategy.TrendEMAStrategy import TrendMaCross
from strategy.signal.Signal import OpenPositionSignal, ADXSkipSignal, TrendStartSignal, TrendContinuationSignal, \
    VegasSignal


class Evaluator:


    def __init__(self, strategyCls: CustomerStrategy, basicSignal: OpenPositionSignal, time: str, atrflag: bool=False, trace: bool= False):
        self.stats = collections.OrderedDict()
        self.success_cnt, self.total_cnt = 0, 0
        self.total_return = 0.0
        self.bt = None
        self.strategy = strategyCls
        self.dataService = DataService()
        self.basicSignal = basicSignal
        self.time = time
        self.strategy.atrflag= atrflag
        self.strategy.trace = trace

    def init(self, ticker: str) -> Backtest:

        data = self.dataService.prepareData(ticker, self.time)
        self.bt = Backtest(data, self.strategy,
                      cash=25000, commission=0.0001)
        self.strategy.ticker = ticker
        self.strategy.skipSignals = []
        self.strategy.closeSignals = []
        return self.bt


    def getInfo(self, setting, ticker, result):


        numOfTrades = result['# Trades']
        winRate = float(result['Win Rate [%]'])
        totalReturn = result['Return [%]']
        dic = {
            'Return [%]': totalReturn,
            'Buy & Hold Return [%]': result['Buy & Hold Return [%]'],
            '# Trades': numOfTrades,
            'Exposure [%]:': result['Exposure [%]'],
            'Win Rate[%]': winRate}
        if numOfTrades:
            self.total_cnt, self.success_cnt = self.total_cnt + numOfTrades, self.success_cnt + numOfTrades * winRate
            self.total_return += totalReturn

        if setting not in self.stats:
            self.stats[setting] = []

        self.stats[setting].append(setting + ":" + ticker + "," + dic.__str__())


    def run(self):

        for ticker in['USDCAD', 'EURCAD']: # ['USDCAD', 'EURCAD', 'NZDUSD', 'EURCAD', 'USDJPY', 'EURUSD', 'NZDCAD', 'AUDCAD', 'AUDUSD']:

            self.strategy.openPositionSignals = [basicSignal()]

            setting = "Basic cases"

            bt = self.init(ticker)
            result = bt.run()
            self.getInfo(setting, ticker, result)
            bt.plot(filename=ticker + "_basic.html")

            # setting = "Basic cases with ATR"
            # #print("Testing for basic cases:")
            # bt = init(ticker, True)
            # result = bt.run()
            # getInfo(setting,ticker,result)

            # bt.plot(filename=ticker + "_basic.html")
            #
            #
            # setting = "Add skip"
            # bt = init(ticker)
            # TrendMaCross.skipSignals = [SkipSignal()]
            # result = bt.run()
            # getInfo(setting, ticker, result)
            #
            #
            # setting = "Add ADX skip"
            # bt = self.init(ticker)
            # self.strategy.skipSignals = [ADXSkipSignal()]
            # result = bt.run()
            # self.getInfo(setting, ticker, result)
            # #
            # setting = "Two skips"
            # bt = init(ticker)
            # TrendMaCross.skipSignals = [ADXSkipSignal(), SkipSignal()]
            # result = bt.run()
            # getInfo(setting, ticker, result)
            # #
            #

            # setting = "Add close non trend"
            # bt = init(ticker)
            # TrendMaCross.closeSignals = [ClosePositionNotTrendSignal()]
            # result = bt.run()
            # getInfo(setting, ticker, result)
            #
            #
            #
            # setting ="Add Close Non-profit"
            # bt = init(ticker)
            # TrendMaCross.closeSignals = [ClosePositionNotProfitSignal()]
            # result = bt.run()
            # #bt.plot()
            # getInfo(setting, ticker, result)

            # setting = 'Two close filter'
            # bt = init(ticker)
            # TrendMaCross.closeSignals = [ClosePositionNotProfitSignal(), ClosePositionNotTrendSignal()]
            # result = bt.run()
            # #bt.plot()
            # getInfo(setting, ticker,result)

        for stat in self.stats.values():
            print("-------------------------------------")
            for item in stat:
                print(item)


        print("Total success rate: {}, total trades: {}".format(str(self.success_cnt * 1.0/self.total_cnt), str(self.total_cnt)))
        print("Per trade return: {}, total return: {}".format(str(self.total_return/self.total_cnt), str(self.total_return)))



"""
Run evaluator
"""
time = '1 hour'
atrflag =False
trace = True
strategyCls =  TrendMaCross #TrendContinuation #TrendMaCross
basicSignal = VegasSignal #TrendStartSignal() #TrendContinuationSignal()#TrendStartSignal()
eva = Evaluator(strategyCls, basicSignal, time, atrflag, trace)

eva.run()
