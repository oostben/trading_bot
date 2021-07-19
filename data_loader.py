from helpers import get_tickers
import pandas as pd
from helpers import get_engine



class Data_Loader:
    def __init__(self,val_percent):
        self.val_percent = val_percent
    def load(self,):
        dict_for_predictions = {}
        x,y = [],[]
        for ticker in get_tickers():
            print("loading ", ticker)
            #get data from db
            df = pd.read_sql_query('select * from  trading_data where ticker = ' + "\'" + ticker + "\'", get_engine("trading_bot_db"))
            #drop the incomplete rows (some indicators can't be computed at all ticks)
            df.dropna(inplace= True)
            df.dropna(axis='columns',inplace= True)
            
            df = pd.concat((df, pd.get_dummies(df['index'].dt.weekday)), axis=1)
            skip = ['index','ticker','std','pct_change']
            #Normalize columns
            # for column in df:
            #     if column in skip: continue
            #     df[column] = df[column] / (max(abs(min(df[column])),abs(max(df[column]))) + .0000001)
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
                objective = df.loc[i+1,'pct_change']
                del temp['price']
                del temp['level_0']
                x.append(list(temp))
                y.append(objective)

        x,y = self.even_out_data(x,y)
        self.x_train, self.y_train, self.x_validation, self.y_validation = self.val_split(x,y,percent = self.val_percent)
        self.dict_for_predictions = dict_for_predictions
        return self.x_train, self.y_train, self.x_validation, self.y_validation, self.dict_for_predictions 

    def val_split(self,x,y,percent=20):
        l = int(len(x) * (percent / 100))
        x_train = x[:-l]
        y_train = y[:-l]
        x_validation= x[-l:]
        y_validation = y[-l:]
        return x_train, y_train, x_validation, y_validation

    def even_out_data(self,x,y):
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
        