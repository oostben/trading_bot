from tree import *
from network import *
import time
import alpaca_trade_api as tradeapi



# tickers = ["BA","AAPL"]
tickers = ["BA", "TSLA", "SCI", "WM", "ACB", "NVDA", "BABA","MSFT","ACN","AAL","T","BAC"]
# tickers = get_sp_500_tickers()

tree = Tree(tickers)

for i in range(2,20,5):
    tree.add_sma(length_in=i)
    tree.add_rsi(length_in=i)
    tree.add_roc(length_in=i)
for i in range(2,50,5):
    for j in range(2,5):
        if j >= i: continue
        tree.add_gc(fast_in=i,slow_in=j)

tree.update()

x_train,y_train = tree.get_data_for_network(length_in=2)

keys = list(x_train.keys())
num_inds = len(x_train[keys[0]][0])
x = []
y = []
for key in keys:
    x.extend(x_train[key])
    y.extend(y_train[key]/max(y_train[key][:-100]))

net = Network(num_inds, activation=torch.nn.ReLU(), learning_rate_in=.001)
net.train_model(x,y,epochs=20)

data = tree.get_indicator_data(stocks_in=tickers,length_in=1)

predictions = {}

for ticker in tickers:
    y_pred = net.predict(data[ticker][-1])
    predictions[ticker] = y_pred

print(predictions)
liquidate_positions()
time.sleep(10)
cash_val = float(get_cash_val())

total_pred_val = 0
keys = list(predictions.keys())

for key in keys:
    total_pred_val += abs(predictions[key])

multiplier = cash_val / total_pred_val

api = tradeapi.REST()
for key in keys:
    if predictions[key] > 0:
        api.submit_order(
            symbol=key,
            qty=predictions[key]*multiplier,
            side='buy',
            type='market',
            time_in_force='gtc'
        )