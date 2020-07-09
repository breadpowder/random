import collections

from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA
from talib import abstract

from algorithm.index import Bollinger
from data.DataService import DataService
import numpy as np

from strategy.signal.Signal import *


"""
Best result so far,  use 55 and 169
Basic cases:USDCAD,{'Return [%]': 0.5447233072076343, 'Buy & Hold Return [%]': 3.2415760385095402, '# Trades': 8, 'Exposure [%]:': 12.831241283124129, 'Win Rate[%]': 62.5}
Basic cases:CADJPY,{'Return [%]': 1.7629670227496534, 'Buy & Hold Return [%]': 2.2575326231176462, '# Trades': 9, 'Exposure [%]:': 13.110181311018131, 'Win Rate[%]': 66.66666666666666}
Basic cases:NZDUSD,{'Return [%]': 4.5035019083956, 'Buy & Hold Return [%]': 8.757036310271129, '# Trades': 14, 'Exposure [%]:': 9.242916860195077, 'Win Rate[%]': 85.71428571428571}
Basic cases:EURCAD,{'Return [%]': 1.8509584337672569, 'Buy & Hold Return [%]': 0.6247515939048884, '# Trades': 13, 'Exposure [%]:': 19.01441190144119, 'Win Rate[%]': 61.53846153846154}
"""


class TrendMaCross(Strategy):
    n_days = 6

    ma_n0 = 12
    ma_n1 = 55
    ma_n2 = 89
    ma_n3 = 144
    ma_n4 = 169


    ## ATR DOES NOT WORK
    atrflag = False

    #ATR_PROFIT_RATIO = 5.0
    #ATR_LOSS_RATIO = 2.0

    # bull, bullIdx = False, -1
    # bear, bearIdx = False, -1

    openPositionSignals = [BasicSignal()]
    skipSignals = []
    closeSignals = []

    trace = True
    ticker = None

    def init(self):

        a_SMA = abstract.EMA
        a_ADX = abstract.ADX
        a_ATR = abstract.ATR

        # Close = self.data.Close
        # self.upper = self.I(Bollinger, Close, self.n, "upperBand")
        # self.lower = self.I(Bollinger, Close, self.n, "lowerBand")


        self.close = self.I(lambda x: x, self.data.Close, name="close")

        self.ma12 = self.I(a_SMA, self.data.Close, int(self.ma_n0), name="ma12")
        self.ma55 = self.I(a_SMA, self.data.Close, int(self.ma_n2), name="ma55")
        self.ma89 = self.I(a_SMA, self.data.Close, int(self.ma_n4), name="ma169")
        self.adx = self.I(a_ADX, self.data.High, self.data.Low, self.data.Close, int(14), name="adx-14")
        self.atr = self.I(a_ATR, self.data.High, self.data.Low, self.data.Close, int(14), name ="atr-14")


