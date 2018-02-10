print(__doc__)

import MySQLdb
import numpy as numpy
from numpy import array
import pandas as pd

import re
import datetime

import matplotlib.pyplot as plt
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

def plot_price_spread(dataframe):

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
  date_shortened = numpy_date[-1000:]

  import pdb
  pdb.set_trace()

  plt.figure()
  plt.title('Current, Low and High (24 hour) Prices for Ethereum')
  plt.xlabel('Price ($USD)')
  plt.ylabel('Time')
  plt.plot_date(x=date_shortened, y=dataframe_prices[-1000:], fmt="r-", color='g', linewidth=1)
  plt.plot_date(x=date_shortened, y=dataframe_highs[-1000:], fmt="r-", color='r', linewidth=1)
  plt.plot_date(x=date_shortened, y=dataframe_lows[-1000:], fmt="r-", color='b', linewidth=1)
  plt.show()



database = initializeDatabase()
dataframe = databaseToDataframe(database)
plot_price_spread(dataframe)

'''

plt.figure()
plt.title('Correlation between Price and High (24 hour) - ETH')
plt.xlabel('Price')
plt.ylabel('High (24 hr)')
axis = plt.axis([300, 400, 300, 400])
m, b = numpy.polyfit(x, y, 1)
plt.grid(True)
plt.plot(x, y, 'k.')
plt.plot(x, m*x + b, '-')
plt.show()

'''


'''
#some helpful data processing:

standardized_x = preprocessing.scale(x)
print(standardized_x)

dataframe_numpy_matrix = dataframe.as_matrix(columns=None)
print(dataframe_numpy_matrix)

print(list(dataframe.columns.values))

'''






