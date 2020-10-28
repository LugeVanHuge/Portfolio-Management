import yfinance as yf
import pandas as pd
import numpy as np
import datetime as dt


# gets stock attribute over a history
# e.g. Open    High    Low    Close   Volume   Dividends   Splits
def get_attr_history(tick, attribute, start, end, interval):

    ticker = yf.Ticker(tick)  # get yf ticker from input
    return pd.Series(ticker.history(start=start, end=end, interval=interval)[attribute])


# gets daily (close-open) as a percentage over a history
def get_delta_history(tick, time_range):

    ticker = yf.Ticker(tick)    # get yf ticker from input
    ticker_hist = ticker.history(period=time_range)    # generate history of ticker
    closeList = ticker_hist['Close']    # get close values from history
    openList = ticker_hist['Open']      # get open values from history

    deltaList = [0]*int(len(closeList))  # initialise list of deltas

    j = 0
    for j in range(len(deltaList)):     # calculate bi-monthly price delta % over history
        deltaList[j] = (1 - openList[j]/closeList[j])*100

    return pd.Series(deltaList)    # convert list into panda series


# gets history of volatility (calculated as SDev) of a stock on a monthly basis
def get_month_volatility(tick, time_range):

    close_hist = np.array(get_attr_history(tick, 'Close', time_range))  # get close history
    volatility_hist = [0]*int(len(close_hist)/30)    # initialise array for volatility history

    for i in range(int(len(close_hist)/30)):        # calculate standard deviation for each month in history
        month_values = close_hist[i*30 : (i+1)*30]
        month_values = pd.Series(month_values)
        volatility_hist[i] = month_values.std()

    return pd.Series(volatility_hist)


# gets (close_i - close_(i-1)) of a stock from a start to end date (YYYY-MM-DD)
def get_stock_change(tick, start, end):

    # format start and end dates to allow for operators
    start1 = dt.datetime.strptime(start, '%Y-%m-%d')
    end1 = dt.datetime.strptime(end, '%Y-%m-%d')
    # get start and end one day earlier
    start2 = dt.datetime.strptime(start, '%Y-%m-%d') - dt.timedelta(days=1)
    end2 = dt.datetime.strptime(end, '%Y-%m-%d') - dt.timedelta(days=1)

    # get series for day i and day i - 1
    ticker = yf.Ticker(tick)  # get yf ticker from input
    close_hist_i = np.array(ticker.history(start=start1, end=end1)["Close"])
    close_hist_im1 = np.array(ticker.history(start=start2, end=end2)["Close"])
    close_change = np.subtract(close_hist_i, close_hist_im1)

    close_change = np.array([100*(close_hist_i[i] - close_hist_im1[i])/close_hist_i[i] for i in range(len(close_hist_i))])
    change_mean = np.average(close_change)
    change_sdev = np.std(close_change)
    # get dates array
    dates = np.array([start1 + dt.timedelta(days=i) for i in range(len(close_hist_i))])

    # get stock change series
    return [pd.DataFrame(close_change, index=dates), change_mean, change_sdev]

