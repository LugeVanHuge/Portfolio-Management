from StockGetFunctions import get_attr_history
import numpy as np
import matplotlib.pyplot as plt

# choose parameters for price time series
ticker = "MSFT"
start = "2018-01-01"
end = "2020-01-01"
interval = "1d"

# get time series from yfinance and choose starting values for portfolio

close_hist = get_attr_history(ticker, "Close", start, end, interval)
cash = 500.0
portfolio = 500.0


# calculate a moving average from a time series, at a current date and for a chosen time interval
def running_ma(time_series, current_date, ma_period):

    ma = time_series[current_date - ma_period : current_date].mean()

    return ma


# wallet class to store portfolio values
class Wallet:
    cash = cash
    holdings = portfolio


# buy an amt in cash to holdings
def buy(amt):
    if Wallet.cash > amt:   # if funds are sufficient, move cash into stock holdings
        Wallet.cash -= amt
        Wallet.holdings += amt
    else:                   # else sell as much as is available (this might be a bad idea)
        amt = Wallet.cash
        Wallet.cash -= amt
        Wallet.holdings += amt


# sell an amt from holdings to generate cash
def sell(amt):
    if Wallet.holdings > amt:   # if holdings are sufficient, sell amt to generate cash
        Wallet.cash += amt
        Wallet.holdings -= amt
    else:                       # else sell as much stock as possible
        amt = Wallet.holdings
        Wallet.cash += amt
        Wallet.holdings -= amt


# update holdings value at start of day
def update(time_series, current_date):
    Wallet.holdings = Wallet.holdings * time_series[current_date]/time_series[current_date - 1]


# TESTING:

# initialise parameters and arrays
undervalued = True
portfolio_history = np.zeros(shape=(2, len(close_hist), 2))
ma_history = np.zeros(shape=(2, len(close_hist)))
amt = 10
amt_temp = amt      # temp variable for changing amt if necessary

# step through time series element-wise
for i in range(len(close_hist)):

    # update value of holdings based on change since previous period
    update(close_hist, i)
    # compute both moving averages
    ma_long = running_ma(close_hist, i, 30)
    ma_short = running_ma(close_hist, i, 7)

    # increase amt proportional to distance from mean
    amt_temp = amt * (ma_long - ma_short)**2 / ma_long

    # mean reversion: if 30d MA < 90d MA, assume stock is undervalued and buy.
    # if 30d MA > 90d MA, assume stock is overvalued and sell.
    # occurs once per day, after price has been updated.
    if ma_short < ma_long:
        buy(amt_temp)
    elif ma_short > ma_long:
        sell(amt_temp)

    # populate history arrays for plotting
    ma_history[0][i] = ma_short
    ma_history[1][i] = ma_long
    portfolio_history[0][i] = Wallet.cash
    portfolio_history[1][i] = Wallet.holdings

# print main results:
total_portfolio = portfolio_history[:][0] + portfolio_history[:][1]
portfolio_end = total_portfolio[-1][0]
portfolio_start = total_portfolio[0][0]

portfolio_return = round(portfolio_end/portfolio_start * 100, 2)
cash_percent = round(portfolio_history[0][-1][0]/portfolio_end * 100, 2)
equity_percent = 100 - cash_percent
stock_return = round(close_hist[-1]/close_hist[0] * 100, 2)
print(f"{ticker} market returns from {start} to {end}:\n{stock_return}%\n"
      f"Portfolio returns:\n{portfolio_return}%"
      f"\nWith {cash_percent}% of portfolio in cash and "
      f"{equity_percent}% in stocks at {end}")

# plot results with matplotlib.pyplot
fig, a = plt.subplots(2, 2)

a[0][0].plot(np.arange(0, len(close_hist)), ma_history[:][0], 'r')
a[0][0].plot(np.arange(0, len(close_hist)), ma_history[:][1], 'b')
a[0][0].plot(np.arange(0, len(close_hist)), close_hist, 'k')
a[0][0].set_title("Moving Averages Over Price History")
a[0][1].plot(np.arange(0, len(close_hist)), portfolio_history[:][0] + portfolio_history[:][1], 'k')
a[0][1].set_title("Total Portfolio Value")
a[1][0].plot(np.arange(0, len(close_hist)), portfolio_history[:][0], 'r')
a[1][0].set_title("Cash")
a[1][1].plot(np.arange(0, len(close_hist)), portfolio_history[:][1], 'r')
a[1][1].set_title("Equity Holdings")

fig.suptitle(f"Plotted results for mean reversion trading of {ticker} from {start} to {end}\n"
             f"With trading unit of ${amt} and sampling period of {interval}")
plt.show()