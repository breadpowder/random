from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import GOOG, SMA
from talib import abstract

from algorithm.index import Bollinger


class BollingerCross(Strategy):
    n = 10
    ma_n1 = 20
    ma_n2 = 50

    def init(self):
        Close = self.data.Close

        a_SMA = abstract.SMA

        self.upper = self.I(Bollinger, Close, self.n, "upperBand")
        self.lower = self.I(Bollinger, Close, self.n, "lowerBand")
        self.close = self.I(lambda x: x, Close, name="close")
        self.ma10 = self.I(a_SMA, Close, int(self.ma_n1), name="ma10")
        self.ma20 = self.I(SMA, Close, int(self.ma_n2), name="ma20")
        self.cnt = self.n

    def next(self):

        price = self.close[-1]

        if crossover(self.lower, self.close) and self.ma10 > self.ma20:
            if not self.position:
                self.buy(sl=price * .90)
                # print("buy: ", ','.join((str(self.cnt), str(self.data.Close[self.cnt]))))
        elif crossover(self.close, self.upper) and self.position.is_long:
            self.position.close()
            # print("sell: ", ','.join((str(self.cnt), str(self.data.Close[self.cnt]))))

        self.cnt += 1


bt = Backtest(GOOG, BollingerCross,
              cash=10000, commission=0.)

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
print(bt.run())
bt.plot()
