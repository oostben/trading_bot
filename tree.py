from node import *

class Tree:
    def __init__(self, tickers_in):
        self.root = Root()
        for ticker in tickers_in:
            self.add_stock(ticker)
        self.update()
        self.offset = 0

    def add_stock(self, symbol_in):
        Ticker(root_in=self.root,symbol_in=symbol_in)

    def update(self):
        q = [self.root]
        while len(q) > 0:
            curr_node = q.pop(0)
            curr_node.reset_update()
            for child in curr_node.children:
                q.append(child)

        q = [self.root]
        while len(q) > 0:
            curr_node = q.pop(0)
            if not curr_node.ready_to_be_updated():
                q.append(curr_node)
                continue
            curr_node.update()
            for child in curr_node.children:
                q.append(child)
    
    def add_sma(self,length_in):
        for stock in self.root.children:
            SMA(root_in=self.root, symbol_in=stock.get_name(),length_in=length_in)
        self.offset = max(self.offset, length_in)
    
    def add_rsi(self,length_in):
        for stock in self.root.children:
            RSI(root_in=self.root, symbol_in=stock.get_name(),length_in=length_in)
        self.offset = max(self.offset, length_in)
    
    def add_roc(self,length_in):
        for stock in self.root.children:
            ROC(root_in=self.root, symbol_in=stock.get_name(),length_in=length_in)
        self.offset = max(self.offset, length_in)
    
    def add_gc(self,fast_in,slow_in):
        for stock in self.root.children:
            GC(root_in=self.root, symbol_in=stock.get_name(),fast_in=fast_in,slow_in=slow_in)
        self.offset = max(self.offset, max(fast_in, slow_in))


    def print_tree_names(self):
        q = [self.root, "sentinal"]
        while(len(q) > 0):
            curr_node = q.pop(0)
            if curr_node == "sentinal" and len(q) != 0:
                print()
                q.append("sentinal")
            elif curr_node != "sentinal":
                print(curr_node.name, "-->", end=' ')
                print(len(curr_node.timeseries), end='\n')
                for child in curr_node.children:
                    q.append(child)

    def get_indicator_data(self, stocks_in=[], length_in=1):
        data = {}
        if len(stocks_in) == 0:
            stocks_in = self.get_tickers()
        
        for stock_ticker in stocks_in:
            data[stock_ticker] = []
            for child in self.root.children:
                if child.name == stock_ticker:
                    q = [child]
                    while(len(q) > 0):
                        curr_node = q.pop(0)
                        for index, data_point in enumerate(curr_node.timeseries[self.offset:-length_in]):
                            if len(data[stock_ticker]) <= index: 
                                data[stock_ticker].append([])
                            data[stock_ticker][index].append(data_point)
                        q = q + curr_node.children
        for key in data.keys():
            data[key] = np.array(data[key])
        return data
    
    def get_close_data(self,stocks_in=[]):
        closes = {}
        if len(stocks_in) == 0:
            stocks_in = self.get_tickers()
        
        for stock_ticker in stocks_in:
            closes[stock_ticker] = []
            for child in self.root.children:
                if child.name == stock_ticker:
                    closes[stock_ticker] = child.close[self.offset:]
        return closes

    def get_tickers(self):
        ret = []
        for stock in self.root.children:
            ret.append(stock.name)
        return ret

    def get_data_for_network(self, length_in=5, type="close"):
        
        indicators = self.get_indicator_data(length_in=length_in)
        if type == "close": subject_data = self.get_close_data()

        x = indicators
        print(len(x["BA"]), len(x["BA"][0]))

        y = self.generate_training_data(data_in=subject_data, length_in=length_in)
        assert(len(x) == len(y))

        print(len(x["BA"]), len(y["BA"]))
        assert(len(x["BA"]) == len(y["BA"]))
        return x,y

    
    def generate_training_data(self,data_in, length_in=1):
        keys = list(data_in.keys())
        ret = {}
        for stock in keys:
            ret[stock] = np.empty((len(data_in[keys[0]])-length_in))
            #ret[stock][:] = np.NaN
        for i in range(len(data_in[keys[0]]) - length_in):
            for stock in keys:
                ret[stock][i] = ((data_in[stock][i+length_in] - data_in[stock][i]) / data_in[stock][i])*100
        return ret
    
    
    





    

