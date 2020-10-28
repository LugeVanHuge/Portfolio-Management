import pandas as pd
from matplotlib import pyplot as plt
import datetime
import yfinance as yf

"""
Track the performance of a portfolio of stocks with manual entries for buy and sell orders.
JSE-listed stocks include a .JO and are priced in ZAR cents. US-listed stocks are priced in USD.
"""
# ######################################### Global Parameters ########################################################

stocks = ['ETF500.JO', 'ETF5IT.JO', 'DGH.JO', 'NPN.JO', 'NFEMOM.JO', 'PPE.JO', 'BTC-USD', 'ETH-USD', 'XRP-USD',
          'LINK-USD', 'BCH-USD', 'LTC-USD', 'ADA-USD', 'BNB-USD', 'BRK-B', 'VOO', 'CLS.JO', 'FSR.JO', 'ANG.JO',
          'NY1.JO', 'SYG4IR.JO']
start = datetime.date(2020, 4, 1)
end = datetime.date.today() - datetime.timedelta(days=1)    # choose end as yesterday to avoid yfinance glitch
start_str = str(start)
end_str = str(end)
data = pd.DataFrame()
RFRR = 6.5         # risk-free rate of return in SA over given period (%)

# ######################################### Populate DataFrame #######################################################

# get price data for all stocks in data and add columns for holdings
for ticker in stocks:
    data[ticker] = yf.download(ticker, start_str, end_str)["Adj Close"]
    data[ticker + " shares"] = 0.0
# get exchange rate
data["USD/ZAR"] = yf.download("ZAR=X", start_str, end_str)["Adj Close"]

# no data for DCX10 in yfinance, so do this manually (have to ignore two of the small coins for now (19 Aug 2020))
data["DCX10"] = (data['BTC-USD'] + data['ETH-USD'] + data['XRP-USD'] +
                       data['LINK-USD'] + data['BCH-USD'] + data['LTC-USD'] +
                       data['ADA-USD'] + data['BNB-USD']) * 1.255624651480927e-4
data["DCX10 shares"] = 0.0

# empty columns to track portfolio value and cumulative amount of capital invested
data["Portfolio"] = 0.0
data["Cumulative Capital Invested"] = 0.0

# fill in any existing nan values
data.ffill(axis=0, inplace=True)

# adjust share prices so that data value is in ZAR
for ticker in stocks:
    if "JO" in ticker:  # if SA stock, get ZAR from ZAR cents
        data[ticker + " ZAR"] = data[ticker] / 100
    else:   # else convert to ZAR from USD
        data[ticker + " ZAR"] = data[ticker] * data["USD/ZAR"]
# DCX10 is not listed so this is done manually:
data["DCX10 ZAR"] = data["DCX10"] * data["USD/ZAR"]


# ############################## functions to buy or sell a set number of shares ######################################

def buy(ticker, date, shares):
    data.loc[date:end_str, ticker + " shares"] += shares
    data.loc[date:end_str, "Cumulative Capital Invested"] += shares * data[ticker + " ZAR"][date]


def sell(ticker, date, shares):
    data.loc[date:end_str, ticker + " shares"] += shares
    data.loc[date:end_str, "Cumulative Capital Invested"] -= shares * data[ticker + " ZAR"][date]


# ################################ manually enter transactions (in shares): ###########################################

buy("ETF5IT.JO", "2020-06-17", 40.5405)
buy("NPN.JO", "2020-06-03", 0.1722 + 0.3442)
buy("NFEMOM.JO", "2020-07-17", 14.2857)
buy("PPE.JO", "2020-07-17", 1886.7925)
buy("DCX10", "2020-07-17", 12.0880)
#buy("VOO", "2020-04-02", 2.2018)
buy("CLS.JO", "2020-06-03", 2.0877)
buy("FSR.JO", "2020-06-04", 11.6523)
buy("ETF500.JO", "2020-06-04", 1.7925)
buy("ETF500.JO", "2020-06-17", 1.9135)
buy("ETF500.JO", "2020-06-19", 1.8220)
buy("ETF500.JO", "2020-07-17", 88.8889 + 21.0778)
buy("DGH.JO", "2020-05-22", 13.1222)
sell("DGH.JO", "2020-06-03", 5.7882)
buy("DGH.JO", "2020-08-18", 0.0015)
sell("NPN.JO", "2020-06-19", 0.1585)
#buy("BRK-B", "2020-04-02", 1.1372)
#buy("BRK-B", "2020-08-17", 0.0156)
sell("CLS.JO", "2020-06-12", 2.0877)
sell("FSR.JO", "2020-06-12", 11.6523)
buy("ANG.JO", "2020-08-25", 1.5756)
buy("NY1.JO", "2020-08-25", 10.3521)
buy("SYG4IR.JO", "2020-08-25", 12.8252)
buy("PPE.JO", "2020-08-25", 340.3288)

# ########################################### Other Calculations #####################################################

# compute total portfolio value:
for ticker in stocks:
    data["Portfolio"] += data[ticker + " shares"] * data[ticker + " ZAR"]

# compute portfolio returns adjusted for a R1000 investment
adj_returns = data.copy()
adj_returns["Return on R1000 Invested"] = 0.0
for ticker in stocks:
    adj_returns[ticker + " shares"] = adj_returns[ticker + " shares"] * 1000 /\
                                      adj_returns["Cumulative Capital Invested"]
    adj_returns["Return on R1000 Invested"] += adj_returns[ticker + " shares"] * adj_returns[ticker + " ZAR"]

# Create benchmark of R1000 invested into SNP500
adj_returns["R1000 of SNP shares"] = 1000.0 / data["VOO ZAR"][start_str]
adj_returns["R1000 of SNP"] = adj_returns["R1000 of SNP shares"] * data["VOO ZAR"]

# ############################################## Plot Results ########################################################

# print KPIs
days_invested = (end - start).days
f_num_years = days_invested / 365.0      # number of years as a float
endval = adj_returns["Return on R1000 Invested"].iloc[-1]
portfolio_return = (endval - 1000.0) / 1000.0 * 100.0   # return to date as a percentage
annualised_returns = (1 + portfolio_return/100)**(1 / f_num_years) - 1
risk = adj_returns['Return on R1000 Invested'].std()
mean = adj_returns['Return on R1000 Invested'].mean()
risk_pct = risk/mean * 100.0
sharpe = (annualised_returns * 100 - RFRR) / risk
print(f"Annualised return = {round(annualised_returns*100,2)}%\nPortfolio standard deviation = {round(risk_pct,2)}%"
      f"\nSharpe ratio = {round(sharpe,2)}")

# plot data
plt.figure()
plt.title("Portfolio Returns vs Benchmark")
plt.plot(adj_returns["Return on R1000 Invested"], label='Return on R1000 Invested in Portfolio')
plt.plot(adj_returns["R1000 of SNP"], label='Return on R1000 Invested in S&P500')
plt.legend()
plt.grid()

plt.figure()
plt.title("Portfolio Value and Capital Invested")

# Clean first data point for better scaled plot
data["Portfolio"][start_str] = data["Portfolio"]["2020-04-02"]
data["Cumulative Capital Invested"][start_str] = data["Cumulative Capital Invested"]["2020-04-02"]

plt.plot(data["Portfolio"], label='Portfolio Value')
plt.plot(data["Cumulative Capital Invested"], label='Total Capital Invested')
plt.legend()
plt.grid()

plt.show()
