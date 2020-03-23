# Gets user input of stocks, time period and metrics and plots the metric values over the given time period.

import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

# get list of metrics and stock tickers to print
metrics = input("Enter a comma-space-separated list of metrics to plot from the below:\n"
                "Open, High, Low, Close, Volume\n")
stocks = input("Enter a comma-space-separated list of stock tickers for which to plot the chosen metrics:\n")

metricsList = metrics.split(", ")     # convert metric string to list
stocksList = stocks.split(", ")     # convert tickers string to list

# get period start and end from user
timeStart = input("Enter history start date in the format YYYY-MM-DD:\n")
timeEnd = input("Enter end date in the format YYYY-MM-DD:\n")


# get historical data of a given stock from ticker name, start and end, and metric name
def get_stock_data(tick, metric, timeStart, timeEnd):

    ticker = yf.Ticker(tick)        # get yf ticker
    ticker_hist = ticker.history(start=timeStart, end=timeEnd)  # generate history of ticker
    data_hist = ticker_hist[metric]         # get data of specific metric

    return pd.Series(data_hist)     # return data as pandas series


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

    plt.xlabel('Date')
    plt.ylabel(metricsList[i])

plt.show()

