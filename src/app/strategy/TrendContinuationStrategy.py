import collections

from backtesting import Backtest, Strategy
from talib import abstract
from data.DataService import DataService
import numpy as np

from strategy.CustomerStrategy import CustomerStrategy
from strategy.signal.Signal import *

from algorithm.CustomerIndicators import TREND


class TrendContinuation(CustomerStrategy):


    def init(self):

        a_EMA = abstract.EMA
        a_ATR = abstract.ATR


        self.close = self.I(lambda x: x, self.data.Close, name="close")

        self.ma12 = self.I(a_EMA, self.data.Close, int(self.ma_n0), name="ma12")
        self.ma55 = self.I(a_EMA, self.data.Close, int(self.ma_n1), name="ma55")
        self.ma169 = self.I(a_EMA, self.data.Close, int(self.ma_n2), name="ma169")
        self.trendIdx  = self.I(TREND, self.data.Close, self.ma_n1, self.ma_n2, name="trendIndicator")
        self.atr = self.I(a_ATR, self.data.High, self.data.Low, self.data.Close, int(14), name ="atr-14")



    @classmethod
    def printIfTrace(self, info):
        if self.trace:
            print(info)

    def next(self):

        idx = self.close.shape[0]

        if self.skipSignals:
            if any((s.toSkip( idx, self.data, self.ma12, self.ma55, self.ma169, self.ticker, self.adx) for s in self.skipSignals)):
                return

        if all((s.toBuy(idx, self.data, self.ma12, self.ma55, self.ma169, self.ticker, self.trendIdx, self.atr) for s in self.openPositionSignals)):
            info = ','.join((str(idx), str(self.ma12[-1]), str(self.ma55[-1]), str(self.ma169[-1]), str(self.close[-1])))
            if not self.position:
                price = self.data.Close[-1]
                if self.atrflag:
                    #price -= self.ATR_LOSS_RATIO * self.atr[-1]

                    self.buy(price, sl=price - 2 * self.atr[-1], tp=price + 2 * self.atr[-1])
                else:
                    self.buy(price, sl=price * .9950, tp=price * 1.005)

                self.printIfTrace("buy: " + info)

        ##bear market
        elif all((s.toSell(idx, self.data, self.ma12, self.ma55, self.ma169, self.ticker, self.trendIdx,self.atr) for s in self.openPositionSignals)):
            info = ','.join((str(idx), str(self.ma12[-1]), str(self.ma55[-1]), str(self.ma169[-1]), str(self.close[-1])))
            if not self.position:
                price = self.data.Close[-1]
                if self.atrflag:
                    #price += self.ATR_LOSS_RATIO * self.atr[-1]
                    self.sell(price,  sl=price + 2 * self.atr[-1], tp=price - 2 * self.atr[-1])
                else:
                    self.sell(price, sl=price * 1.0050, tp=price * 0.995)
                self.printIfTrace("sell: " + info)


        ##false bull market in previous order or false bear market
        if self.closeSignals:
            if self.position and any((s.toClose(self.position, self._broker.position_open_i, idx, self.data, self.ma12, self.ma55, self.ma169, self.ticker) for s in self.closeSignals)):
                self.printIfTrace("force close position:" + str(idx))
                self.position.close()

