from abc import abstractmethod

from backtesting._util import _Data
from numpy import ndarray
from backtesting.lib import crossover
from backtesting import Position
import numpy as np


class Signal:
    n_days = 6

    ma_n0 = 12
    ma_n1 = 55
    ma_n2 = 89
    ma_n3 = 144
    ma_n4 = 169

    ADX_CUTOFF = 20

    ATR_MARGIN = 0.5

    safeMargin2 = {
        'USDJPY': 0.0,
        'CADJPY': 0.10,
        'USDCAD': 0.0020,
        'EURUSD':0.0020,
        'EURCAD':0.0025,
        'NZDUSD':0.0010,
        'NZDCAD':0.0010,
        'AUDCAD':0.0005,
        'AUDUSD':0.0010
    }

    safeMargin = {
        'USDJPY': 0.0,
        'CADJPY': 0.10,
        'USDCAD': 0.0020,
        'EURUSD':0.0020,
        'EURCAD':0.0020,
        'NZDUSD':0.0010,
        'NZDCAD':0.0006,
        'AUDCAD':0.0005,
        'AUDUSD':0.0010
    }


class OpenPositionSignal(Signal):

    @abstractmethod
    ## ma12: ndarray, ma55: ndarray, ma169: ndarray, trendIdx:ndarray
    def toBuy(self, idx, data: _Data, ticker: str, kwargs) -> bool:
        pass

    @abstractmethod
    def toSell(self, idx, data: _Data, ticker: str, kwargs: dict) -> bool:
        pass


class SkipSignal(Signal):
    @abstractmethod
    def toSkip(self, idx:int, data: _Data, ma12: ndarray, ma55: ndarray, ma169: ndarray, ticker: str, adx: ndarray) -> bool:
        pass


class CloseSignal(Signal):
    @abstractmethod
    def toClose(self, position: Position, openIdx: int, idx: int, data: _Data, ma12: ndarray, ma55: ndarray, ma169: ndarray, ticker: str) -> bool:
        pass



class TrendStartSignal(OpenPositionSignal):

    def toBuy(self, idx,  data: _Data, ticker: str, kwargs: dict) -> bool:
        ma12 = kwargs['ma12']
        ma55 = kwargs['ma55']
        ma169 = kwargs['ma169']
        trendIdx = kwargs['trendIdx']
        atr = kwargs['atr']

        return crossover(ma12, (ma55 + ma169)/2) \
               and data.Close[-1] > ma12[-1] \
               and ma55[-1] > (ma169[-1] - abs(trendIdx[-1] * 0.5)) \
                and data.Close[-2] > ma169[-2] \
                and data.Close[-1] > ma169[-1]

    def toSell(self, idx, data: _Data, ticker: str, kwargs: dict) -> bool:
        ma12 = kwargs['ma12']
        ma55 = kwargs['ma55']
        ma169 = kwargs['ma169']
        trendIdx = kwargs['trendIdx']
        atr = kwargs['atr']

        return crossover((ma55 + ma169) / 2, ma12) \
                   and data.Close[-1] < ma12[-1]  \
                   and data.Close[-2] < ma55[-2]\
                   and data.Close[-1] < ma55[-1] \
                   and ma55[-1] < (ma169[-1] + abs(trendIdx[-1] * 0.5)) \


class  VegasSignal(OpenPositionSignal):


    def __init__(self):
        self.lastCrossUp, self.lastCrossIdx = 0, -1

    def toBuy(self, idx,  data: _Data, ticker: str, kwargs: dict) -> bool:


        ma12 = kwargs['ma12']
        ma144 = kwargs['ma144']
        ma338 = kwargs['ma338']
        ma55 =kwargs['ma55']

        if crossover(ma12, ma338):
            print("Setting cross up at idx {} buy ".format(idx))
            self.lastCrossUp = 1
            self.lastCrossIdx = idx

        if crossover(ma338, ma12):
            print("Setting cross down at idx {} buy ".format(idx))
            self.lastCrossUp = -1
            self.lastCrossIdx = idx


        trendIdx = kwargs['trendIdx']

        if self.lastCrossUp ==1  and idx - self.lastCrossIdx < 48 and crossover(ma12, ma144):
            self.lastCrossUp = 0
            return True

        return False
        #and ma55[-1] > ma144[-1]
               #and ma144[-1] > ma338[-1]


    def toSell(self, idx, data: _Data, ticker: str, kwargs: dict) -> bool:

        ma12 = kwargs['ma12']
        ma144 = kwargs['ma144']
        ma338 = kwargs['ma338']
        ma55 =kwargs['ma55']


        trendIdx = kwargs['trendIdx']
        if self.lastCrossUp == -1 and idx - self.lastCrossIdx < 48 and crossover(ma144, ma12):
            self.lastCrossUp =0
            return  True
        return False
               #and ma55[-1] < ma144[-1]
               #and ma144[-1] < ma338[-1]


