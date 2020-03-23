import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Uses price history of a list of stocks to plot risk/reward efficiency frontier based off Modern Portfolio Theory.
# Returns are considered bi-monthly.

stockInput = input("Enter a comma-space-separated stock tickers list. e.g. MSFT, GOOG, AMZN:\n")
timeRange = input("Enter a time period from the following:\n3mo, 6mo, "
                  "1y, 2y, 5y, 10y, ytd, max.\n")
resolution = int(input("Enter an integer portfolio weighting resolution percentage. e.g. res = 20 will permute "
                       "weightings in 20% increments:\n"))
resolution = int(100/resolution)    # convert percentage to a fraction of 100%


# get history of stock delta (close-open) as a percentage
def getDeltaHistory(tick, timeRange):

    ticker = yf.Ticker(tick)    # get yf ticker from input
    ticker_hist = ticker.history(period=timeRange)    # generate history of ticker
    closeList = ticker_hist['Close']    # get close values from history
    openList = ticker_hist['Open']      # get open values from history

    deltaList = [0]*int(len(closeList))  # initialise list of deltas

    j = 0
    for j in range(len(deltaList)):     # calculate bi-monthly price delta % over history
        deltaList[j] = (1 - openList[j]/closeList[j])*100

    return pd.Series(deltaList)    # convert list into panda series


# get mean daily delta for a stock
def getMean(tick):
    deltaList = getDeltaHistory(tick, timeRange)    # get delta list

    return deltaList.mean()      # get mean of daily deltas


# get standard deviation of daily deltas for a stock
def getsDev(tick):
    deltaList = getDeltaHistory(tick, timeRange)    # get delta list
    deltasDev = deltaList.std()

    return deltasDev


# generate all possible permutations of portfolio composition with a given resolution
# note that resolution will also give the total weight of the portfolio
def weights(portfolio_size, resolution):

    if portfolio_size == 1:
        yield (resolution,)
    else:
        for value in range(resolution):
            for permutation in weights(portfolio_size - 1, resolution - value):
                yield (value,) + permutation


# find weighted return of portfolio
def portfolio_return(portfolio):

    weighted_return = 0

    i = 0
    for i in range(len(portfolio)):
        weighted_return += portfolio[i].weight * portfolio[i].mean

    return weighted_return


# find weighted risk (sDev) of entire portfolio
def portfolio_risk(portfolio, timeRange):

    # generate data frame of stock deltas
    sDevFrame = pd.DataFrame([[0]*len(portfolio)]*len(getDeltaHistory(portfolio[0].tick, timeRange)))

    i = 0
    for i in range(len(portfolio)):
        sDevFrame[i] = getDeltaHistory(portfolio[i].tick, timeRange)

    covMatrix = sDevFrame.cov()     # covariance matrix of portfolio
    covMatrix = np.array(covMatrix)

    # make diagonal values = 1
    i = 0
    for i in range(len(portfolio)):
        j = 0
        for j in range(len(portfolio)):
            if i == j:
                covMatrix[i][j] = 1

    # generate vertical and horizontal weighting matrices
    wtHorizontal = np.array([0.0]*len(portfolio))     # horizontal weighting matrix
    wtVertical = np.array([[0.0]] * len(portfolio))   # vertical weighting matrix
    i = 0
    for i in range(len(portfolio)):     # populate matrices
        wtHorizontal[i] = float(portfolio[i].weight*resolution_scale)
        wtVertical[i] = float(portfolio[i].weight*resolution_scale)

    # generate sDev matrix
    sDevMatrix = np.array([[0.0]*len(portfolio)]*len(portfolio))
    i = 0
    for i in range(len(portfolio)):
        j = 0
        for j in range(len(portfolio)):
            if i == j:
                sDevMatrix[i][j] = portfolio[i].sDev

    # compute portfolio variance (risk) with matrix multiplication
    total_risk = np.matmul(np.matmul(np.matmul(np.matmul(wtHorizontal, sDevMatrix), covMatrix), sDevMatrix), wtVertical)

    return float(total_risk)


class Stock:  # relevant information for stocks

    def __init__(self, tick, mean, sDev, weight):
        self.tick = tick
        self.mean = mean
        self.sDev = sDev
        self.weight = weight


# ========================================== DRIVER CODE =============================================================

# create array and dictionary of stock tickers
stockNames = stockInput.split(", ")
portfolio = {}

resolution_scale = float(1/resolution)        # scaling factor to put final weighting into range [0, 1]

i = 0
for i in range(len(stockNames)):
    portfolio[i] = stockNames[i]

# populate stock objects using defined functions
k = 0
for k in range(len(stockNames)):

    portfolio[k] = Stock(tick=stockNames[k], mean=getMean(stockNames[k]),
                         sDev=getsDev(stockNames[k]), weight=0)

# get list of weights
weightsList = list(weights(len(portfolio), resolution))

# dataframe to store risk vs return results
risk_return = np.array([[0.0]*2]*len(weightsList))

# list to store markers for graph
weight_markers = [[0.0]*len(portfolio)]*len(weightsList)

# try all different weightings to generate portfolio risk and reward
i = 0
for i in range(len(weightsList)):
    j = 0
    for j in range(len(portfolio)):        # define a portfolio weighting
        portfolio[j].weight = weightsList[i][j]        # define stock weighting

    weight_markers[i] = weightsList[i]       # get weighting marker

    risk_return[i][0] = portfolio_risk(portfolio, timeRange)        # assign risk according to given weight matrix
    risk_return[i][1] = portfolio_return(portfolio)                 # assign return

weight_markers = np.array(weight_markers)*resolution_scale

# FINALLY plot risk vs reward for all permuted portfolio weightings
fig = plt.figure()
ax = fig.add_subplot(111)
plt.scatter(risk_return[:, 0], risk_return[:, 1], s=None, c='#ff0000', marker='.')
plt.xlabel("Portfolio Risk")
plt.ylabel("Portfolio Return")
k = 0
for i, j in zip(risk_return[:, 0], risk_return[:, 1]):
    ax.annotate(weight_markers[k], xy=(i, j))
    k += 1
plt.show()

