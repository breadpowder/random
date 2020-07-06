from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA
from talib import abstract

from algorithm.index import Bollinger
from data.DataService import DataService
import numpy as np


class BollingerCross(Strategy):

    RUN_CLOSE_NOT_PROFIT_IN_X_DAYS = False

    RUN_CLOSE_NON_TREND = False

    RUN_SKIP_NON_TRENDING= False

    RUN_BUFFER_SIGNAL = False

    n_days = 6

    ma_n0 = 12
    ma_n1 = 55
    ma_n2 = 89
    ma_n3 = 144
    ma_n4 = 169

    bull, bullIdx = False, -1
    bear, bearIdx = False, -1

    ticker = None
    profitMarginDict = {
        'USDJPY': 0.25,
        'CADJPY': 0.20,
        'USDCAD': 0.0020
    }

    safeMargin = {
        'USDJPY': 0.25,
        'CADJPY': 0.10,
        'USDCAD': 0.0025
    }


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

    def profitInTrend(self, idx):

        if not self.position or idx - self._broker._position_open_i < self.n_days: return True

        if self.position.is_long and self.close[-1] - self.position.open_price < 0:
            return False

        if self.position.is_short and self.position.open_price - self.close[-1] < 0:
            return False

        return True


    def nonTrendMarket(self, idx, n=n_days) -> bool:

        if idx < self.ma_n2: return False

        result = np.absolute(np.subtract(self.ma55[idx - n: idx], self.ma89[idx - n:idx]))

        cnt = np.count_nonzero(result < self.safeMargin[self.ticker])

        return cnt >= n and not (
                    self.data.High[-2] < self.ma89[-2] and self.data.High[-2] < self.ma55[-2] and self.data.High[-1] <
                    self.ma89[-1] and self.data.High[-1] < self.ma55[-1] or self.data.Low[-1] > self.ma55[-1] and
                    self.data.Low[-1] > self.ma89[-1] and self.data.Low[-2] > self.ma55[-2] and self.data.Low[-2] >
                    self.ma89[-2])

    def bullMarket(self, idx, check=True) -> bool:
        return ((False if check else (self.bull and idx <= self.bullIdx + self.n_days)) or crossover(self.ma12, (self.ma55 + self.ma89)/2)) \
               and self.close[-1] > self.ma12[-1] \
               and self.ma55[-1] > (self.ma89[-1] - self.safeMargin[self.ticker])

    def bearMarket(self, idx, check=True) -> bool:
        return ((False if check else (self.bear and idx <= self.bearIdx + self.n_days)) or crossover((self.ma55 + self.ma89)/2, self.ma12)) \
               and self.close[-1] < self.ma12[-1] \
               and self.ma89[-1] > (self.ma55[-1] - self.safeMargin[self.ticker])

    def next(self):

        ## price = self.data.close[-1]
        idx = self.close.shape[0]

        # if self.record:
        #     print("Position:" + str(self.position))
        #     print("Orders:" + str(self.orders))
        #     self.record = False

        ### if an order is not executed in X hours, cancel it
        # if
        # self.lastOrder = -1
        # if self.orders and not self.position and self.lastOrder>0 and idx - self.lastOrder >6:
        #       print("cancel order: ",  ','.join([str(idx)]))
        #       self.orders.cancel()
        #       self.lastOrder =-1

        ## stop trading in non trending market
        if self.nonTrendMarket(idx) and not self.position and not self.orders:
            print("Non trending market " + str(idx))
            if self.bullMarket(idx, True):
                print("Setting bull:" + str(idx))
                self.bull, self.bullIdx = True, idx

            elif self.bearMarket(idx, True):
                print("Setting bear:" + str(idx))
                self.bear, self.bearIdx = True, idx
            return

        ## bull market
        # if self.close[-1] > self.ma12 and self.ma12 > self.ma55 and self.ma55 > self.ma89 + self.safeMargin[self.ticker]:
        #     price = self.close[-1]
        #     self.buy(price = price * .9980, sl=price * .9950, tp = price * 1.01)
        #     self.lastOrder = idx

        if self.bullMarket(idx, False):
            info = ','.join((str(idx), str(self.ma12[-1]), str(self.ma55[-1]), str(self.ma89[-1]), str(self.close[-1])))
            if not self.position:
                price = self.close[-1]
                self.buy(price, sl=price * .9950, tp=price * 1.01)
                print("buy: " + info)
            elif self.position.is_long:
                self.position.close()
                print("close buy: " + info)

            self.bull = False

        ##bear market
        elif self.bearMarket(idx, False):
            info = ','.join((str(idx), str(self.ma12[-1]), str(self.ma55[-1]), str(self.ma89[-1]), str(self.close[-1])))
            if not self.position:
                price = self.close[-1]
                self.sell(price, sl=price * 1.0050, tp=price * 0.99)
                print("sell: " + info)
            elif self.position.is_short:
                self.position.close()
                print("close sell:" + info)
            self.bear = False

        ##false bull market in previous order
        ## (crossover(self.ma12, self.close) or crossover(self.ma55, self.ma12))
        if not self.profitInTrend(idx) or (self.data.Close[-1] < self.ma12[-1] and (self.data.Close[-1] < self.ma55[-1] + self.safeMargin[self.ticker] or self.data.Close[-1] < self.ma89[-1] + self.safeMargin[self.ticker])\
                and self.position.is_long):

            print("bull market trending changed, close: ", ','.join([str(idx)]))
            self.position.close()

        ##false bear market
        if not self.profitInTrend(idx) or (self.data.Close[-1] > self.ma12[-1] and (self.data.Close[-1] > self.ma55[-1] - self.safeMargin[self.ticker] or self.data.Close[-1] > self.ma89[-1] - self.safeMargin[self.ticker])\
                and self.position.is_short):
            print("bear market trending changed close: ", ','.join([str(idx)]))
            self.position.close()


dataService = DataService()

ticker = 'CADJPY'
data = dataService.prepareData(ticker, '1 hour')
bt = Backtest(data, BollingerCross,
              cash=25000, commission=0.0001)

BollingerCross.ticker = ticker

# result, heatmap = bt.optimize(n=range(5, 25, 5),
#                  ma_n1=range(10, 35, 5),
#                  ma_n2=range(30, 80, 10),
#            constraint= lambda p: p.ma_n2 > p.ma_n1,return_heatmap=True,maximize='Equity Final [$]')
#
# print(result)
#
# print("--------")
#
# print(heatmap)

### basic trading

### adding close order if not profit in X-hours

### adding close order if not in reading

### adding catch signal

print(bt.run())
## bt.plot()
