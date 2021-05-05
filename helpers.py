import alpaca_trade_api as tradeapi
import numpy as np

def get_bars(ticker_in, timeframe_in='day', limit_in=600):
    api = tradeapi.REST()
    barset = api.get_barset(ticker_in, timeframe_in, limit=limit_in)
    bars = barset[ticker_in]
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

