# Gets user input of stocks, time period and metrics and plots the metric values over the given time period.

import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# get list of metrics and stock tickers to print
metrics = input("Enter a comma-space-separated list of metrics to plot from the below:\n"
                "Open, High, Low, Close, Volume, DailyReturn%, WeekVolatility, MonthVolatility\n")
stocks = input("Enter a comma-space-separated list of stock tickers for which to plot the chosen metrics:\n")

metricsList = metrics.split(", ")     # convert metric string to list
stocksList = stocks.split(", ")     # convert tickers string to list

# get period start and end from user
timeStart = input("Enter history start date in the format YYYY-MM-DD:\n")
timeEnd = input("Enter end date in the format YYYY-MM-DD:\n")


# get volatility of stock's value on a monthly basis based off closing values
def get_month_volatility(ticker_hist):

    close_hist = np.array(ticker_hist['Close'])  # get close history
    volatility_hist = [0]*int(len(close_hist)/30)    # initialise array for volatility history

    for i in range(int(len(close_hist)/30)):        # calculate standard deviation for each month in history
        month_values = close_hist[i*30 : (i+1)*30]
        month_values = pd.Series(month_values)
        volatility_hist[i] = month_values.std()

    return pd.Series(volatility_hist)


# get volatility of stock's value on a weekly basis based off closing values
def get_week_volatility(ticker_hist):

    close_hist = np.array(ticker_hist['Close'])  # get close history
    volatility_hist = [0]*int(len(close_hist)/7)    # initialise array for volatility history

    for i in range(int(len(close_hist)/7)):         # calculate standard deviation for each week in history
        week_values = close_hist[i*7 : (i+1)*7]
        week_values = pd.Series(week_values)
        volatility_hist[i] = week_values.std()

    return pd.Series(volatility_hist)


# get history of daily percentage change of a stock
def get_return_percent(ticker_hist):

    close_hist = ticker_hist['Close']       # get close history
    open_hist = ticker_hist['Open']         # get open history
    change_hist = [0]*len(close_hist)       # initialise array for change history

    for i in range(len(close_hist)):        # calculate percentage change for each day in history
        change_hist[i] = (1 - open_hist[i]/close_hist[i])*100

    return pd.Series(close_hist)        # return panda series


# get historical data of a given stock from ticker name, start and end, and metric name
def get_stock_data(tick, metric, timeStart, timeEnd):

    ticker = yf.Ticker(tick)        # get yf ticker
    ticker_hist = ticker.history(start=timeStart, end=timeEnd)  # generate history of ticker

    if metric == 'DailyReturn%':
        data_hist = get_return_percent(ticker_hist)     # get daily return percent history

    elif metric == 'WeekVolatility':
        data_hist = get_week_volatility(ticker_hist)

    elif metric == 'MonthVolatility':
        data_hist = get_month_volatility(ticker_hist)

    else:
        data_hist = ticker_hist[metric]         # get data of specified metric
        data_hist = pd.Series(data_hist)        # convert to panda series

    return data_hist


# plot data
i = 0
for i in range(len(metricsList)):   # iterate through metrics
    dataList = pd.DataFrame({})  # make pandas dataframe to store information of current metric
    j = 0
    for j in range(len(stocksList)):    # iterate through stocks
        # append stock data for current metric onto dataframe
        dataList[stocksList[j]] = get_stock_data(stocksList[j], metricsList[i], timeStart, timeEnd)

    # plot all stock's data for current metric
    dataList.plot(title=metricsList[i])

    # choose label for x-axis
    if metricsList[i] == 'WeekVolatility':
        xlabel = 'Weeks from start date'
    else:
        xlabel= metricsList[i]

    plt.xlabel(xlabel)
    plt.ylabel(metricsList[i])

plt.show()

