from talib import abstract
import numpy as np
import pandas as pd


ema = abstract.EMA
def TREND(data: np.ndarray, n1: int, n2: int):
    data = np.subtract(ema(data, n1),ema(data,n2))
    return ema(data, 10)

def OCCI(close: np.ndarray, n: int):

    close = pd.Series(close)
    max = pd.Series(close).rolling(n).max()
    min = pd.Series(close).rolling(n).min()
    result = close.subtract(min.shift(1)).divide(max.shift(1).subtract(min.shift(1)))

    return result


def OCCIHL(high: np.ndarray, low: np.ndarray, close: np.ndarray, n: int):

    max = pd.Series(high).rolling(n).max()
    min = pd.Series(low).rolling(n).min()
    result = pd.Series(close).subtract(min.shift(1)).divide(max.shift(1).subtract(min.shift(1)))

    return result













