import alpaca_trade_api as tradeapi
import numpy as np
from constants import *
from sqlalchemy import create_engine
import random

def get_engine(dbName):
    return create_engine("postgresql://"+DB_USERNAME+":"+DB_PASSWORD+"@"+DB_URL +":"+DB_PORT+ "/" + dbName)

def shuffle_data(x,y):
    c = list(zip(x,y))
    random.shuffle(c)
    x, y = zip(*c)
    x = list(x)
    y= list(y)
    return x,y

def even_out_data(x,y):
    good = 0
    bad = 0
    badi = []
    for i,temp in enumerate(y):
        if temp < 0: 
            bad +=1
            badi.append(i)
        else: good +=1
    # print(badi)
    for i in range(good-bad):
        x.pop(badi[-1])
        y.pop(badi[-1])
        badi.pop(-1)
    return x,y

def val_split(x,y,percent=20):
    l = int(len(x) * (percent / 100))
    x_train = x[:-l]
    y_train = y[:-l]
    x_validation= x[-l:]
    y_validation = y[-l:]
    return x_train, y_train, x_validation, y_validation

def get_bars(ticker_in, timeframe_in='day', limit_in=600):
    api = tradeapi.REST()
    barset = api.get_barset(ticker_in, timeframe_in, limit=limit_in).df
    bars = barset[ticker_in]
    print("got ", ticker_in)
    return bars

def print_positions():
    api = tradeapi.REST()
    portfolio = api.list_positions()
    for position in portfolio:
        print("{} shares of {}".format(position.qty, position.symbol))

def liquidate_positions():
    api = tradeapi.REST()
    portfolio = api.list_positions()
    for position in portfolio:
        api.submit_order(
            symbol=position.symbol,
            qty=position.qty,
            side='sell',
            type='market',
            time_in_force='gtc'
        )

def get_cash_val():
    api = tradeapi.REST()
    account = api.get_account()
    return account.cash


def node_already_exists(root_in, name_in):
    q = [root_in]
    while len(q) > 0:
        curr_node = q.pop(0)
        if curr_node.name == name_in:
            return True
        q.extend(curr_node.children)
    return False

def normalize_list(lis_in):
    return lis_in / max(lis_in)

def get_sp_500_tickers():
    file1 = open('s&p500.txt', 'r')
    lines = file1.readlines()
    ret = []
    for line in lines:
        ret.append(line.strip())
    print(ret)
    return ret

def get_tickers():
    if TICKERS_SETTING == "500":
        return get_sp_500_tickers()
    if TICKERS_SETTING == "small":
        return TICKERS_SMALL
    if TICKERS_SETTING == "large":
        return TICKERS_LARGE