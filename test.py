from tree import *
from network import *
from helpers import *
tickers = ["BA", "TSLA", "SCI", "WM", "ACB", "NVDA", "BABA","MSFT","ACN","AAL","T","BAC"]
# tickers = get_sp_500_tickers()
tree = Tree(tickers)

for i in range(2,20,5):
    tree.add_sma(length_in=i)
    tree.add_rsi(length_in=i)
    tree.add_roc(length_in=i)
for i in range(2,50,5):
    for j in range(2,5):
        if j >= i: continue
        tree.add_gc(fast_in=i,slow_in=j)

tree.update()
x_train,y_train = tree.get_data_for_network()

keys = list(x_train.keys())
num_inds = len(x_train[keys[0]][0])
x = []
y = []
x_test = []
y_test = []
for key in keys:
    x.extend(x_train[key][:-100])
    x_test.extend(x_train[key][-100:])
    y.extend(y_train[key][:-100]/max(y_train[key][:-100]))
    y_test.extend(y_train[key][-100:]/max(y_train[key][-100:]))


net = Network(num_inds, activation=torch.nn.ReLU())
# print(x)
net.train_model(x,y)

y_pred = net.test(x_test)

correct = 0
for i in range(len(y_test)):
    if (y_test[i] > 0 and y_pred[i] > 0) or (y_test[i] < 0 and y_pred[i] < 0):
        correct += 1
print(correct, len(y_test), correct/len(y_test))


tree.print_tree_names()
