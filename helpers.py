import alpaca_trade_api as tradeapi
import numpy as np

def get_bars(ticker_in, timeframe_in='day', limit_in=1000):
    api = tradeapi.REST()
    barset = api.get_barset(ticker_in, timeframe_in, limit=limit_in)
    bars = barset[ticker_in]
    return bars

def node_already_exists(root_in, name_in):
    q = [root_in]
    while len(q) > 0:
        curr_node = q.pop(0)
        if curr_node.name == name_in:
            return True
        q.extend(curr_node.children)
    return False
