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


class OptionPositionSignal(Signal):

    @abstractmethod
    def toBuy(self, idx, data: _Data, ma12: ndarray, ma55: ndarray, ma89: ndarray, ticker: str) -> bool:
        pass

    @abstractmethod
    def toSell(self, idx, data: _Data, ma12: ndarray, ma55: ndarray, ma89: ndarray, ticker: str) -> bool:
        pass


class SkipSignal(Signal):
    @abstractmethod
    def toSkip(self, idx:int, data: _Data, ma12: ndarray, ma55: ndarray, ma89: ndarray, ticker: str, adx: ndarray) -> bool:
        pass


class CloseSignal(Signal):
    @abstractmethod
    def toClose(self, position: Position, openIdx: int, idx: int, data: _Data, ma12: ndarray, ma55: ndarray, ma89: ndarray, ticker: str) -> bool:
        pass



class BasicSignal(OptionPositionSignal):

    def toBuy(self, idx, data: _Data, ma12: ndarray, ma55: ndarray, ma89: ndarray, ticker: str) -> bool:

        return crossover(ma12, (ma55 + ma89) / 2) and data.Close[-1] > ma12[-1]  and data.Close[-2] > ma89[-2] and data.Close[-1] > ma89[-1] \
               and ma55[-1] > (ma89[-1] - self.safeMargin[ticker])

    def toSell(self, idx, data: _Data, ma12: ndarray, ma55: ndarray, ma89: ndarray, ticker: str) -> bool:
        return crossover((ma55 + ma89) / 2, ma12) and ma12[-1] > data.Close[-1]  and data.Close[-2] < ma55[-2] and data.Close[-1] < ma55[-1] \
               and ma89[-1] > ( ma55[-1] - self.safeMargin[ticker])


class ClosePositionNotTrendSignal(CloseSignal):

    def toClose(self, position: Position, openIdx: int, idx: int, data: _Data, ma12: ndarray, ma55: ndarray, ma89: ndarray,
                ticker: str) -> bool:


        if position.is_long and data.Close[-1] < ma12[-1] \
                and (data.Close[-1] < ma55[-1] + self.safeMargin[ticker] or data.Close[-1] < ma89[-1] + self.safeMargin[ticker]):
            #print("bull market trending changed, close: ", ','.join([str(idx)]))
            return True

        elif position.is_short and data.Close[-1] > ma12[-1] \
                and (data.Close[-1] > ma55[-1] - self.safeMargin[ticker] or data.Close[-1] > ma89[-1] - self.safeMargin[ticker]):
            #print("bear market trending changed close: ", ','.join([str(idx)]))
            return True





class ClosePositionNotProfitSignal(CloseSignal):

    ##self._broker._position_open_i
    def toClose(self, position: Position, openIdx: int, idx: int, data: _Data, ma12: ndarray, ma55: ndarray, ma89: ndarray,
                ticker: str) -> bool:

        if not position or idx - openIdx < self.n_days: return False

        if position.is_long and data.Close[-1] - position.open_price < 0:
            return True

        if position.is_short and position.open_price - data.Close[-1] < 0:
            return True

        return False


class SkipSignal(SkipSignal):

    def toSkip(self, idx:int, data: _Data, ma12: ndarray, ma55: ndarray, ma89: ndarray, ticker: str, adx: ndarray) -> bool:
        if idx < self.ma_n2: return False

        result = np.absolute(np.subtract(ma55[idx - self.n_days: idx], ma89[idx - self.n_days:idx]))

        cnt = np.count_nonzero(result < self.safeMargin[ticker])

        return cnt >= self.n_days and not (
                data.High[-2] < ma89[-2] and data.High[-2] < ma55[-2] and data.High[-1] <
                ma89[-1] and data.High[-1] < ma55[-1] or data.Low[-1] > ma55[-1] and
                data.Low[-1] > ma89[-1] and data.Low[-2] > ma55[-2] and data.Low[-2] >
                ma89[-2])

class ADXSkipSignal(SkipSignal):

    def toSkip(self, idx:int, data: _Data, ma12: ndarray, ma55: ndarray, ma89: ndarray, ticker: str, adx: ndarray) -> bool:

        if adx[-1] < self.ADX_CUTOFF:
            return True

        return False
