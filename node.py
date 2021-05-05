from helpers import *
import numpy as np
import talib
from abc import ABCMeta, abstractmethod


class Node:
    def __init__(self, name_in="root", parents_in=None):
        self.name = name_in
        if parents_in is None:
            self.parents = []
        elif isinstance(parents_in, list):
            self.parents = parents_in
        else:
            self.parents = [parents_in]
        self.children = []
        self.length = 0
        self.timeseries = []
        self.been_updated = False

    @abstractmethod
    def update(self):
        pass
    
    def add_child(self, child):
        self.children.append(child)

    def print_name(self):
        print(self.name)

    def get_name(self):
        return self.name

    def updated(self):
        return self.been_updated

    def ready_to_be_updated(self):
        for parent in self.parents:
            if not parent.updated():
                return False
        return True

    def reset_update(self):
        self.been_updated = False
class Root(Node):
    def __init__(self):
        self.name = "root"
        self.parents = []
        self.children = []
        self.length = 0
        self.timeseries = []

    def update(self):
        self.been_updated = True
        return

class Ticker(Node):
    def __init__(self, root_in, symbol_in):
        Node.__init__(self, name_in=symbol_in, parents_in=root_in)
        root_in.add_child(self)
        self.bars = []

    def update(self):
        self.bars = get_bars(self.name)
        self.volume = np.array([bar.v for bar in self.bars])
        self.low = np.array([bar.l for bar in self.bars])
        self.high = np.array([bar.h for bar in self.bars])
        self.open = np.array([bar.o for bar in self.bars])
        self.close = np.array([bar.c for bar in self.bars])
        self.timeseries = np.array([bar.c/max(self.close) for bar in self.bars])

        self.been_updated = True

class SMA(Node):
    def __init__(self, root_in, symbol_in, length_in, type_in="close"):
        potential_name = symbol_in+"_SMA_"+str(length_in)+"_"+type_in
        if node_already_exists(root_in, potential_name): return
        for child in root_in.children:
            if child.get_name() == symbol_in:
                Node.__init__(self, name_in=potential_name, parents_in=child)
                child.add_child(self)
                self.length = length_in
                self.type = type_in
                break

    def update(self):
        if self.type == "open":
            self.timeseries = talib.SMA(self.parents[0].open, timeperiod=self.length)
        elif self.type == "high":
            self.timeseries = talib.SMA(self.parents[0].high, timeperiod=self.length)
        elif self.type == "low":
            self.timeseries = talib.SMA(self.parents[0].low, timeperiod=self.length)
        elif self.type == "close":
            self.timeseries = talib.SMA(self.parents[0].close, timeperiod=self.length)            
        elif self.type == "volume":
            self.timeseries = talib.SMA(self.parents[0].volume, timeperiod=self.length)
        self.been_updated = True

class RSI(Node):
    def __init__(self, root_in, symbol_in, length_in, type_in="close"):
        potential_name = symbol_in+"_RSI_"+str(length_in)+"_"+type_in
        if node_already_exists(root_in, potential_name): return
        for child in root_in.children:
            if child.get_name() == symbol_in:
                Node.__init__(self, name_in=potential_name, parents_in=child)
                child.add_child(self)
                self.length = length_in
                self.type = type_in
                break

    def update(self):
        if self.type == "open":
            self.timeseries = talib.RSI(self.parents[0].open, timeperiod=self.length)
        elif self.type == "high":
            self.timeseries = talib.RSI(self.parents[0].high, timeperiod=self.length)
        elif self.type == "low":
            self.timeseries = talib.RSI(self.parents[0].low, timeperiod=self.length)
        elif self.type == "close":
            self.timeseries = talib.RSI(self.parents[0].close, timeperiod=self.length)            
        elif self.type == "volume":
            self.timeseries = talib.RSI(self.parents[0].volume, timeperiod=self.length)
        self.been_updated = True


class ROC(Node):
    def __init__(self, root_in, symbol_in, length_in, type_in="close"):
        potential_name = symbol_in+"_ROC_"+str(length_in)+"_"+type_in
        if node_already_exists(root_in, potential_name): return
        for child in root_in.children:
            if child.get_name() == symbol_in:
                Node.__init__(self, name_in=potential_name, parents_in=child)
                child.add_child(self)
                self.length = length_in
                self.type = type_in
                break

    def update(self):
        if self.type == "open":
            self.timeseries = talib.ROC(self.parents[0].open, timeperiod=self.length)
        elif self.type == "high":
            self.timeseries = talib.ROC(self.parents[0].high, timeperiod=self.length)
        elif self.type == "low":
            self.timeseries = talib.ROC(self.parents[0].low, timeperiod=self.length)
        elif self.type == "close":
            self.timeseries = talib.ROC(self.parents[0].close, timeperiod=self.length)            
        elif self.type == "volume":
            self.timeseries = talib.ROC(self.parents[0].volume, timeperiod=self.length)
        self.been_updated = True

class GC(Node):
    def __init__(self, root_in, symbol_in, fast_in, slow_in, type_in="close"):
        potential_name = symbol_in+"_GC_"+str(fast_in)+"_"+str(slow_in)+"_"+type_in

        if node_already_exists(root_in, potential_name): return
        SMA(root_in=root_in, symbol_in=symbol_in,length_in=fast_in,type_in=type_in)
        SMA(root_in=root_in, symbol_in=symbol_in,length_in=slow_in,type_in=type_in)

        for child in root_in.children:

            if child.get_name() == symbol_in:
                for ind in child.children:
                    if ind.name == symbol_in+"_SMA_"+str(fast_in)+"_"+type_in:
                        fast = ind
                    if ind.name == symbol_in+"_SMA_"+str(slow_in)+"_"+type_in:
                        slow = ind

                Node.__init__(self, name_in=potential_name, parents_in=[fast,slow])
                fast.add_child(self)
                slow.add_child(self)
                self.fast = fast_in
                self.slow = slow_in
                self.type = type_in
                break

    def update(self):
        fast = self.parents[0].timeseries
        slow = self.parents[1].timeseries
        self.timeseries = fast-slow
        # self.timeseries[self.timeseries > 0] = 1
        # self.timeseries[self.timeseries < 0] = -1
        self.been_updated = True