## self.ma144 = self.I(a_SMA, Close, int(self.ma_n3), name="ma144")
        ## self.ma169 = self.I(a_SMA, Close, int(self.ma_n4), name="ma169")

    # def bullMarket(self, idx, check=True) -> bool:
    #     return ((False if check else (self.bull and idx <= self.bullIdx + self.n_days)) or crossover(self.ma12, (self.ma55 + self.ma89)/2)) \
    #            and self.close[-1] > self.ma12[-1] \
    #            and self.ma55[-1] > (self.ma89[-1] - self.safeMargin[self.ticker])
    #
    # def bearMarket(self, idx, check=True) -> bool:
    #     return ((False if check else (self.bear and idx <= self.bearIdx + self.n_days)) or crossover((self.ma55 + self.ma89)/2, self.ma12)) \
    #            and self.close[-1] < self.ma12[-1] \
    #            and self.ma89[-1] > (self.ma55[-1] - self.safeMargin[self.ticker])
    @classmethod
    def printIfTrace(self, info):
        if self.trace:
            print(info)

    def next(self):

        idx = self.close.shape[0]

        ### if an order is not executed in X hours, cancel it
        # if
        # self.lastOrder = -1
        # if self.orders and not self.position and self.lastOrder>0 and idx - self.lastOrder >6:
        #       self.printIfTrace("cancel order: ",  ','.join([str(idx)]))
        #       self.orders.cancel()
        #       self.lastOrder =-1

        if self.skipSignals:
            if any((s.toSkip( idx, self.data, self.ma12, self.ma55, self.ma89, self.ticker, self.adx) for s in self.skipSignals)):
                return

        if all((s.toBuy(idx, self.data, self.ma12, self.ma55, self.ma89, self.ticker) for s in self.openPositionSignals)):
            info = ','.join((str(idx), str(self.ma12[-1]), str(self.ma55[-1]), str(self.ma89[-1]), str(self.close[-1])))
            if not self.position:
                price = self.data.Close[-1]
                if self.atrflag:
                    price = self.data.Low[-1]
                    self.buy(price, sl=price - self.atr[-1] * self.ATR_LOSS_RATIO, tp=price + self.atr[-1] * self.ATR_PROFIT_RATIO)
                else:
                    self.buy(price, sl=price * .9950, tp=price * 1.005)

                self.printIfTrace("buy: " + info)
            elif self.position.is_long:
                self.position.close()
                self.printIfTrace("close buy: " + info)

            self.bull = False

        ##bear market
        elif all((s.toSell(idx, self.data, self.ma12, self.ma55, self.ma89, self.ticker) for s in self.openPositionSignals)):
            info = ','.join((str(idx), str(self.ma12[-1]), str(self.ma55[-1]), str(self.ma89[-1]), str(self.close[-1])))
            if not self.position:
                price = self.data.Close[-1]
                if self.atrflag:
                    price = self.data.High[-1]
                    self.sell(price, sl=price + self.atr[-1] * self.ATR_LOSS_RATIO, tp=price - price * self.ATR_PROFIT_RATIO)
                else:
                    self.sell(price, sl=price * 1.0050, tp=price * 0.995)
                self.printIfTrace("sell: " + info)
            elif self.position.is_short:
                self.position.close()
                self.printIfTrace("close sell:" + info)
            self.bear = False

        ##false bull market in previous order or false bear market
        if self.closeSignals:
            if self.position and any((s.toClose(self.position, self._broker.position_open_i, idx, self.data, self.ma12, self.ma55, self.ma89, self.ticker) for s in self.closeSignals)):
                self.printIfTrace("force close position:" + str(idx))
                self.position.close()

stats = collections.OrderedDict()

for ticker in ['NZDUSD', 'CADJPY']: #['USDCAD','CADJPY','NZDUSD', 'EURCAD','USDJPY','EURUSD','NZDCAD','AUDCAD','AUDUSD']:

    dataService = DataService()
    data = dataService.prepareData(ticker, '1 hour')

    def init(ticker:str, atrflag = False) -> Backtest:
        bt = Backtest(data, TrendMaCross,
                      cash=25000, commission=0.0001)
        TrendMaCross.ticker = ticker
        TrendMaCross.skipSignals = []
        TrendMaCross.trace = False
        TrendMaCross.atrflag = atrflag
        TrendMaCross.closeSignals = []
        return bt


    def getInfo(setting, ticker, result):
        dic = {
            'Return [%]' : result['Return [%]'],
            'Buy & Hold Return [%]': result['Buy & Hold Return [%]'],
            '# Trades': result['# Trades'],
            'Exposure [%]:' : result['Exposure [%]'],
            'Win Rate[%]': result['Win Rate [%]']}

        if setting not in stats:
            stats[setting] = []

        stats[setting].append(setting +":" + ticker + "," + dic.__str__())

    setting = "Basic cases"
    #print("Testing for basic cases:")
    bt = init(ticker)
    result = bt.run()
    getInfo(setting,ticker,result)
    bt.plot(filename=ticker + "_basic_bad.html")

    # setting = "Basic cases with ATR"
    # #print("Testing for basic cases:")
    # bt = init(ticker, True)
    # result = bt.run()
    # getInfo(setting,ticker,result)

    #bt.plot(filename=ticker + "_basic.html")
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
    # bt = init(ticker)
    # TrendMaCross.skipSignals = [ADXSkipSignal()]
    # result = bt.run()
    # getInfo(setting, ticker, result)
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

for stat in stats.values():
    print("-------------------------------------")
    for item in stat:
        print(item)


# result, heatmap = bt.optimize(n=range(5, 25, 5),
#                  ma_n1=range(10, 35, 5),
#                  ma_n2=range(30, 80, 10),
#            constraint= lambda p: p.ma_n2 > p.ma_n1,return_heatmap=True,maximize='Equity Final [$]')
#
# self.printIfTrace(result)
#
# self.printIfTrace("--------")
#
# self.printIfTrace(heatmap)



