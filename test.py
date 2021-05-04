from tree import *

tickers = ["AAPL", "AMZN"]
tree = Tree(tickers)

for i in range(2,30):
    tree.add_sma(length_in=i)
    tree.add_rsi(length_in=i)
    tree.add_roc(length_in=i)
for i in range(2,30):
    for j in range(2,30):
        if j >= i: continue
        tree.add_gc(fast_in=i,slow_in=j)
tree.update()

tree.print_tree_names()