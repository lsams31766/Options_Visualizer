#options_profit_calculator
'''
  Calclate options profit over various strike prices and days into the future
  Use Black Sholes to predict the options price for thes parameters
'''
from datetime import date, timedelta
from model import Strategy
from blackscholes import BlackScholesCall, BlackScholesPut
import math
from scipy.stats import norm
from datetime import date, datetime

def calculate_option_prices(S, K, T, r, sigma, q):
    """
    Calculate the Black-Scholes option prices for European call and put options using the 'blackscholes' package.

    Parameters:
    S : float - current stock price
    K : float - strike price of the option
    T : float - time to maturity (in years)
    r : float - risk-free interest rate (annual as a decimal)
    sigma : float - volatility of the underlying stock (annual as a decimal)
    q : float - annual dividend yield (as a decimal)

    Returns:
    tuple - (call price, put price)
    """
    # Creating instances of BlackScholesCall and BlackScholesPut
    call_option = BlackScholesCall(S=S, K=K, T=T, r=r, sigma=sigma, q=q)
    put_option = BlackScholesPut(S=S, K=K, T=T, r=r, sigma=sigma, q=q)

    # Get call and put prices
    call_price = call_option.price()
    put_price = put_option.price()

    return call_price, put_price

def black_scholes_delta(S, K, T, r, sigma, option_type='call'):
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

    if option_type == 'call':
        delta = norm.cdf(d1)
    elif option_type == 'put':
        delta = norm.cdf(d1) - 1
    else:
        raise ValueError("option_type must be 'call' or 'put'")

    return delta



#define what range of strike prices to calculate
NBR_PRICES_BELOW_TO_SHOW = 10 # 10 below, given price, 10 above
def get_prices_to_calc(cur_stock_price):
    # return list of prices to show
    prices = []
    interval = 1
    if cur_stock_price <= 1:
        interval =  0.1
    if cur_stock_price <= 100:
        interval = 1
    if cur_stock_price <= 500:
        interval = 3
    interval = 2
    
    cur = round(cur_stock_price, interval)
    cur = cur - (interval * NBR_PRICES_BELOW_TO_SHOW)
    for _ in range(NBR_PRICES_BELOW_TO_SHOW):
        prices.append(cur)
        cur += interval
    prices.append(cur_stock_price)
    cur = cur_stock_price + interval
    for _ in range(NBR_PRICES_BELOW_TO_SHOW):
        prices.append(cur)
        cur += interval
    
    # reverse the list want how to low
    prices = prices[::-1]
    return prices

def get_dates_until(end_date_str):
    """
    Gets all dates from today until the specified end date (inclusive).

    Args:
        end_date_str (str): The end date in 'YYYY-MM-DD' format.
    """
    today = date.today()
    dates = []
    try:
        end_date = date.fromisoformat(end_date_str)
    except ValueError:
        print("Invalid date format. Please use 'YYYY-MM-DD'.")
        return

    if end_date < today:
        print("The end date must be in the future.")
        return

    current_date = today
    while current_date <= end_date:
        dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)
    return dates

# Example usage:
# To print dates from today until October 25, 2025
# d = get_dates_until("2025-10-25") 
# print(d)

# test for various stock prices
# prices = get_prices_to_calc(499)
# print(prices)

def get_future_options_values(strategy, cur_stock_price, strike_price,
        DTE, interest_rate, sigma, q, premium, in_dollars=True):
    # use blacksholes model to get option values accross strike prices
    # and dates up to DTE (days to expire)
    #TODO - 2 modes
    # mode a: output value = Calculated  - Paid (PROFIT or LOSS in $)
    # mode b: output value = 100 * (calculated - paid )/ paid (PNL in %)

    prices = get_prices_to_calc(cur_stock_price)
    S = cur_stock_price
    K = strike_price
    T = float(DTE)/365.0
    r = interest_rate
    if strategy == Strategy.LONG_CALL:
        # for now just get values for stock price range
        values = []
        for p in prices:
            call_price, _ = calculate_option_prices(p,K,T,r,sigma,q)
            # as per mode calculate profit
            if in_dollars == True:
                pnl = call_price - premium
            else: # percent pnl
                pnl = 100 * ((call_price - premium)/premium)
            values.append(pnl)

    if strategy == Strategy.LONG_PUT:
        # for now just get values for stock price range
        values = []
        for p in prices:
            _, put_price = calculate_option_prices(p,K,T,r,sigma,q)
            # as per mode calculate profit
            if in_dollars == True:
                pnl = put_price - premium
            else: # percent pnl
                pnl = 100 * (( put_price - premium)/premium)
            values.append(pnl)

    if strategy == Strategy.SHORT_CALL:
        # for now just get values for stock price range
        values = []
        for p in prices:
            call_price, _ = calculate_option_prices(p,K,T,r,sigma,q)
            # as per mode calculate profit
            if in_dollars == True:
                pnl = premium - call_price
            else: # percent pnl
                pnl = 100 * ((premium - call_price)/premium)
            values.append(pnl)

    if strategy == Strategy.SHORT_PUT:
        # for now just get values for stock price range
        values = []
        for p in prices:
            _, put_price = calculate_option_prices(p,K,T,r,sigma,q)
            # as per mode calculate profit
            if in_dollars == True:
                pnl = premium - put_price
            else: # percent pnl
                pnl = 100 * ((premium - put_price)/premium)
            values.append(pnl)        

    return prices,values


