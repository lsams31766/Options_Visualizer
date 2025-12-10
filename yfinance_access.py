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