import alpaca_trade_api as tradeapi

api = tradeapi.REST()

# Get daily price data for AAPL over the last 5 trading days.
barset = api.get_barset('AAPL', 'day', limit=1000)
aapl_bars = barset['AAPL']
print(aapl_bars[0])
# See how much AAPL moved in that timeframe.
week_open = aapl_bars[0].o
week_close = aapl_bars[-1].c
percent_change = (week_close - week_open) / week_open * 100

print(percent_change)
