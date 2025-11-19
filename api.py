#api.py
#functions for external access to options data
from yfinance_access import get_current_stock_price, get_expiration_dates
from model import *
from options_funcs import get_options_chain, get_profit_and_loss

def get_ticker_quote(ticker_name):
    # given ticker name as text, validate it exists, return underlying price
    try:
        current_price, stock_ticker = get_current_stock_price(ticker_name)
        return current_price, stock_ticker
    except ValueError as e:
        print(f"ERROR retrieving stock price: {e}")

def get_strategies():
    # return a lis of tuples, the strategy and it's description
    inst_all_strategies = all_strategies
    all_s = []
    for s in inst_all_strategies:
        all_s.append((s,get_strategy_str(s)))
    return all_s

def list_expiration_dates(stock_ticker):
    # get options expiration date for given stock_ticker
    # output is a list of dates in format: YYYY-MM-DD
    expiration_dates = get_expiration_dates(stock_ticker)
    return expiration_dates

def list_options_chain(stock_ticker, expiraton_date):
    # return optons chain as a dict (see options_funcs.py
    return get_options_chain(stock_ticker, expiraton_date)

def get_pnl(optionsTrade):
    # get profit and loss over various stock prices
    # get_profit_and_loss(strategy, cur_stock_price, 
    #     strike_price1, premium1, 
    #     strike_price2=None, premium2=None,
    #     strike_price3=None, premium3=None,
    #     strike_price4=None, premium4=None):
    pnl_table = get_profit_and_loss(optionsTrade)
    return pnl_table

def test():
    current_price, stock_ticker = get_current_stock_price('AAPL')
    print("AAPL stock price:",current_price)
    print('ALL Strategies:')
    s = get_strategies()
    for item in s:
        print(item)
    print('Expiration Dates:')
    exp_dates = list_expiration_dates(stock_ticker)
    for item in exp_dates:
        print(item)
    print('-'*50)
    chain = list_options_chain(stock_ticker, exp_dates[0])
    print('CALLS')
    for item in chain['CALLS']:
        print(item)
    print('PUTS')
    for item in chain['PUTS']:
        print(item)

if __name__ == "__main__":
    test()
    # print('main')


