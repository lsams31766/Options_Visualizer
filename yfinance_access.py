# get options data from yfinance
import yfinance as yf
import pandas as pd

'''
  TODO
  We want options chain for a given Ticker
  1) Select Ticker
  2) Get available exiration dates
  3) Get available strike prices
  4) For a given Put/Call strike price, expiration, get
     - price of option
     - implied volatlity
'''

def get_expiration_dates(stock_ticker):
    try:
        # Get the available options expiration dates
        expiration_dates = stock_ticker.options
        return expiration_dates
    except Exception:
        return None


def get_strike_prices_and_premiums(stock_ticker,selected_date,call=True):
    options_chain = stock_ticker.option_chain(selected_date)

    # The options_chain object has separate attributes for calls and puts
    if call == True:
       df = options_chain.calls
    else:
        df = options_chain.puts
    '''
    Column names:
    ['contractSymbol', 'lastTradeDate', 'strike', 
    'lastPrice', 'bid', 'ask', 'change', 'percentChange', 
    'volume', 'openInterest', 'impliedVolatility', 
    'inTheMoney', 'contractSize', 'currency']
    '''
    result_list = df[['strike', 'lastPrice','impliedVolatility']].apply(tuple, axis=1).to_list()
    return result_list

def get_sigma(stock_ticker, selected_date, strike_price, call=True):
    options_chain = stock_ticker.option_chain(selected_date)
    if call == True:
       df = options_chain.calls
    else:
        df = options_chain.puts
    # print(df)
    sigma = df[df['strike'] == strike_price]['impliedVolatility'].iloc[0]
    return sigma

def get_current_stock_price(ticker_symbol):
    #ticker = yf.Ticker("AAPL")
    # Get the most recent price information
    stock_ticker = yf.Ticker(ticker_symbol)
    current_price = stock_ticker.info['currentPrice']
    return current_price, stock_ticker

# TODO get stock history 
# given ticker name, history period, interval (daily, weekly, ...)
yf_period_values = ["1d", "5d", "1mo", "3mo", "6mo", "1y", 
                    "2y", "5y", "10y", "ytd", "max"]

yf_interval_values = ["1m", "2m", "5m", "15m", "30m", "60m", 
                      "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
def get_yf_period_values():
    return yf_period_values

def get_yf_interval_values():
    return yf_interval_values

def get_stock_dates_and_prices(ticker_name, period_value, interval_value):
    # return dict of dates and prices
    d = {}
    meta = yf.Ticker(ticker_name)
    df = meta.history(period=period_value, interval=interval_value)
    # move index to a column in format YY-MM-DD
    df['Date'] = df.index
    df['Date'] = pd.to_datetime(df['Date'])
    df['Formatted_Date'] = df['Date'].dt.strftime('%y-%m-%d')
    # round price to 2 decimal places
    df = df.round({'Close':2})
    # put into dict
    l_dates = list(df['Formatted_Date'])
    l_prices = list(df['Close'])
    for i in range(len(l_dates)):
        d[l_dates[i]] = l_prices[i]
    return d



# get historical prices for a stock
def main():
    d = get_stock_dates_and_prices('ORCL','1mo','1d')
    for k,v in d.items():
        print(k,v)

    return
    # Create a Ticker object for the desired stock (e.g., "META" for Meta Platforms)
    meta = yf.Ticker("ORCL")

    # Get historical market data for the maximum available period
    # data = meta.history(period="max")
    # print(data.head())

    # Get data for a specific period and interval (e.g., last 3 months, weekly data)
    weekly_data = meta.history(period="3mo", interval="1wk")
    weekly_data['Date'] = weekly_data.index
    weekly_data['Date'] = pd.to_datetime(weekly_data['Date'])
    weekly_data['Formatted_Date'] = weekly_data['Date'].dt.strftime('%y-%m-%d')
    weekly_data = weekly_data.round({'Close':2})
    #print(weekly_data.columns)
    #print(weekly_data['Close'].head())
    tuples_list = list(zip(weekly_data['Formatted_Date'], weekly_data['Close']))
    for t in tuples_list[0:9]:
        print(f"'{t[0]}',")
    for t in tuples_list[0:9]:
        print(f"'{t[1]}'")

if __name__ == "__main__":
    main()