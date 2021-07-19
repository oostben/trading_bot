# forecast monthly births with xgboost
from xgboost import XGBRegressor
import numpy
from typing import List
from constants import N_ESTIMATORS
from model_interface import SModel

class Boost(SModel):
    def __init__(self):
        self.model = XGBRegressor(
                n_estimators=N_ESTIMATORS,
                max_depth=10,
                eta=0.1,
                subsample=0.7,
                colsample_bytree=0.8)

    def train(self):
        eval_set = [(self.x_train, self.y_train), (self.x_validation, self.y_validation)]
        self.model.fit(self.x_train, self.y_train, eval_metric="mae", eval_set=eval_set, verbose=True)
        self.print_accuracy("val")
        self.print_accuracy("train")

    def set_data(self, x_train, y_train, x_validation=None, y_validation=None):
        self.x_train = x_train
        self.y_train = y_train
        self.x_validation = x_validation
        self.y_validation = y_validation
        self.shuffle_data()

        self.x_train = numpy.array([numpy.array(self.x_train[i]) for i in range(len(self.x_train))])
        self.y_train = numpy.array([numpy.array(self.y_train[i]) for i in range(len(self.y_train))])
        self.x_validation = numpy.array([numpy.array(self.x_validation[i]) for i in range(len(self.x_validation))])
        self.y_validation = numpy.array([numpy.array(self.y_validation[i]) for i in range(len(self.y_validation))])

    def print_accuracy(self, kind):
        if kind == "train": 
            x = self.x_train
            y = self.y_train
        elif kind == "val": 
            x = self.x_validation
            y = self.y_validation
        
        predictions = self.predict(x)
        correct = 0
        for i,y_pred in enumerate(predictions):
            if (y_pred > 0 and y[i] > 0) or (y_pred < 0 and y[i] < 0): correct +=1
        print("XGBoost", kind, " accuracy ", correct/len(x))
    
    def predict(self,data:List):
        data = numpy.asarray(data)
        if data.ndim == 1:
            data = numpy.expand_dims(data, axis=0)
        return self.model.predict(data)

    def get_val_y(self):
        return list(self.predict(self.x_validation))