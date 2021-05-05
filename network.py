import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from collections import OrderedDict


class Network(nn.Module):
    def __init__(self,num_inds,activation=nn.ReLU(),shape_in=[1000,500,100,20,10],learning_rate_in=.001):
        super().__init__()
        self.learning_rate = learning_rate_in
        self.layers = OrderedDict()
        self.activation = activation
        self.layers['lin1'] = nn.Linear(num_inds, shape_in[0])
        self.layers['act1'] = self.activation
        for i in range(len(shape_in) - 1):
            self.layers['lin' + str(i + 2)] = nn.Linear(shape_in[i], shape_in[i + 1])
            self.layers['act' + str(i + 2)] = self.activation
            self.layers['norm' + str(i + 2)] = nn.LayerNorm(shape_in[i + 1])
            torch.nn.init.normal_(self.layers['lin' + str(i + 2)].weight, mean=0.0, std=0.01)

        self.layers['lin' + str(len(shape_in) + 1)] = nn.Linear(shape_in[-1], 1)
        # self.layers['act' + str(len(shape_in) + 1)] = self.activation
        self.network = nn.Sequential(self.layers)
        self.init_weights()
    
    # initialize weights/biases in every layer
    def init_weights(self):
        for layer in self.network:
            if isinstance(layer, nn.Linear):
                torch.nn.init.normal_(layer.weight, mean=0.0, std=0.1)
        for name, param in self.network.named_parameters():
            print(name, param.grad)
        return

    def forward(self, x):
        return self.network(x)

    def train_model(self, x_lis, y_lis, epochs = 15):
        loss_fn = nn.MSELoss()
        print(self.learning_rate)
        optimizer = torch.optim.RMSprop(self.network.parameters(), lr = self.learning_rate)
        for t in range(epochs):
            for i in range(len(x_lis)):
                x = x_lis[i]
                y = y_lis[i]
                # print(x)
                # print(y)
                x_tensor = torch.Tensor(x)
                y_tensor = torch.Tensor(np.array(y))
                y_pred = self.network(x_tensor)
                y_pred = torch.squeeze(y_pred)
                loss = loss_fn(y_pred, y_tensor)
                # print(loss,y_pred,y_tensor, )
                if t % 100 == 99:
                    print(t, loss.item())
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
            if y < 0:
                    y_pred = self.network(x_tensor)
                    y_pred = torch.squeeze(y_pred)
                    loss = loss_fn(y_pred, y_tensor)
                    print(loss,y_pred,y_tensor, )
                    if t % 100 == 99:
                        print(t, loss.item())
                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()
            if y < 0:
                    y_pred = self.network(x_tensor)
                    y_pred = torch.squeeze(y_pred)
                    loss = loss_fn(y_pred, y_tensor)
                    print(loss,y_pred,y_tensor, )
                    if t % 100 == 99:
                        print(t, loss.item())
                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()


        
        total = 0
        correct_signal = 0
        for i in range(len(x_lis)):
            total += 1
            x_tensor = torch.Tensor(x_lis[i])
            y_pred = self.network(x_tensor)

            if (y_pred > 0 and y_lis[i] > 0) or (y_pred < 0 and y_lis[i] < 0):
                correct_signal += 1
        print("********************")
        print(correct_signal, total, correct_signal/total)

    def test(self, x):
        ret = []
        for inds in x:
            x_tensor = torch.Tensor(inds)
            ret.append(self.network(x_tensor))
        return ret
    def predict(self, x):
        x_tensor = torch.Tensor(x)
        return float(self.network(x_tensor))
