from StockGetFunctions import get_attr_history
import numpy as np
import matplotlib.pyplot as plt

# ====== set global variables ======
start = "2012-01-01"    # start date in "YYYY-MM-DD"
end = "2017-01-01"      # end date in "YYYY-MM-DD"
interval = "1d"         # sampling period for stock prices (see yfinance intervals)
ticker_list = ["VOO", "^FTSE", "VWO"]       # choose tickers to trade
SNP = get_attr_history("VOO", "Close", start, end, interval)    # get S&P500 series for benchmarking
ma_long_interval = 10   # interval to calculate long-term moving average
ma_short_interval = 5  # interval to calculate short-term moving average

series_list = {}    # initialise dictionary of ticker price series
ma_list = {}
cash = 10000.0
trade_factor = 0.05  # factor to modify trade amount
# initialise lists to store history of portfolio data
cash_history = []
holdings_history = []
portfolio_history = []
# ==================================


# function to get ma over an entire time series for a given series
def ma_series(series, ma_period):
    ma = np.zeros(len(series))
    for i in range(len(series)):
        if i > ma_period:
            ma[i] = series[i - ma_period : i].mean()

    return ma


# populate series and MA lists
for ticker in ticker_list:
    series_list[ticker] = get_attr_history(ticker, "Close", start, end, interval).to_numpy()
    ma_list[ticker] = [ma_series(series_list[ticker], ma_long_interval),
                       ma_series(series_list[ticker], ma_short_interval)]


# class to define Stock objects for keeping price and moving averages, etc.
class Stock:

    # initialise stock info
    def __init__(self, ticker):
        self.ticker = ticker
        self.price = 0.0
        self.ma_long = 0.0
        self.ma_short = 0.0
        self.undervalued = False
        self.ma_deviation = 0.0
        self.position = 0.0
        self.trade_amt = 0.0
        self.price_yesterday = 0.0

    # update stock ticker info on a given day
    def get_info(self):
        # update price and position
        self.price = prices_today[self.ticker]
        if self.price_yesterday == 0.0:
            pass
        else:
            self.position *= self.price/self.price_yesterday    # change position according to price change
        self.price_yesterday = self.price   # move "yesterday's" price one day forward
        # update MA values
        self.ma_long = ma_today[self.ticker][0]
        self.ma_short = ma_today[self.ticker][1]
        # check if stock is undervalued or not
        if self.ma_long > self.ma_short:
            self.undervalued = True
        else:
            self.undervalued = False
        # get deviation of short ma from long ma (based on square distance)
        if self.ma_long == 0:
            self.ma_deviation = 0.0
        else:
            self.ma_deviation = abs(self.ma_short - self.ma_long) / self.ma_long
        # define an amount to trade based on the ma deviation
        self.trade_amt = self.position * self.ma_deviation

    def trade(self):
        if self.undervalued:    # if stock is undervalued, buy more
            self.position += self.trade_amt
        elif not self.undervalued:  # else, sell
            # sell amt of stock, or whole position if amt > position
            self.position = max(self.position - self.trade_amt, 0.0)


# function to buy and sell stocks on a given day
def trade(stocks_info, cash):
    total_dev = 0.0     # variable to store sum of stock deviations for undervalued stocks
    #print("===New trade===")
    # deal with overvalued stocks (selling) first
    for ticker in stocks_info:      # loop through all stocks
        Stock = stocks_info[ticker]

        if not Stock.undervalued:   # if stock is overvalued, sell amt (or whole position if amt > position)
            #print(f"==Sell overval stock: {ticker}")
            #print(f"Cash before trade: {cash}\nPosition before trade:{Stock.position}\nTrade amt: {Stock.trade_amt}")
            Stock.trade()
            cash += min(Stock.position, Stock.trade_amt)
            #print(f"Cash after trade: {cash}\nPosition after trade: {Stock.position}")
        elif Stock.undervalued:     # count deviation for undervalued stocks
            total_dev += Stock.ma_deviation

    buy_amt = cash * trade_factor       # set aside cash to buy

    # deal with buying undervalued stocks
    for ticker in ticker_list:      # loop through all stocks (again)
        Stock = stocks_info[ticker]

        if Stock.undervalued:   # for undervalued stocks, buy proportionally to MA deviation
            #print("==Buy underval stock:", Stock.ticker)
            Stock.trade_amt = buy_amt * Stock.ma_deviation / total_dev      # set proportional trade amt
            #print(f"Cash before trade: {cash}\nPosition before trade:{Stock.position}\nMA deviation: {Stock.ma_deviation}\nTrade amt: {Stock.trade_amt}")
            Stock.trade()       # buy amt of stock
            cash -= Stock.trade_amt     # reflect purchase in cash reserves
            #print(f"Cash after trade: {cash}\nPosition after trade: {Stock.position}")

    return cash



