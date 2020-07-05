import pandas as pd


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
