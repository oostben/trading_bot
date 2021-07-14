import alpaca_trade_api as tradeapi
import numpy as np
from constants import *
from sqlalchemy import create_engine
import random
import pandas as pd
from datetime import datetime

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
    if TICKERS_SETTING == "best":
        return TICKERS_BEST

def write_predictions(predictions):
    data = [[p[0],p[1]] for p in predictions.items()]
    df = pd.DataFrame(data, columns = ['ticker', 'prediction'])
    df.to_sql('predictions', con=get_engine("trading_bot_db"), if_exists='replace')

def write_positions_to_db():
    api = tradeapi.REST()
    portfolio = api.list_positions()
    # if len(portfolio) > 0:
    data = [[p.symbol,p.qty] for p in portfolio]
    df = pd.DataFrame(data, columns = ['ticker', 'quantity'])
    df.to_sql('positions', con=get_engine("trading_bot_db"), if_exists='replace')

def write_last_time_updated():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y") + " "
    dt_string+= datetime.today().strftime("%I:%M %p")
    data = [dt_string]
    df = pd.DataFrame(data, columns = ['last_updated'])
    df.to_sql('last_updated', con=get_engine("trading_bot_db"), if_exists='replace')

def store_cash_val():
    cash_val = float(get_cash_val())
    data = [cash_val]
    df = pd.DataFrame(data, columns = ['cash_val'])
    df.to_sql('cash_val', con=get_engine("trading_bot_db"), if_exists='replace')
    return cash_val

def calculate_multiplier(cash_val, predictions):
    total_pred_val = 0
    for val in predictions.values():
        if val > 0: total_pred_val += val
    if total_pred_val > 0:
        return cash_val / total_pred_val
    else:
        return 0

def submit_orders(predictions,multiplier):
    api = tradeapi.REST()
    for key,val in predictions.items():
        if val > 0:
            api.submit_order(
                symbol=key,
                # qty=val*multiplier-.01,
                qty=1,
                side='buy',
                type='market',
                time_in_force='day'
            )