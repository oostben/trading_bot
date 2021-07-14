from network import *
import alpaca_trade_api as tradeapi
import pandas as pd
from helpers import *
from update_data_db import *
from data_loader import data_loader

#make sure data exists in RDS
update_data_db()

#get x,y and dict for actually making the predictions for tommorrow
x,y, dict_for_predictions = data_loader()

#shuffle the data
x,y = shuffle_data(x,y)

#even out data so it's a 50 50 split between stocks moving up/down
x,y = even_out_data(x,y)

#split out validation and trianing
x_train, y_train, x_validation, y_validation = val_split(x,y, percent=10)

#get number of indicators we are using to set the first layer of the net
num_inds = len(x[0])

#initalize the network
net = Network(num_inds, activation=torch.nn.ReLU(), learning_rate_in=LR)

#trian network
net.train_model(x_train,y_train,x_validation,y_validation,epochs=EPOCHS)

# get predictions
predictions = {}
for ticker in get_tickers():
    y_pred = net.predict(dict_for_predictions[ticker])
    predictions[ticker] = y_pred

#sort predictions
predictions = dict(reversed(sorted(predictions.items(), key=lambda item: item[1])))

#write predictions to DB
write_predictions(predictions)

#store the time now for last updated time on website
write_last_time_updated()

#liquidate the old positions
liquidate_positions()

#store the cash value for the website
cash_val = store_cash_val()

# calculate multiplier for position sizing
multiplier = calculate_multiplier(cash_val,predictions)

if multiplier > 0:
    submit_orders(predictions, multiplier)

#write the positions to the db for website
write_positions_to_db()