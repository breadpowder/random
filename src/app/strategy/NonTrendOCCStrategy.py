from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from talib import abstract

from algorithm.index import Bollinger
from data.DataService import DataService
import numpy as np

from strategy.CustomerStrategy import CustomerStrategy
from strategy.signal.Signal import *
from algorithm.CustomerIndicators import OCCI, OCCIHL


class NonTrendOCCStrategy(CustomerStrategy):

    ATR_RATIO = 1
    PROFIT_RATIO = 0.8
    LOW = -0.05
    HIGH = 1.05


    def init(self):

        a_ADX = abstract.ADX
        a_ATR = abstract.ATR
        a_EMA = abstract.EMA

        self.close = self.I(lambda x: x, self.data.Close, name="close")
        self.atr = self.I(a_ATR, self.data.High, self.data.Low, self.data.Close, int(14), name ="atr")
        self.ma12 = self.I(a_EMA, self.data.Close, int(self.ma_n0), name="ma12")
        #self.occi = self.I(OCCI, self.data.Close, int(3), name='occ')

        self.occi = self.I(OCCIHL, self.data.High, self.data.Low, self.data.Close, int(3), name='occ')

    @classmethod
    def printIfTrace(self, info):
        if self.trace:
            print(info)

    def next(self):

        idx = self.close.shape[0]

        last_atr, last_close, last_open = self.atr[-1], self.data.Close[-1],self.data.Open[-1]
        #self.printIfTrace(str(last_adx) + "," + str(last_atr))

        # if (self.occi[-1] > self.HIGH  or self.occi[-1] < self.LOW) and not self.position and not self.orders:
        #     self.printIfTrace("return at: " + str(idx))
        #     return
        #
        # if (self.occi[-1] > self.HIGH  or self.occi[-1] < self.LOW) and (self.orders or self.position):
        #     self.printIfTrace("return at: " + str(idx))
        #     if not self.position and self.orders:
        #         self.orders.cancel()
        #
        #     # if self.position:
        #     #     self.position.close()
        #     return
        #lastThree = self.occi[-3:] > self.LOW and self.occi[-3:] < self.HIGH
        #print(lastThree)
        #if  lastThree.all():
        currentAtr = self.data.High[-1] - self.data.Low[-1]
        upper = self.data.High[-1] - self.data.Close[-1] if currentAtr > 0 else self.data.High[-1] - self.data.Open[-1]
        lower = self.data.Open[-1] - self.data.Low[-1] if currentAtr > 0 else self.data.Close[-1] - self.data.Low[-1]
        bar = abs(self.data.Close[-1] - self.data.Open[-1])

        if self.LOW < self.occi[-1] < self.HIGH and self.LOW < self.occi[-2] < self.HIGH and self.LOW < self.occi[-3] < self.HIGH:
            ###
            if  currentAtr > self.atr[-1]  and lower > bar * 1.0 and lower > upper and not self.position:
                price = self.data.Close[-1] #self.data.Low[-1] - self.ATR_RATIO * last_atr
                self.buy(price , sl =  price - self.PROFIT_RATIO * last_atr, tp= price + self.PROFIT_RATIO * last_atr)
                self.printIfTrace("Buy at index:" + str(idx))

            elif currentAtr > self.atr[-1]  and upper > bar * 1.0 and upper > lower  and not self.position:
                 price = self.data.Close[-1] #self.data.High[-1] + self.ATR_RATIO * last_atr
                 self.printIfTrace("Sell at index:" + str(idx))
                 self.sell(price, sl =  price + self.PROFIT_RATIO * last_atr, tp= price - self.PROFIT_RATIO  * last_atr)


stats = []

for ticker in ['EURUSD']: #['USDCAD','USDJPY','CADJPY','EURUSD','EURCAD','NZDUSD','NZDCAD','AUDCAD','AUDUSD']:

    dataService = DataService()
    data = dataService.prepareData(ticker, '1 hour')

    def init(ticker:str) -> Backtest:
        bt = Backtest(data, NonTrendOCCStrategy,
                      cash=25000, commission=0.0001)
        NonTrendOCCStrategy.ticker = ticker
        NonTrendOCCStrategy.skipSignals = []
        NonTrendOCCStrategy.close = []
        NonTrendOCCStrategy.trace = True
        return bt

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
    bt.plot(filename=ticker + "non_trend_basic.html")

    # result, heatmap = bt.optimize(ADX_CUTOFF=[20, 25, 30, 45],
    #                      ATR_RATIO =[1.0,1.2,1.5, 1.8,2.0],
    #                      PROFIT_RATIO= [1.0,1.2,1.5,1.8,2.0],
    #                      return_heatmap=True,maximize='Equity Final [$]')
    #
    # print(result)
    # print(heatmap)


print("-------------------------------------")
for stat in stats:
     print(stat)





#
# self.printIfTrace(result)
#
# self.printIfTrace("--------")
#
# self.printIfTrace(heatmap)



