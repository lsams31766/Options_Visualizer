#!/usr/bin/python3
import sys
import logging as l
from functools import wraps
from io import StringIO
import os
import operator

from api import get_strategies, get_ticker_quote, \
  list_expiration_dates, list_options_chain, get_pnl
from model import *

#from models import *
#from presentation import *
#from queries_and_filters import get_all_attributes, get_assoc_constructed_attribute, apply_filter, check_env_switched

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#DEFAULT_USER = 'samuell3'
#APP_LOG_PATH = os.path.join(BASE_DIR, 'logs', 'app.log')
#LOG_LEVEL = l.INFO

# def setupLogger(name, logFile, formatter, level=LOG_LEVEL):
#     handler = l.FileHandler(logFile)
#     handler.setFormatter(formatter)
#     logger = l.getLogger(name)
#     logger.setLevel(level)
#     logger.addHandler(handler)
#     return logger

# appLog = setupLogger('appInfo', APP_LOG_PATH, l.Formatter('%(asctime)s: %(levelname)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S"))


from flask import Flask, render_template, request, jsonify, url_for, redirect, g, abort, send_file, Response
from flask_cors import CORS, cross_origin

import traceback

cur_stock_ticker = None
cur_exp_date = None

app = Flask(__name__)
CORS(app)

# @app.before_request
# def auth():
#     g.user = str(request.headers.get('Smuid'))

@app.route('/', methods=['GET'])
def index():
    print("### index ###")
    return render_template('index.html')

@app.route('/getStrategies', methods=['GET'])
def getStrategies():
    print("### Get Strategies ###")
    s = get_strategies()
    elements = [item[1] for item in s]
    print(elements)
    try:
        return jsonify({
                "items": elements
        })
    except:
        print("ERROR serializaing strategies")
        return jsonify({
                "items": []
        })
    

@app.route('/getPrice', methods=['POST'])
def getPrice():
    global cur_stock_ticker
    print("### getPrice ###")
    content = request.json
    tickerSymbol = content['ticker_symbol']
    price, stockTicker = get_ticker_quote(tickerSymbol)
    cur_stock_ticker = stockTicker
    return jsonify({
            "item": price
    })

@app.route('/getExpirationDates', methods=['POST'])
def getExpirationDates():
    print("### getExpirationDates ###")
    content = request.json
    tickerSymbol = content['ticker_symbol'] # not needed unless js stores the object
    expDates = list_expiration_dates(cur_stock_ticker)
    return jsonify({
            "items": expDates
    })

@app.route('/getOptionsChain', methods=['POST'])
def getOptionsChain():
    print("### getOptionsChain ###")
    try:
        #raw_data = request.data.decode('utf-8') 
        #print(raw_data)
        data = request.get_json(force=True)
        ticker_symbol = data['ticker_symbol']
        exp_date = data['exp_date']
        calls_or_puts = data['calls_or_puts']
        print('ticker_symbol:',ticker_symbol,'exp_date:',exp_date, 
              'call_or_puts:',calls_or_puts)
    except Exception as e:
        print("NO CONTENT",e)
        return jsonify({
             "data": []
         })
    # output_list = []
    _, stock_ticker =  get_ticker_quote(ticker_symbol)
    chain = list_options_chain(stock_ticker, exp_date)
    # COMBINE Calls and Puts on same line - only strike in CALLS
    # need to add STRIKE, PREMIUM and DELTA to the data
    output_list = []
    for item in chain[calls_or_puts]:
        strike = item[0]
        premium = item[1]
        delta = item[2]
        row = {'STRIKE':strike, 'PREMIUM':premium, 'DELTA':delta}
        output_list.append(row)
    # print(output_list)
    return jsonify({
            "data": output_list
    })

def extract_nbr(s):
    # find first number or decimal in string
    pos = -1
    for i, c in enumerate(s):
        if c.isdigit():
            pos = i
            break 
    if pos == -1:
        return 0
    rest_of_str = s[pos:]
    if '.' in rest_of_str:
        return float(rest_of_str)
    else:
        return int(rest_of_str)