def make_profit_calcs_matrix(strategy, cur_stock_price, 
        strike_price1, DTE, interest_rate, sigma1, q, premium1, 
        strike_price2, sigma2, premium2, 
        in_dollars=True):
    profit_calc_matrix = []
    # add prices as first row
    DTE_cur = DTE
    if strategy == Strategy.CREDIT_SPREAD:
        prices,_ = get_future_options_values(Strategy.SHORT_PUT, cur_stock_price, strike_price1,
        DTE_cur, interest_rate, sigma1, q, premium1, True)
        profit_calc_matrix.append(prices)
        temp_table1 = []
        temp_table2 = []
        # Get the SELL PUT option prices
        while DTE_cur > 0:
            _,values = get_future_options_values(Strategy.SHORT_PUT, cur_stock_price, strike_price1,
            DTE_cur, interest_rate, sigma1, q, premium1, True)
            temp_table1.append(values)
            DTE_cur = DTE_cur - 1
        # Get the BUY PUT option prices
        DTE_cur = DTE
        while DTE_cur > 0:
            _,values = get_future_options_values(Strategy.LONG_PUT, cur_stock_price, strike_price2,
            DTE_cur, interest_rate, sigma2, q, premium2, True)
            temp_table2.append(values)
            DTE_cur = DTE_cur - 1
        # combine the tables into profit_calc_matrix
        r = 0
        c = 0
        row_length = len(temp_table1[0])
        for r in range(len(temp_table1)):
            new_row = []
            for c in range(row_length):
                if in_dollars == True:
                    new_row.append(temp_table1[r][c] + temp_table2[r][c])
                else: 
                    pdiff = premium1 - premium2
                    pnl = temp_table1[r][c] + temp_table2[r][c]
                    profit = 100.0 * pnl / pdiff
                    new_row.append(profit)
            profit_calc_matrix.append(new_row)
    else:
        prices,_ = get_future_options_values(strategy, cur_stock_price, strike_price1,
        DTE_cur, interest_rate, sigma1, q, premium1, in_dollars)
        profit_calc_matrix.append(prices)
        # add values as subsequent rows
        while DTE_cur > 0:
            _,values = get_future_options_values(strategy, cur_stock_price, strike_price1,
            DTE_cur, interest_rate, sigma1, q, premium1, in_dollars)
            profit_calc_matrix.append(values)
            DTE_cur = DTE_cur - 1
    return profit_calc_matrix


def combine_prices_and_values(prices,values):
    combined = []
    for i in range(len(prices)):
        combined.append((prices[i],values[i]))
    return combined

def make_dte_value_dict(DTE, prices, values):
    dte_dict = {}
    # dictionary, key is DTE, value is list of tuples (strike_price,value)
    for day in range(DTE):
        new_dte = DTE - day
        prices, values = get_future_options_values(Strategy.LONG_CALL,
                S,K,new_dte,r,sigma,q)
        dte_dict[day] = combine_prices_and_values(prices,values)
    return dte_dict

def rotate_table(t):
    row_length = len(t[0])
    col_length = len(t)
    output_table = []
    for _ in range(row_length):
        new_row = [0 for _ in range(col_length)]
        output_table.append(new_row)
    r = 0
    c = 0
    for row in t:
        for value in row:
            cur_row = output_table[r]
            cur_row[c] = value
            r += 1
        # finished a row
        r = 0
        c += 1
    return output_table

# TSLA 4 days to expiration CALL
# S = 435
# K = 435
# T = 4.0/365.0
# r = 0.004
# sigma = 0.558
# q = 0
# call_price, put_price = calculate_option_prices(S,K,T,r,sigma,q)
# print("TSLA Call Price: {:.6f}, Put Price: {:.6f}".format(call_price, put_price))

# S = 435 # current stock price
# K = 425 # strike price bought at
# DTE = 21 # days to expire
# r = 0.00425 # interest rate
# sigma = 0.64 # Implied Volaitlity - LOOK THIS UP!
# q = 0 # dividend - LOOK THIS UP!
# prices, values = get_future_options_values(Strategy.LONG_PUT,
#             S,K,DTE,r,sigma,q)
# for i in range(len(prices)):
#     print(prices[i],values[i])

# we also want for various DTE's - dict of DTE and strike prices/values
# dte_dict = make_dte_value_dict(DTE,prices,values)

# for key,value in dte_dict.items():
#     print(key,':')
#     print(value)

# in reality we will have a price we bought the option at
# then we will add/subtract the calcualted value to get profit
