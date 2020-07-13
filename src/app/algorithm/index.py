import collections

import pandas as pd

from algorithm.CustomerIndicators import TREND, OCCI
from data.DataService import DataService
from talib import abstract
import numpy as np


def Bollinger(series: pd.Series, n: int, name: str) -> pd.DataFrame:
    """

    :param series:
    :param n:
    :return: boolinger band
    """

    ma = pd.Series(series).rolling(n).mean()
    std = pd.Series(series).rolling(n).std()

    result = pd.DataFrame({'MA': ma, 'STD': std})

    result['upperBand'] = result['MA'] + (result['STD'] * 1.5)
    result['lowerBand'] = result['MA'] - (result['STD'] * 1.5)

    return result[name]

def calcuateATR():

    dataService = DataService()
    for ticker in ['USDCAD','NZDCAD','USDJPY','CADJPY']:
        data = dataService.prepareData(ticker, '1 hour')

        a_ATR = abstract.ATR

        result = a_ATR(data.High, data.Low, data.Close, int(6))

        print("----------------")
        print(ticker)
        print(result[-5:])


def supportLine():

    # import matplotlib as mpl
    #
    # import matplotlib.pyplot as plt
    # from random import randint
    # import numpy as np
    # from matplotlib.lines import Line2D
    #
    # np.random.seed(0)
    ys_tuple = (np.random.normal(10, 0.3, size = 10), np.random.normal(10, 0.3, size = 10))

    xs = np.arange(10)
    #
    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    # ax.add_line(Line2D(xs[-2:], ys[-2:]))
    #
    # plt.scatter(xs,ys)
    # plt.show()

    ## points
    ## "high": [(),()],
    ## "low": [(),()]
    ## "avg": [(),()]

    ## line: [slope,b]


    def crossPoint(low: float, high: float, idx: int, slope:float, b:float):

        cross = slope * idx + b

        if low < cross < high:
            return cross

        if cross > high:
            return float('inf')

        return float('-inf')

    result, line = collections.deque(), []
    low_min, idx  = float('Inf'), len(ys_tuple)

    idx = len(x)

    for (y_1, y_2) in zip(ys_1, ys_2):

        idx -=1
        if len(result) > 2: break

        low, high = y_tuple
        ## test if cross body a line a ready
        if len(result)>2:
            slope, b = line
            cross = crossPoint(low, high, idx, slope, b)
            if cross != float('inf') and cross != float('-inf'):
                result.append((low, high, idx))
            else:
                result.popleft()
                line = []

        ## build the line
        elif len(result) == 1:
            if low < low_min:
                low_min = low

                slope = (low - low_min) * 1.0 / (result[0][2] - idx)
                b = low - slope * idx

                line = [slope, b]

        else:

            result.append((low, high , idx))





















ys_tuple = np.random.normal(10, 0.3, size = (2,10))


#print(ys_tuple)



np.where(ys_tuple[0] > ys_tuple[1], ys_tuple[0], ys_tuple[1])
np.where(ys_tuple[0] > ys_tuple[1], ys_tuple[1], ys_tuple[0])







# dataService = DataService()
#for ticker in ['USDCAD']:
#     data = dataService.prepareData(ticker, '1 hour')
#
#     print(TREND(data.Close,55, 169)[:390])

## calcuateATR()

# a = np.empty(0)
# a = np.append(a, 1)
# a = np.append(a, 2)
# a = np.append(a, 4)
# a = np.append(a, 0)
# print(OCCI(a,2))

