#options_funcs.py
import math
from scipy.stats import norm
from utilities import days_until_date
from model import *
from options_profit_calculator import make_profit_calcs_matrix, rotate_table
from yfinance_access import get_sigma, get_current_stock_price

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

def get_prices_interval(cur_stock_price):
    # return interval of prices to create table with given stock price
    if cur_stock_price <= 1:
        return 0.1
    if cur_stock_price <= 10:
        return 1
    if cur_stock_price <= 50:
        return 1
    if cur_stock_price <= 100:
        return 1
    if cur_stock_price <= 500:
        return 3
    return 3

NBR_PRICES_BELOW_CURRENT = 10 # 10 below and 10 above current price
def get_stock_price_range(cur_stock_price):
    # return list of all stock prices to plot PnL with
    interval = get_prices_interval(cur_stock_price)
    stock_range = []
    # if price is 23.1, we want 5,10,15,20,23.1  a
    #                       and 25,30,35,40,45
    middle = round(int(cur_stock_price), interval)
    lowest = max(0,middle - (interval * NBR_PRICES_BELOW_CURRENT))
    highest = middle + (interval * NBR_PRICES_BELOW_CURRENT)
    cur = lowest
    while cur < cur_stock_price:
        stock_range.append(cur)
        cur += interval
    stock_range.append(cur_stock_price)
    if cur == cur_stock_price:
        cur += interval
        cur = round(cur, interval)
        stock_range.append(cur)
    while cur < highest:
        cur += interval
        stock_range.append(cur)
    return stock_range

# CALLER: pnl_table = get_profit_and_loss(optionsTrade)
def get_profit_and_loss(optionsTrade):
    # need to pull out data from optionsTrade to put into formulas
    # NOTE optonsTrade defined in model.py
    PNL = []
    ot = optionsTrade # smaller variable name
    leg1 = ot.legs[0]
    oq1 = leg1.options_quote
    if len(ot.legs) > 1:
        leg2 = ot.legs[1]
        oq2 = leg2.options_quote
    if len(ot.legs) > 2:
        leg3 = ot.legs[2]
        oq3 = leg3.options_quote
    if len(ot.legs) > 3:
        leg4 = ot.legs[3]
        oq4 = leg4.options_quote
    stock_range = get_stock_price_range(oq1.underlying_price)
    strategy = ot.strategy
    if strategy == Strategy.LONG_CALL:
        for p in stock_range:
            profit = round(max(p-oq1.strike_price,0)-oq1.premium,2)
            PNL.append(profit)
    
    if strategy == Strategy.LONG_PUT:
        for p in stock_range:
            profit = round(max(oq1.strike_price-p,0)-oq1.premium,2)
            PNL.append(profit)

    if strategy == Strategy.SHORT_CALL:
        for p in stock_range:
            profit = round(oq1.premium - max(0,p-oq1.strike_price),2)
            PNL.append(profit)

    if strategy == Strategy.SHORT_PUT:
        for p in stock_range:
            profit = round(oq1.premium - max(0, oq1.strike_price-p),2)
            PNL.append(profit)
            
    if strategy == Strategy.CREDIT_SPREAD:
        # Sell a PUT, and Buy a PUT at a lower strike price 
        if oq1.strike_price <= oq2.strike_price:
            raise Exception("Credit Spread, invalid strike prices")
        for p in stock_range:
            profit1 = round(oq1.premium-max(0,oq1.strike_price-p),2)
            profit2 = round(max(oq2.strike_price-p,0)-oq2.premium,2)
            PNL.append(round(profit1 + profit2, 2))

    if strategy == Strategy.CALENDAR_SPREAD:
        # Sell call with near expiration
        # Buy Call with further out expiration
        for p in stock_range:
            profit1 = round(oq1.premium - max(0,p-oq1.strike_price),2)
            profit2 = round(max(p-oq2.strike_price,0)-oq2.premium,2)
            PNL.append(round(profit1 + profit2, 2))

    if strategy == Strategy.IRON_CONDOR:
        # sell OTM put, Buy further OTM put,
        # Sell OTM call, Buy further OTM call
        if oq1.strike_price <= oq2.strike_price:
            raise Exception("Iron Condor, invalid put strike prices")
        if oq3.strike_price >= oq4.strike_price:
            raise Exception("Iron Condor, invalid call strike prices")
        for p in stock_range:
            profit1 = round(oq1.premium - max(0, oq1.strike_price - p),2)
            profit2 = round(max(0, oq2.strike_price -p) - oq2.premium,2)
            profit3 = round(oq3.premium-max(0,p-oq3.strike_price),2)
            profit4 = round(max(0,p-oq4.strike_price) - oq4.premium,2)
            PNL.append(round(profit1 + profit2 + profit3 + profit4, 2))

    if strategy == Strategy.COLLAR:
        # Sell call higher than current price
        # Buy Put lower then current price
        if oq1.strike_price <= oq2.strike_price:
            raise Exception("Collar, invalid put strike prices")
        for p in stock_range:
            profit1 = round(oq1.premium - max(0,p-oq1.strike_price),2)
            profit2 = round(max(oq1.strike_price-p,0)-oq1.premium,2)
            PNL.append(round(profit1 + profit2, 2))

    return stock_range, PNL

