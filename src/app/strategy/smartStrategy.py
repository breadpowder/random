from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA
from talib import abstract

from algorithm.index import Bollinger
from data.DataService import DataService
import numpy as np

from strategy.signal.Signal import *


class BollingerCross(Strategy):
    n_days = 6

    ma_n0 = 12
    ma_n1 = 55
    ma_n2 = 89
    ma_n3 = 144
    ma_n4 = 169

    # bull, bullIdx = False, -1
    # bear, bearIdx = False, -1

    openPositionSignals = [BasicSignal()]
    skipSignals = []
    closeSignals = []

    trace = True

    def init(self):

        a_SMA = abstract.EMA

        # Close = self.data.Close
        # self.upper = self.I(Bollinger, Close, self.n, "upperBand")
        # self.lower = self.I(Bollinger, Close, self.n, "lowerBand")
        self.close = self.I(lambda x: x, self.data.Close, name="close")

        self.ma12 = self.I(a_SMA, self.data.Close, int(self.ma_n0), name="ma12")
        self.ma55 = self.I(a_SMA, self.data.Close, int(self.ma_n1), name="ma55")
        self.ma89 = self.I(a_SMA, self.data.Close, int(self.ma_n2), name="ma89")

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
            if any((s.toSkip( idx, self.data, self.ma12, self.ma55, self.ma89, self.ticker) for s in self.skipSignals)):
                return

        if all((s.toBuy(idx, self.data, self.ma12, self.ma55, self.ma89, self.ticker) for s in self.openPositionSignals)):
            info = ','.join((str(idx), str(self.ma12[-1]), str(self.ma55[-1]), str(self.ma89[-1]), str(self.close[-1])))
            if not self.position:
                price = self.close[-1]
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
                price = self.close[-1]
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

for ticker in ['USDCAD','CADJPY', 'USDJPY']:

    dataService = DataService()
    data = dataService.prepareData(ticker, '1 hour')

    def init(ticker:str) -> Backtest:
        bt = Backtest(data, BollingerCross,
                      cash=25000, commission=0.0001)
        BollingerCross.ticker = ticker
        BollingerCross.skipSignals = []
        BollingerCross.close = []
        BollingerCross.trace = False
        return bt

    stats = []

    def getInfo(result):
        dic = {
            'Return [%]' : result['Return [%]'],
            'Buy & Hold Return [%]': result['Buy & Hold Return [%]'],
            '# Trades': result['# Trades'],
            'Exposure [%]:' : result['Exposure [%]'],
            'Win Rate[%]': result['Win Rate [%]']}
        stats.append(dic)


    print("Testing for basic cases:")
    print("------------------------------------")
    bt = init(ticker)
    result = bt.run()
    getInfo(result)
    bt.plot(filename=ticker + "_basic.html")

    print("Testing for add skip:")
    print("------------------------------------")
    bt = init(ticker)
    BollingerCross.skipSignals = [SkipSignal()]
    result = bt.run()
    getInfo(result)


    print("Testing for add close")
    print("------------------------------------")
    bt = init(ticker)
    BollingerCross.closeSignals = [ClosePositionNotTrendSignal()]
    result = bt.run()
    getInfo(result)


    print("Testing for add non-proft:")
    print("------------------------------------")
    bt = init(ticker)
    BollingerCross.closeSignals = [ClosePositionNotProfitSignal()]
    result = bt.run()
    #bt.plot()
    getInfo(result)

    print("Testing for add two close filter:")
    print("------------------------------------")
    bt = init(ticker)
    BollingerCross.closeSignals = [ClosePositionNotProfitSignal(), ClosePositionNotTrendSignal()]
    result = bt.run()
    #bt.plot()
    getInfo(result)

    print("-------------------------------------")
    for stat in stats:
        print(stat)


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



