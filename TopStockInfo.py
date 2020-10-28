from StockGetFunctions import get_stock_change
from StockGetFunctions import get_attr_history
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

# ========= input global variables =================================== #

ticker = "GOOGL"
start = "2019-05-13"
end = "2020-05-13"
interval = "1d"       # ideally keep as '1d' for MA calcs
smoothing_factor = 2  # (keep as 2 by default)
MA_interval = 14      # interval for MA calcs in days

# ========= calculated global variables ============================== #

close_hist = get_attr_history(ticker, "Close", start, end, interval)
# dictionary to map string interval to int interval in days
interval_dict = {'1d': 1, '5d': 5, '1wk': 7, '1mo': 30, '3mo': 91}

# ==================================================================== #


# get moving average of price history over an interval in days
# calculated as MA = sum(values)/#periods
def simple_moving_average(close_history, MA_interval):
    SMA = close_history.copy()      # create copy of hist to init SMA

    # calculate MA array
    i = 0
    while i < MA_interval:
        SMA[i] = 'NaN'      # don't plot values until SMA can be properly calculated
        i += 1
    while i in range(MA_interval, len(SMA)):
        SMA[i] = close_history[i - MA_interval : i].sum()/MA_interval
        i += 1

    return SMA


# get exponential moving average over interval in days
# 12- and 26-day for short term, 50- and 200-day for longer term
# smoothing = 2 by default. Increasing weights recent pricing more.
def exp_moving_average(close_history, MA_interval, smoothing_factor):
    SF = smoothing_factor               # smoothing factor
    f = SF/(1 + MA_interval)            # pre-calculated EMA factor
    EMA = close_history.copy()          # create copy of hist to init EMA

    # calculate MA array
    i = 0
    while i < MA_interval:
        EMA[i] = 'NaN'      # don't plot values until EMA can be properly calculated
        i += 1
    EMA[MA_interval] = simple_moving_average(close_history, MA_interval)[MA_interval]   # get start value
    i += 1
    while i in range(MA_interval+1, len(EMA)):
        EMA[i] = close_history[i]*f + EMA[i-1]*(1-f)        # get EMA values until end of period
        i += 1

    return EMA


# gets moving average convergence/divergence
def MA_converge_diverge(close_history):
    close_hist = close_history.copy()

    EMA12 = exp_moving_average(close_hist, 12, 2)
    EMA26 = exp_moving_average(close_hist, 26, 2)

    MACD = EMA12.subtract(EMA26)

    return MACD


# gets the stochastic oscillator
def stochastic_oscillator(close_history):
    SO = close_history.copy()  # init SO array

    for i in range(0, 15):
        SO[i] = 'NaN'
        i += 1

    for i in range(15, len(close_history)): # compute SO for each day
        C = close_history[i-1]      # latest close
        L14 = close_history[i - 14:i].min()     # 14-day high
        H14 = close_history[i - 14:i].max()     # 14-day low
        SO[i] = ((C-L14)/(H14-L14))*100
        i += 1

    return SO


# gets moving volatility (standard deviation) over an interval
def moving_volatility(close_history, MA_interval):
    MsDev = close_history.copy()

    i = 0
    while i < MA_interval:
        MsDev[i] = 'NaN'  # don't plot values until sDev can be properly calculated
        i += 1

    while i in range(MA_interval, len(MsDev)):
        MsDev[i] = close_history[i-MA_interval:i].std()
        i += 1

    return MsDev

