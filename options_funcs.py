#options_funcs.py
import math
from scipy.stats import norm
from utilities import days_until_date
from model import CALL_OR_PUT

interest_rate = 0.0425

def black_scholes_delta(S, K, T, r, sigma, option_type=CALL_OR_PUT.CALL):
    """
    Calculates the Black-Scholes Delta for a European option.

    Parameters:
    S (float): Current stock price
    K (float): Strike price of the option
    T (float): Time to maturity (in years)
    r (float): Risk-free interest rate (annualized, as a decimal)
    sigma (float): Volatility of the underlying stock (annualized, as a decimal)
    option_type (str): 'call' for a call option, 'put' for a put option

    Returns:
    float: The Delta of the option
    """

    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))

    if option_type == CALL_OR_PUT.CALL:
        delta = norm.cdf(d1)
    else : #PUT
        delta = norm.cdf(d1) - 1

    return delta


def get_delta(ticker, strike_price, DTE, r, sigma, call_or_put=CALL_OR_PUT.CALL):
    S = ticker.info['currentPrice']
    K = strike_price 
    T = DTE/365.0
    #r = 0.00425
    delta = black_scholes_delta(S, K, T, r, sigma, call_or_put)
    return round(float(delta), 2)

    return .5

def get_strike_prices_and_premiums(stock_ticker,selected_date,call_or_put=CALL_OR_PUT.CALL):
    options_chain = stock_ticker.option_chain(selected_date)

    # The options_chain object has separate attributes for calls and puts
    if call_or_put == CALL_OR_PUT.CALL:
       df = options_chain.calls
    else: # PUT
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



def get_options_chain(stock_ticker, selected_date):
    # return optons chain as a list format:
    '''
        {"CALLS":[
                (STRIKE1, PREMIUM1, DELTA1),
                (STRIKE2, PREMIUM2, DELTA2),
                ...
            ],
        "PUTS": [
                (STRIKE1, PREMIUM1, DELTA1),
                (STRIKE2, PREMIUM2, DELTA2),
                ...        
            ]
        }
    '''
    calls_chain = get_strike_prices_and_premiums(stock_ticker,selected_date,CALL_OR_PUT.CALL)
    puts_chain = get_strike_prices_and_premiums(stock_ticker,selected_date,CALL_OR_PUT.PUT)
    # add the delta
    DTE = days_until_date(selected_date)
    calls_deltas = []
    for c in calls_chain:
            calls_deltas.append(get_delta(stock_ticker, c[0], 
                    DTE,interest_rate,c[2],CALL_OR_PUT.CALL))
    calls_chain2 = [tup + (item,) for tup, item in zip(calls_chain, calls_deltas)]

    # repeat for puts
    puts_deltas = []
    for c in puts_chain:
            puts_deltas.append(get_delta(stock_ticker, c[0], 
                    DTE,interest_rate,c[2],CALL_OR_PUT.PUT))
    puts_chain2 = [tup + (item,) for tup, item in zip(puts_chain, puts_deltas)]
    # put in a dictionary
    # format data
    calls_chain2 =[(round(item[0], 1), round(item[1], 2),
                    round(item[2], 2), round(item[3], 2))
                    for item in calls_chain2]

    puts_chain2 = [(round(item[0], 1), round(item[1], 2),
                    round(item[2], 2), round(item[3], 2))
                    for item in puts_chain2]
    d = {"CALLS":calls_chain2, "PUTS":puts_chain2}
    return d


