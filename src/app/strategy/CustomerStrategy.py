from backtesting import Backtest, Strategy

class CustomerStrategy(Strategy):
    n_days = 6

    ma_n0 = 12
    ma_n1 = 55
    ma_n2 = 89
    ma_n3 = 144
    ma_n4 = 169
    ma_n5 = 288
    ma_n6 = 338


    ## ATR DOES NOT WORK
    atrflag = False

    ATR_PROFIT_RATIO = 3
    ATR_LOSS_RATIO = 3

    ADX_CUTOFF = 25


    openPositionSignals = []
    skipSignals = []
    closeSignals = []

    trace = True
    ticker = None