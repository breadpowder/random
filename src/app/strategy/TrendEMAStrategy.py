from talib import abstract
from strategy.CustomerStrategy import CustomerStrategy

"""
Best result so far,  use 55 and 169
Basic cases:USDCAD,{'Return [%]': 0.5447233072076343, 'Buy & Hold Return [%]': 3.2415760385095402, '# Trades': 8, 'Exposure [%]:': 12.831241283124129, 'Win Rate[%]': 62.5}
Basic cases:CADJPY,{'Return [%]': 1.7629670227496534, 'Buy & Hold Return [%]': 2.2575326231176462, '# Trades': 9, 'Exposure [%]:': 13.110181311018131, 'Win Rate[%]': 66.66666666666666}
Basic cases:NZDUSD,{'Return [%]': 4.5035019083956, 'Buy & Hold Return [%]': 8.757036310271129, '# Trades': 14, 'Exposure [%]:': 9.242916860195077, 'Win Rate[%]': 85.71428571428571}
Basic cases:EURCAD,{'Return [%]': 1.8509584337672569, 'Buy & Hold Return [%]': 0.6247515939048884, '# Trades': 13, 'Exposure [%]:': 19.01441190144119, 'Win Rate[%]': 61.53846153846154}
"""


class TrendMaCross(CustomerStrategy):

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
        self.ma169 = self.I(a_SMA, self.data.Close, int(self.ma_n4), name="ma169")
        self.ma144 =  self.I(a_SMA, self.data.Close, int(self.ma_n3), name="ma144")
        self.ma338 =  self.I(a_SMA, self.data.Close, int(self.ma_n6), name="ma338")
        self.ma288 = self.I(a_SMA, self.data.Close, int(self.ma_n5), name="ma288")

        self.adx = self.I(a_ADX, self.data.High, self.data.Low, self.data.Close, int(10), name="adx-14")
        self.atr = self.I(a_ATR, self.data.High, self.data.Low, self.data.Close, int(14), name="atr-14")

    ## self.ma144 = self.I(a_SMA, Close, int(self.ma_n3), name="ma144")
    ## self.ma169 = self.I(a_SMA, Close, int(self.ma_n4), name="ma169")

    # def bullMarket(self, idx, check=True) -> bool:
    #     return ((False if check else (self.bull and idx <= self.bullIdx + self.n_days)) or crossover(self.ma12, (self.ma55 + self.ma169)/2)) \
    #            and self.close[-1] > self.ma12[-1] \
    #            and self.ma55[-1] > (self.ma169[-1] - self.safeMargin[self.ticker])
    #
    # def bearMarket(self, idx, check=True) -> bool:
    #     return ((False if check else (self.bear and idx <= self.bearIdx + self.n_days)) or crossover((self.ma55 + self.ma169)/2, self.ma12)) \
    #            and self.close[-1] < self.ma12[-1] \
    #            and self.ma169[-1] > (self.ma55[-1] - self.safeMargin[self.ticker])
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

        para = {'ma12':self.ma12, 'ma55':self.ma55, 'ma169': self.ma169, 'atr':self.atr, 'trendIdx': self.adx, 'ma144': self.ma144, 'ma338':self.ma338}
        if self.skipSignals:
            if any((s.toSkip(idx, self.data, self.ma12, self.ma55, self.ma169, self.ticker, self.adx) for s in
                    self.skipSignals)):
                return

        if all((s.toBuy(idx, self.data, self.ticker, para) for s in
                self.openPositionSignals)):
            info = ','.join((str(idx), str(self.ma12[-1]), str(self.ma55[-1]), str(self.ma169[-1]), str(self.close[-1])))
            if not self.position:
                price = self.data.Close[-1]
                if self.atrflag:
                    self.buy(price, sl=price - self.atr[-1] * self.ATR_LOSS_RATIO,
                             tp=price + self.atr[-1] * self.ATR_PROFIT_RATIO)
                else:
                    self.buy(price, sl=price * .9950, tp=price * 1.005)

                self.printIfTrace("buy: " + info)
            # elif self.position.is_long:
            #     self.position.close()
            #     self.printIfTrace("close buy: " + info)


        ##bear market
        elif all((s.toSell(idx, self.data, self.ticker, para) for s in
                  self.openPositionSignals)):
            info = ','.join((str(idx), str(self.ma12[-1]), str(self.ma55[-1]), str(self.ma169[-1]), str(self.close[-1])))
            if not self.position:
                price = self.data.Close[-1]
                if self.atrflag:

                    self.sell(price, sl=price + self.atr[-1] * self.ATR_LOSS_RATIO,
                              tp=price - self.atr[-1] * self.ATR_PROFIT_RATIO)
                else:
                    self.sell(price, sl=price * 1.0050, tp=price * 0.995)
                self.printIfTrace("sell: " + info)
            # elif self.position.is_short:
            #     self.position.close()
            #     self.printIfTrace("close sell:" + info)

        ##false bull market in previous order or false bear market
        if self.closeSignals:
            if self.position and any((s.toClose(self.position, self._broker.position_open_i, idx, self.data, self.ma12,
                                                self.ma55, self.ma169, self.ticker) for s in self.closeSignals)):
                self.printIfTrace("force close position:" + str(idx))
                self.position.close()


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