leg_settings = {
    'Call': {'nbr_legs':1, 'call_put':['call'], 'buy_write':['buy']},    
    'Put': {'nbr_legs':1, 'call_put':['put'], 'buy_write':['buy']},
    'Sell Call': {'nbr_legs':1, 'call_put':['call'], 'buy_write':['write']},
    'Sell Put': {'nbr_legs':1, 'call_put':['put'], 'buy_write':['write']},
    'Credit Spread': {'nbr_legs':2, 'call_put':['put','put'], 'buy_write':['write','buy']},
    'Iron Condor': {'nbr_legs':4, 'call_put':['call','call','put','put'], 'buy_write':['write','buy','write','buy']},
    'Calendar Spread': {'nbr_legs':2, 'call_put':['call','call'], 'buy_write':['write','buy']},
    'Collar': {'nbr_legs':2, 'call_put':['call','put'], 'buy_write':['write','buy']}}

def buy_sell_to_enum(buy_sell_str):
    if 'buy' in buy_sell_str.lower():
        buy_or_sell = BUY_OR_SELL.BUY
    else:
        buy_or_sell = BUY_OR_SELL.SELL
    return buy_or_sell

def calls_puts_to_enum(calls_puts_str):
    if 'call' in calls_puts_str.lower():
        calls_or_puts = CALL_OR_PUT.CALL
    else:
        calls_or_puts = CALL_OR_PUT.PUT
    return calls_or_puts

############################################################
#def show_profit_calcs(strike_list_item1, strike_list_item2, ticker, ticker_name, expiration_date, strategy, in_dollars):
def get_profit_calcs(optionsTrade, in_dollars):
    # strike_list_item has (strike_price, premium, iv)
    #TODO - put this in a pandas dataframe
    #columns are stock prices 200,202,204...240
    #indexes are DTE 30, 29, 28, ... 1
    #for a given DTE - vary the stock price to get options value
    # repeat for next DTE until DTE = 1
    # MAY need to optimize if DTE is large > 60 (do every 5,10,30 days)
    # CURRENTLY implemented for 1 DTE
    ot = optionsTrade # smaller variable name
    leg1 = ot.legs[0]
    oq1 = leg1.options_quote
    cur_stock_price = oq1.underlying_price
    strike_price1 = oq1.strike_price
    premium1 = oq1.premium
    # fix expiration date
    if 'Expiration' in oq1.expiration_date:
        oq1.expiration_date = oq1.expiration_date[12:]
    DTE = days_until_date(oq1.expiration_date)

    if oq1.call_or_put == CALL_OR_PUT.CALL:
        call = True 
    else:
        call = False
    # get sigma - a bit inefficient so need some refactoring!!!
    _, stock_ticker = get_current_stock_price(oq1.ticker_symbol)
    sigma1 = get_sigma(stock_ticker, oq1.expiration_date, oq1.strike_price, call)
    
    strike_price2 = None
    sigma2 = None
    premium2 = None
    if len(ot.legs) > 1:
        leg2 = ot.legs[1]
        oq2 = leg2.options_quote
        strike_price2 = oq2.strike_price
        premium2 = oq2.premium
        if oq2.call_or_put == CALL_OR_PUT.CALL:
            call = True 
        else:
            call = False
        # get sigma - a bit inefficient so need some refactoring!!!
        sigma2 = get_sigma(stock_ticker, oq2.expiration_date, oq2.strike_price, call)

    q = oq1.dividends
    if q == None:
        q = 0.0
    strategy = ot.strategy
    ticker_name = oq1.ticker_symbol
    expiration_date = oq1.expiration_date
    data = make_future_profits_table(strategy, ticker_name, 
            cur_stock_price, strike_price1, expiration_date, sigma1, q, premium1, 
            strike_price2, sigma2, premium2, 
            in_dollars)
    return data
   
def format_values(values, min_decimial_places = 0):
    # make it easier to display by shrinking sizes
    new_values = []
    for v in values:
        if v < 10:
            new_values.append(round(v,max(1,min_decimial_places)))
        else:
            if min_decimial_places == 0:
                new_values.append(round(v))
            else:
                new_values.append(round(v, min_decimial_places))
    return new_values

def make_future_profits_table(strategy, ticker_name, cur_stock_price, 
            strike_price1, expiration_date, sigma1, q, premium1, 
            strike_price2, sigma2, premium2, 
            in_dollars):

    output_table = {}
    DTE = days_until_date(expiration_date)
    # place holder for space for DTE
    #place_holder = 'DTE '
    #file.write(place_holder)

    # want rows to be decreasing DTE
    # want colums to be decreasing stock price

    t = make_profit_calcs_matrix(strategy, cur_stock_price, 
    strike_price1, DTE, interest_rate, sigma1, q, premium1, 
    strike_price2, sigma2, premium2, 
    in_dollars)

    # rotate table - expiration on columns, prices in rows
    t2 = rotate_table(t)
        # make the first row with is DTE
    output_table["days"] = [] 
    d = DTE

    while d > 0:
        formatted_string = f"{d:<8}"
        output_table["days"].append(formatted_string)
        d -= 1
    
    # now data section
    # format "data":[
    #  {'price': 478.0, 'data': [1.51, 1.53, 1.55, 1.57, 1.6, 1.62, 1.65, 1.68, 1.71, 1.75, 1.79, 1.83, 1.88, 1.93, 1.99, 2.06, 2.14, 2.23, 2.34, 2.48, 2.65, 2.87, 3.1]},
    output_table["data"] = [] 
    for row in t2:
        output_row = {}
        row = format_values(row,2) # decimal places minimum
        row[0] = round(row[0]) # stock price nearest integer
        output_row['price'] = row[0]
        output_row['data'] = []
        for p in row:
            formatted_string = f"{p:<8}" # Left-align, allocate 8 characters for each number
            output_row['data'].append(formatted_string)
        output_table["data"].append(output_row)
    return output_table


