import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from collections import OrderedDict
import matplotlib.pyplot as plt
from constants import *
import os
import shutil
from typing import List
from model_interface import SModel

class Network(SModel):
    def __init__(self,
                num_inds,activation=nn.ELU(),
                shape_in=[300,600,600,300,50,10],
                learning_rate_in=.01,
                epochs=15):

        self.val_acc = []
        self.train_acc = []
        self.epochs = epochs
        self.learning_rate = learning_rate_in
        self.activation = activation

        self.layers = OrderedDict()
        self.layers['lin1'] = nn.Linear(num_inds, shape_in[0])
        self.layers['act1'] = self.activation
        for i in range(len(shape_in) - 1):
            self.layers['lin' + str(i + 2)] = nn.Linear(shape_in[i], shape_in[i + 1])
            self.layers['norm' + str(i + 2)] = nn.LayerNorm(shape_in[i + 1])
            self.layers['act' + str(i + 2)] = self.activation
            torch.nn.init.xavier_uniform_(self.layers['lin' + str(i + 2)].weight, gain=nn.init.calculate_gain('relu'))
            # torch.nn.init.normal_(self.layers['lin' + str(i + 2)].weight, mean=0.0, std=1)

        self.layers['lin' + str(len(shape_in) + 1)] = nn.Linear(shape_in[-1], 1)
        # self.layers['act' + str(len(shape_in) + 1)] = self.activation
        self.network = nn.Sequential(self.layers)
        self.init_weights()
    
    # initialize weights/biases in every layer
    def init_weights(self):
        for layer in self.network:
            if isinstance(layer, nn.Linear):
                torch.nn.init.normal_(layer.weight, mean=0.0, std=1)
        for name, param in self.network.named_parameters():
            print(name, param.grad)
        return

    def train(self) -> None:
        if os.path.exists(PLOTS_PATH): shutil.rmtree(PLOTS_PATH)
        os.makedirs(PLOTS_PATH)

        self.val_acc.clear()
        self.train_acc.clear()

        loss_fn = nn.MSELoss()
        optimizer = torch.optim.Adam(self.network.parameters(), lr = self.learning_rate)
        
        for e in range(self.epochs):
            print(e)
            self.shuffle_data()
            for i in range(len(self.x_train)):
                x = self.x_train[i]
                y = self.y_train[i]
                x_tensor = torch.Tensor(x)
                y_tensor = torch.Tensor(np.array(y))
                y_pred = self.network(x_tensor)
                y_pred = torch.squeeze(y_pred)
                loss = loss_fn(y_pred, y_tensor)
                # print(loss,y_pred,y_tensor, )
                optimizer.zero_grad()
                # nn.utils.clip_grad_norm_(self.network.parameters(), max_norm=2.0, norm_type=2)
                loss.backward()
                # nn.utils.clip_grad_norm_(self.network.parameters(), max_norm=2.0, norm_type=2)
                optimizer.step()
            self.store_accuracy("train")
            self.store_accuracy("val")
            self.store_plot(e)

    def store_plot(self,epoch):
        plt.plot([x for x in range(len(self.train_acc))],self.train_acc, label = "train")
        plt.plot([x for x in range(len(self.val_acc))],self.val_acc, label = "val")
        plt.savefig(os.path.join(PLOTS_PATH, 'epoch' + str(epoch) + '.png'))

    def store_accuracy(self,kind):
        if kind == "val":
            x, y = self.x_validation, self.y_validation
        elif kind == "train":
            x, y = self.x_train, self.y_train
        correct_signal = 0
        for i in range(len(x)):
            x_tensor = torch.Tensor(x[i])
            y_pred = self.network(x_tensor)
            if (y_pred > 0 and y[i] > 0) or (y_pred < 0 and y[i] < 0): correct_signal += 1
        accuracy = correct_signal / len(x)
        print(kind, " ", accuracy, "\n")
        if kind == "val": self.val_acc.append(accuracy)
        elif kind == "train": self.train_acc.append(accuracy)

    def predict(self, data:List):
        x_tensor = torch.Tensor(data)
        return float(self.network(x_tensor))

    def set_data(self, x_train, y_train, x_validation=None, y_validation=None):
        self.x_train = x_train
        self.y_train = y_train
        self.x_validation = x_validation
        self.y_validation = y_validation

    def get_val_y(self):
        ret = []
        for x in self.x_validation:
            ret.append(self.predict(x))
        return ret