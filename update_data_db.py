import talib
from talib.abstract import *
from helpers import *
import pandas as pd
from sqlalchemy import create_engine

def update_data_db():
    ranges = [2,4,6,10,15]
    data_to_write =pd.DataFrame()
    for ticker in get_tickers():
        bars = get_bars(ticker)
        full = pd.DataFrame(index=bars.index)
        full["ticker"] = ticker
        full['price'] = bars['close']

        for i in range(len(ranges)):
            for j in range(i+1,len(ranges)):
                t1 = SMA(bars, timeperiod=ranges[i])
                t2 = SMA(bars, timeperiod=ranges[j])
                full['GC_' + str(ranges[i]) + "_"+ str(ranges[j])]= (t1-t2)
                full['PPO_' + str(ranges[i]) + "_"+ str(ranges[j])] = PPO(bars,fastperiod=ranges[i],slowperiod=ranges[j],matype=0)
            full['ADX'] = ADX(bars, timeperiod=ranges[i])
            full['ADXR'] = ADXR(bars, timeperiod=ranges[i])
            full['CMO'] = CMO(bars, timeperiod=ranges[i])
            full['CCI'] = CCI(bars, timeperiod=ranges[i])
            full['DX'] = DX(bars, timeperiod=ranges[i])
            full['MFI'] = MFI(bars, timeperiod=ranges[i])
            full['MOM'] = MOM(bars, timeperiod=ranges[i])
            full['ROC'] = ROC(bars, timeperiod=ranges[i])
            full['ROCP'] = ROCP(bars, timeperiod=ranges[i])
            full['RSI'] = RSI(bars, timeperiod=ranges[i])
            full['NATR'] = NATR(bars, timeperiod=ranges[i])
        data_to_write = data_to_write.append(full)
    data_to_write.to_sql('trading_data', con=get_engine("trading_bot_db"), if_exists='replace')
    
# update_data_db()