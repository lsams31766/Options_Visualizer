#model.py

from enum import Enum, auto 

# Options Strategies
class Strategy(Enum):
    LONG_CALL = auto()
    LONG_PUT = auto()
    SHORT_CALL = auto()
    SHORT_PUT = auto()
    CREDIT_SPREAD = auto()
    IRON_CONDOR = auto()
    CALENDAR_SPREAD = auto()
    COLLAR = auto()

all_strategies = [Strategy.LONG_CALL, Strategy.LONG_PUT,
    Strategy.SHORT_CALL, Strategy.SHORT_PUT,
    Strategy.CREDIT_SPREAD, Strategy.IRON_CONDOR,
    Strategy.CALENDAR_SPREAD, Strategy.COLLAR]

def get_strategy_str(strategy):
    # return string name of strategy
    if strategy == Strategy.LONG_CALL:
        return 'Call'
    elif strategy == Strategy.LONG_PUT:
        return 'Put'
    elif strategy == Strategy.SHORT_CALL:
        return 'Sell Call'
    elif strategy == Strategy.SHORT_PUT:
        return 'Sell Put'
    elif strategy == Strategy.CREDIT_SPREAD:
        return 'Credit Spread'
    elif strategy == Strategy.IRON_CONDOR:
        return 'Iron Condor'
    elif strategy == Strategy.CALENDAR_SPREAD:
        return 'Calendar Spread'
    elif strategy == Strategy.COLLAR:
        return 'Collar'
    else:
        return 'Unknown Strategy'    
    

# Options Strategies
class CALL_OR_PUT(Enum):
    CALL = auto()
    PUT = auto()

class BUY_OR_SELL(Enum):
    BUY = auto()
    SELL = auto()

class OptionsQuote:
    ticker_symbol = '' # abbreviation for name of ticker symbol
    yf_ticker = None # the data received from a yfinance call to the ticker
    expiration_date = None # the date of expiration in the form YYYY-MM-DD
    days_to_expire = 0 # the numeric value of days to expiration
    strike_price = 0 # Strike Price in Dollars
    underlying_price = 0 # Current stock or underlying asset price
    premium = 0 # premium paid/received for the option at initiation
    sigma = 0 # the Implied Volatility of the option at initiation
    divedends = 0 # dividends paid on option
    delta = 0 # calculated deleta
    call_or_put = CALL_OR_PUT.CALL # For a put CALL_OR_PUT.PUT

class OptionsChainItem:
    expriation_date = None # format YYYY-MM-DD
    call_or_put = CALL_OR_PUT.CALL # For a put CALL_OR_PUT.PUT
    strike_price = 0 # in dollars
    delta = 0 # as a decimal

class OptionsChain:
    CallStrikes = [] # this will hold OptionsChainItems that are calls
    PutStrikes = [] # this will hold OptionsChainItems that are puts

class OptionsLeg:
    buy_or_sell = BUY_OR_SELL.BUY # for sell it is BUY_OR_SELL.SELL
    options_quote = None # an OptionsQuote object

class OptionsTrade:
    strategy = None # one of the Strategy enums
    legs = [] # 1 or more OptionsLeg items