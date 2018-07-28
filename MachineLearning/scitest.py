print(__doc__)

import MySQLdb
import numpy as numpy
from numpy import array
import pandas as pd

import re

import matplotlib.pyplot as plt
import numpy as np
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score
from sklearn import preprocessing

from configparser import SafeConfigParser

config = SafeConfigParser()
config.read('../Config/config.ini')

def initializeDatabase():
  try:
    db = MySQLdb.connect(host=config.get('sql', 'host'),
              user=config.get('sql', 'user'),
              passwd=config.get('sql', 'passwd'),
              db=config.get('sql', 'db'))
    print('Database initialized!')
  except ValueError:
    print('Error connecting to database!')
  
  return db

def databaseToDataframe(database):
  df_mysql = pd.read_sql('select * from data;', con=database)
  df_mysql.set_index('time', inplace=True)
  return df_mysql

database = initializeDatabase()
dataframe = databaseToDataframe(database)

dataframe_prices = dataframe['price'].values
dataframe_highs = dataframe['high'].values
dataframe_lows = dataframe['low'].values

#Strip strings into date-time format
dataframe_time = dataframe.index.values
for z in range (0, len(dataframe_time)):
  this_time = dataframe_time[z]
  this_time = re.sub('\+00:00$', '', this_time)
  dataframe_time[z] = this_time

pandas_date = pd.to_datetime(dataframe_time)
numpy_date = numpy.array(pandas_date,dtype=numpy.datetime64)

#dataframe_np = dataframe.as_matrix(columns=None)
#print(dataframe_np)

price_reshaped = dataframe_prices.reshape(-1, 1)
high_reshaped = dataframe_prices.reshape(-1, 1)

# standardize the data attributes
standardized_price = preprocessing.scale(price_reshaped)
standardized_high = preprocessing.scale(high_reshaped)

'''
print('\nSTANDARDIZED:')
print(standardized_price)
'''

# Split the data into training/testing sets
price_x_train = standardized_price[:-20]
price_x_test = standardized_price[-20:]

# Split the targets into training/testing sets
price_y_train = standardized_high[:-20]
price_y_test = standardized_high[-20:]

# Create linear regression object
regr = linear_model.LinearRegression()

#print(len(price_y_train))

# Train the model using the training sets
regr.fit(price_x_train, price_y_train)

# Make predictions using the testing set
price_y_pred = regr.predict(price_x_test)

# The coefficients
print('Coefficients: \n', regr.coef_)
# The mean squared error
print("Mean squared error: %.2f"
      % mean_squared_error(price_y_test, price_y_pred))
# Explained variance score: 1 is perfect prediction
print('Variance score: %.2f' % r2_score(price_y_test, price_y_pred))

# Plot outputs
plt.scatter(price_x_test, price_y_test,  color='black')
plt.plot(price_x_test, price_y_pred, color='red', linewidth=1)

plt.xticks(())
plt.yticks(())

plt.show()