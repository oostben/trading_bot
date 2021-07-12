from network import *
import alpaca_trade_api as tradeapi
import pandas as pd
from sqlalchemy import create_engine
from helpers import *
from update_data_db import *
from update_positions_db import *

update_data_db()

dict_for_predictions = {}
x,y = [],[]
for ticker in get_tickers():
    #get data from db
    df = pd.read_sql_query('select * from  trading_data where ticker = ' + "\'" + ticker + "\'", get_engine("trading_bot_db"))
    df.dropna(inplace= True)
    df.dropna(axis='columns',inplace= True)
    
    #Normalize columns
    for column in df:
        if column == 'index' or column == 'ticker': continue
        df[column] = df[column] / (max(abs(min(df[column])),abs(max(df[column]))) + .0000001)

    #store most recent datapoint for prediction of tommorrow
    most_recent = df.iloc[-1]
    del most_recent['index']
    del most_recent['ticker']
    del most_recent['price']
    dict_for_predictions[ticker] = list(most_recent)
    
    #create x and y
    df =df.reset_index()
    for i in range(len(df)-1):
        temp = df.loc[i]
        del temp['index']
        del temp['ticker']
        cur_price = df.loc[i,'price']
        next_price = df.loc[i+1,'price']
        objective = next_price - cur_price
        del temp['price']
        del temp['level_0']
        x.append(list(temp))
        y.append(objective)

x,y = shuffle_data(x,y)
x,y = even_out_data(x,y)
x_train, y_train, x_validation, y_validation = val_split(x,y, percent=10 )
num_inds = len(x[0])
net = Network(num_inds, activation=torch.nn.ReLU(), learning_rate_in=LR)
net.train_model(x_train,y_train,x_validation,y_validation,epochs=EPOCHS)

predictions = {}
for ticker in get_tickers():
    y_pred = net.predict(dict_for_predictions[ticker])
    predictions[ticker] = y_pred

#sort predictions
predictions = dict(reversed(sorted(predictions.items(), key=lambda item: item[1])))

data = [[p[0],p[1]] for p in predictions.items()]
df = pd.DataFrame(data, columns = ['ticker', 'prediction'])
df.to_sql('predictions', con=get_engine("trading_bot_db"), if_exists='replace')

liquidate_positions()
cash_val = float(get_cash_val())

data = [cash_val]
df = pd.DataFrame(data, columns = ['cash_val'])
df.to_sql('cash_val', con=get_engine("trading_bot_db"), if_exists='replace')

total_pred_val = 0
for key,val in predictions.items():
    if val > 0: total_pred_val += val

multiplier = cash_val / total_pred_val

api = tradeapi.REST()
for key,val in predictions.items():
    if val > 0:
        api.submit_order(
            symbol=key,
            qty=val*multiplier-.01,
            side='buy',
            type='market',
            time_in_force='day'
        )

write_positions_to_db()