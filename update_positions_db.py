import alpaca_trade_api as tradeapi
import pandas as pd
from helpers import *

def write_positions_to_db():
    api = tradeapi.REST()
    portfolio = api.list_positions()
    data = [[p.symbol,p.qty] for p in portfolio]
    df = pd.DataFrame(data, columns = ['ticker', 'quantity'])
    df.to_sql('positions', con=get_engine("trading_bot_db"), if_exists='replace')
write_positions_to_db()