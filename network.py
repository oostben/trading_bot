import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from collections import OrderedDict
import matplotlib.pyplot as plt
from constants import *
import os
import shutil

class Network(nn.Module):
    def __init__(self,num_inds,activation=nn.ReLU(),shape_in=[1000,400],learning_rate_in=.01):
        super().__init__()
        self.learning_rate = learning_rate_in
        self.layers = OrderedDict()
        self.activation = activation
        self.layers['lin1'] = nn.Linear(num_inds, shape_in[0])
        self.layers['act1'] = self.activation
        for i in range(len(shape_in) - 1):
            self.layers['lin' + str(i + 2)] = nn.Linear(shape_in[i], shape_in[i + 1])
            self.layers['norm' + str(i + 2)] = nn.LayerNorm(shape_in[i + 1])
            self.layers['act' + str(i + 2)] = self.activation
            torch.nn.init.normal_(self.layers['lin' + str(i + 2)].weight, mean=0.0, std=1)

        self.layers['lin' + str(len(shape_in) + 1)] = nn.Linear(shape_in[-1], 1)
        # self.layers['act' + str(len(shape_in) + 1)] = self.activation
        self.network = nn.Sequential(self.layers)
        self.init_weights()
    
    # initialize weights/biases in every layer
    def init_weights(self):
        for layer in self.network:
            if isinstance(layer, nn.Linear):
                torch.nn.init.normal_(layer.weight, mean=0.0, std=0.5)
        for name, param in self.network.named_parameters():
            print(name, param.grad)
        return

    def forward(self, x):
        return self.network(x)

    def train_model(self, x_lis, y_lis, x_val, y_val, epochs = 15):
        
        if os.path.exists(PLOTS_PATH):
            shutil.rmtree(PLOTS_PATH)
        os.makedirs(PLOTS_PATH)

        loss_fn = nn.MSELoss()
        print(self.learning_rate)
        optimizer = torch.optim.RMSprop(self.network.parameters(), lr = self.learning_rate)
        val_acc, train_acc = [],[]
        for t in range(epochs):
            for i in range(len(x_lis)):
                x = x_lis[i]
                y = y_lis[i]
                x_tensor = torch.Tensor(x)
                y_tensor = torch.Tensor(np.array(y))
                y_pred = self.network(x_tensor)
                y_pred = torch.squeeze(y_pred)
                loss = loss_fn(y_pred, y_tensor)
                # print(loss,y_pred,y_tensor, )
                optimizer.zero_grad()
                nn.utils.clip_grad_norm_(self.network.parameters(), max_norm=2.0, norm_type=2)
                loss.backward()
                nn.utils.clip_grad_norm_(self.network.parameters(), max_norm=2.0, norm_type=2)
                optimizer.step()
            total = 0
            correct_signal = 0
            for i in range(len(x_val)):
                total += 1
                x_tensor = torch.Tensor(x_val[i])
                y_pred = self.network(x_tensor)

                if (y_pred > 0 and y_val[i] > 0) or (y_pred < 0 and y_val[i] < 0):
                    correct_signal += 1
            print("** Accuracy for val on epoch ", t , " **")
            print(correct_signal, total, correct_signal/total)
            val_acc.append(correct_signal/total)

            plt.plot([x for x in range(len(val_acc))],val_acc, label = "val")

            total = 0
            correct_signal = 0
            for i in range(len(x_lis)):
                total += 1
                x_tensor = torch.Tensor(x_lis[i])
                y_pred = self.network(x_tensor)
                if (y_pred > 0 and y_lis[i] > 0) or (y_pred < 0 and y_lis[i] < 0):
                    correct_signal += 1
            print("** Accuracy for train on epoch ", t , " **")
            print(correct_signal, total, correct_signal/total,"\n")
            train_acc.append(correct_signal/total)
            plt.plot([x for x in range(len(train_acc))],train_acc, label = "train")
            plt.savefig(os.path.join(PLOTS_PATH, 'epoch' + str(t) + '.png'))

    def test(self, x):
        ret = []
        for inds in x:
            x_tensor = torch.Tensor(inds)
            ret.append(self.network(x_tensor))
        return ret

    def predict(self, x):
        x_tensor = torch.Tensor(x)
        return float(self.network(x_tensor))
