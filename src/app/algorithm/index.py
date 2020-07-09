import pandas as pd

from data.DataService import DataService
from talib import abstract


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


## calcuateATR()

