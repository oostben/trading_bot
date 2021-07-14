import os
from constants_private import *
TICKERS_LARGE = ["BA", "TSLA", "SCI", "WM", "ACB", "NVDA", "BABA","MSFT","ACN","AAL","T","BAC","HRL","HST","HWM","HPQ","HUM","HBAN","HII","IT","IEX","IDXX","INFO"]
TICKERS_SMALL = ["BA"]
TICKERS_BEST = ["AFRM", "UBER", "PLTR", "BA", "BABA", "TSLA", "WM", "ACB", "NVDA", "GME", "JACK", "KO", "AAL", "MCD", "BAC","MSFT", "GOOGL", "F", "FB", "SCI", "GPS", "COF","XOM", "RKT"]
TICKERS_SETTING = "best"

PLOTS_PATH = os.path.join(".","plots")
EPOCHS = 1
LR = .001
# LR = .0001