# get_pnl
@app.route('/getPnlTable', methods=['POST'])
def getPnlTable():
    print("### getPnlTable ###")
    # data payload must include:
    #   exp_date1, calls_or_puts1, strike_price1, premium1, strategy
    #   cur_stock_price, buy_or_sell
    try:
        raw_data = request.data.decode('utf-8') 
        print("raw_data",raw_data)
        data = request.get_json(force=True)
        print("data",data)
        # todo allow multiple legs
        exp_date1 = data['exp_date1']
        calls_or_puts1 = data['calls_or_puts1']
        if 'call' in calls_or_puts1.lower():
            calls_or_puts1 = CALL_OR_PUT.CALL
        else:
            calls_or_puts1 = CALL_OR_PUT.PUT
        # need to clean up some items
        strike_price1 = extract_nbr(data['strike_price1'])
        premium1 = extract_nbr(data['premium1'])
        strategy = data['strategy']
        strategy = strategy_str_to_obj(strategy)
        cur_stock_price = extract_nbr(data['cur_stock_price'])
        buy_or_sell = data['buy_or_sell']
        if 'buy' in buy_or_sell.lower():
            buy_or_sell = BUY_OR_SELL.BUY
        else:
            buy_or_sell = BUY_OR_SELL.SELL
        print('Cleaned values',strike_price1,premium1,cur_stock_price)
        print('exp_date1:',exp_date1,'calls_or_puts1:',calls_or_puts1,
              'premium1:',premium1, 'strategy:',strategy)
    except Exception as e:
        print("NO CONTENT",e)
        return jsonify({
             "data": []
         })
    # make an optionsTrade object, get the pnl, return to caller
    q = OptionsQuote()
    # TODO allow for multiple legs
    q.expiration_date = exp_date1
    q.call_or_put = calls_or_puts1
    q.strike_price = strike_price1
    q.premium = premium1
    q.underlying_price = cur_stock_price
    oLeg = OptionsLeg()
    oLeg.buy_or_sell = buy_or_sell
    oLeg.options_quote = q 
    oTrade = OptionsTrade()
    oTrade.legs = [oLeg] # assume 1 leg for now
    oTrade.strategy = strategy
    pnl_table = get_pnl(oTrade)
    # print(output_list)
    return jsonify({
            "data": pnl_table
    })


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=8001, debug=True)

    # s = 'Strike: 25'
    # f = extract_nbr(s)
    # print(f)
    # AAPL exp_date: 2025-12-05
    # FOR TESTING
    # _, stock_ticker =  get_ticker_quote('AAPL')
    # chain = list_options_chain(stock_ticker, '2025-12-05')
    # output_list = []
    # for item in chain['CALLS']:
    #     strike = item[0]
    #     premium1 = item[1]
    #     delta1 = item[2]

    #     row = {'STRIKE':strike, 'PREMIUM1':premium1, 
    #            'DELTA1':delta1,}
    #     output_list.append(row)
    # for ol in output_list:
    #     print(output_list)
    ###
    # q = OptionsQuote()
    # q.expiration_date = '2025-12-05'
    # q.call_or_put = CALL_OR_PUT.CALL
    # q.strike_price = chain['CALLS'][22][0]
    # q.premium = chain['CALLS'][22][1]
    # tickerSymbol = 'AAPL'
    # price, stockTicker = get_ticker_quote(tickerSymbol)
    # q.underlying_price = price
    # oLeg = OptionsLeg()
    # oLeg.buy_or_sell = BUY_OR_SELL.BUY
    # oLeg.options_quote = q 
    # oTrade = OptionsTrade()
    # oTrade.legs = [oLeg] # assume 1 leg for now
    # oTrade.strategy = Strategy.LONG_CALL
    # pnl_table = get_pnl(oTrade)
    # for line in pnl_table:
    #     print(line)

    
 