# initialise stock objects from ticker list
stocks_info = {}
for ticker in ticker_list:
    stocks_info[ticker] = Stock(ticker)


# simulate real-time prices
for i in range(len(SNP)):
    #print(f"++++ Day {i} ++++")
    if i < ma_long_interval:    # don't trade until MA can be calculated
        pass
    else:

        # get today's price for each stock in ticker list
        prices_today = {}    # init prices list dictionary
        ma_today = {}        # init moving average list dictionary
        for ticker in ticker_list:
            while True:
                try:
                    prices_today[ticker] = series_list[ticker][i]    # for each ticker, set the prices list element to today's price
                    ma_today[ticker] = [ma_list[ticker][0][i], ma_list[ticker][1][i]]     # likewise for moving averages
                    stocks_info[ticker].get_info()      # get stock info for today
                    break
                except IndexError:
                    print(f"{ticker} has the wrong number of periods")
                    break
        # perform trading algorithm (sell overvalued stocks then use portion of cash to buy undervalued stocks)
        cash = trade(stocks_info, cash)

    # sum stock positions to get total holdings for the day
    holdings_total = 0.0
    for ticker in ticker_list:
        Stock = stocks_info[ticker]
        holdings_total += Stock.position

    # append histories
    cash_history.append(cash)
    holdings_history.append(holdings_total)
    portfolio_history.append(cash + holdings_total)

# === plot results with matplotlib.pyplot ===
# replace all zero MAs with NaN for prettier graphs
for ticker in ticker_list:
    for i in range(ma_long_interval+1):
        ma_list[ticker][0][i] = "NaN"
        ma_list[ticker][1][i] = "NaN"

# plot stock data
fig, a = plt.subplots(len(ticker_list))
i = 0
for ticker in ticker_list:
    a[i].plot(series_list[ticker], "k")
    a[i].plot(ma_list[ticker][0], "b")
    a[i].plot(ma_list[ticker][1], "r")
    a[i].set_title(ticker)
    i += 1

# print results summary
print(f"Trading results from {start} to {end}:\n_________________________________")
portfolio_returns = round(portfolio_history[-1] / portfolio_history[0] * 100, 2)
print(f"Portfolio returns: {portfolio_returns}%\n_________________________________")
market_returns_sum = 0.0
for ticker in ticker_list:
    market_returns = round(series_list[ticker][-1] / series_list[ticker][0] * 100, 2)
    print(f"Market returns for {ticker}: {market_returns}%")
    market_returns_sum += market_returns
print(f"_________________________________\nAverage market return: {round(market_returns_sum/len(ticker_list), 2)}%")
print(f"S&P500 returns: {round(SNP[-1] / SNP[0] * 100, 2)}%")

# plot portfolio data
plt.figure()
plt.plot(np.arange(0, len(SNP)), portfolio_history, 'k', label="Total portfolio")
plt.title("Portfolio Values")
plt.plot(np.arange(0, len(SNP)), cash_history, 'b', label="Cash")
plt.plot(np.arange(0, len(SNP)), holdings_history, 'r', label="Equity")

plt.legend()
plt.show()