class TrendContinuationSignal(OpenPositionSignal):

    def toBuy(self, idx, data: _Data, ticker: str, ** kwargs) -> bool:

        ma12 = kwargs['ma12']
        ma55 = kwargs['ma55']
        ma169 = kwargs['ma169']
        trendIdx = kwargs['trendIdx']
        atr =kwargs['atr']
        ### if strong trend exists and cross over ma169
        return  trendIdx[-1] > atr[-1] * 1.5 and crossover(ma12,data.Close - atr[-1] * 0.5) and ma55[-1] > ma169[-1] #and ma55[-1] > ma169[-1] + 0.0060 and np.diff(trendIdx[-5:]).mean() > np.diff(trendIdx[-10:-5]).mean()


    def toSell(self, idx, data: _Data, ticker:str, ** kwargs) -> bool:
        ma12 = kwargs['ma12']
        ma55 = kwargs['ma55']
        ma169 = kwargs['ma169']
        trendIdx = kwargs['trendIdx']
        atr =kwargs['atr']
        return  trendIdx[-1] < - atr[-1] * 1.5 and crossover(data.Close + atr[-1] * 0.5, ma12) and ma55[-1] < ma169[-1] #and ma169[-1] < ma55[-1] + 0.0060 and and np.diff(trendIdx[-5:]).mean() < np.diff(trendIdx[-10:-5]).mean()


class ClosePositionNotTrendSignal(CloseSignal):

    def toClose(self, position: Position, openIdx: int, idx: int, data: _Data, ma12: ndarray, ma55: ndarray, ma169: ndarray,
                ticker: str) -> bool:


        if position.is_long and data.Close[-1] < ma12[-1] \
                and (data.Close[-1] < ma55[-1] + self.safeMargin[ticker] or data.Close[-1] < ma169[-1] + self.safeMargin[ticker]):
            #print("bull market trending changed, close: ", ','.join([str(idx)]))
            return True

        elif position.is_short and data.Close[-1] > ma12[-1] \
                and (data.Close[-1] > ma55[-1] - self.safeMargin[ticker] or data.Close[-1] > ma169[-1] - self.safeMargin[ticker]):
            #print("bear market trending changed close: ", ','.join([str(idx)]))
            return True





class ClosePositionNotProfitSignal(CloseSignal):

    ##self._broker._position_open_i
    def toClose(self, position: Position, openIdx: int, idx: int, data: _Data, ma12: ndarray, ma55: ndarray, ma169: ndarray,
                ticker: str) -> bool:

        if not position or idx - openIdx < self.n_days: return False

        if position.is_long and data.Close[-1] - position.open_price < 0:
            return True

        if position.is_short and position.open_price - data.Close[-1] < 0:
            return True

        return False


class SkipSignal(SkipSignal):

    def toSkip(self, idx:int, data: _Data, ma12: ndarray, ma55: ndarray, ma169: ndarray, ticker: str, adx: ndarray) -> bool:
        if idx < self.ma_n2: return False

        result = np.absolute(np.subtract(ma55[idx - self.n_days: idx], ma169[idx - self.n_days:idx]))

        cnt = np.count_nonzero(result < self.safeMargin[ticker])

        return cnt >= self.n_days and not (
                data.High[-2] < ma169[-2] and data.High[-2] < ma55[-2] and data.High[-1] <
                ma169[-1] and data.High[-1] < ma55[-1] or data.Low[-1] > ma55[-1] and
                data.Low[-1] > ma169[-1] and data.Low[-2] > ma55[-2] and data.Low[-2] >
                ma169[-2])

class ADXSkipSignal(SkipSignal):

    def toSkip(self, idx:int, data: _Data, ma12: ndarray, ma55: ndarray, ma169: ndarray, ticker: str, adx: ndarray) -> bool:

        if adx[-1] < self.ADX_CUTOFF:
            return True

        return False
