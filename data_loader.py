from helpers import get_tickers
import pandas as pd
from helpers import get_engine
def data_loader():
    dict_for_predictions = {}
    x,y = [],[]
    for ticker in get_tickers():
        #get data from db
        df = pd.read_sql_query('select * from  trading_data where ticker = ' + "\'" + ticker + "\'", get_engine("trading_bot_db"))
        #drop the incomplete rows (some indicators can't be computed at all ticks)
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
        for i in range(len(df)-2):
            temp = df.loc[i]
            del temp['index']
            del temp['ticker']
            cur_price = df.loc[i+1,'price']
            next_price = df.loc[i+2,'price']
            objective = next_price - cur_price
            del temp['price']
            del temp['level_0']
            x.append(list(temp))
            y.append(objective)
    return x,y,dict_for_predictions