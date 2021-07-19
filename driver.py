from network import *
from boost import *
from data_loader import *

from model_interface import *
from helpers import *
from update_data_db import *

#make sure data exists in RDS
# update_data_db()

#get x,y and dict for actually making the predictions for tommorrow
data_loader = Data_Loader(val_percent = 15)
x_train, y_train, x_validation, y_validation, dict_for_predictions = data_loader.load()


#get number of indicators we are using to set the first layer of the net
num_inds = len(x_train[0])

#initalize the network
boost = IModel(Boost())
net = IModel(Network(num_inds=num_inds, activation=torch.nn.ReLU(), learning_rate_in=LR, epochs=EPOCHS))

boost.set_data(x_train, y_train, x_validation, y_validation)
net.set_data(x_train, y_train, x_validation, y_validation)


#trian
boost.train()
net.train()
temp1 = boost.get_val_y()
temp2 = net.get_val_y()
correct = 0
for i in range(len(temp1)):
    print(temp1[i], temp2[i], (temp1[i]+temp2[i])/2,y_validation[i])
    if ((temp1[i]+temp2[i])/2 > 0 and y_validation[i] > 0) or ((temp1[i]+temp2[i])/2 < 0 and y_validation[i] < 0):
        correct +=1
print(correct / len(temp1))
# get predictions
predictions = {}
for ticker in get_tickers():
    y_pred1 = net.predict(dict_for_predictions[ticker])
    y_pred2 = boost.predict(dict_for_predictions[ticker])
    predictions[ticker] = float((y_pred1/y_pred2))

#sort predictions
predictions = dict(reversed(sorted(predictions.items(), key=lambda item: item[1])))

#write predictions to DB
write_predictions(predictions)

#store the time now for last updated time on website
write_last_time_updated()

#liquidate the old positions
liquidate_positions()

#store the cash value for the website
cash_val = store_cash_val()

# calculate multiplier for position sizing
multiplier = calculate_multiplier(cash_val,predictions)

if multiplier > 0:
    submit_orders(predictions, multiplier)

#write the positions to the db for website
write_positions_to_db()