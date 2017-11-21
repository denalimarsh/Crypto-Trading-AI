print(__doc__)


import MySQLdb
import numpy as numpy
from numpy import array
import pandas as pd

import matplotlib.pyplot as plt
import numpy as np
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score
from sklearn import preprocessing

from ConfigParser import SafeConfigParser

config = SafeConfigParser()
config.read('config.ini')

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

print(type(dataframe))

# Load the diabetes dataset
diabetes = datasets.load_diabetes()

dataframe_np = dataframe.as_matrix(columns=None)
print(dataframe_np)

'''
print('\nDataframe:')
print(dataframe)
print()

print('\nDiabetes:')
print(diabetes)
print()
'''

# Use only one feature
diabetes_X = diabetes.data[:, np.newaxis, 2]

print(dataframe_np.shape)

#price_reshaped = dataframe_np.reshape(-1, 1)

#print(type(dataframe_price))


#print('\nDataframe - PRICE:')
#print(price_reshaped)

# standardize the data attributes
standardized_price = preprocessing.scale(dataframe_np)

print('\nSTANDARDIZED:')
print(standardized_price)

# Split the data into training/testing sets
price_x_train = standardized_price[:-20]
price_x_test = standardized_price[-20:]

'''
price_headers = []
for x in range(0, dataframe_np):
  price_headers.append('price')

price_y = array(price_headers)
'''


# Split the targets into training/testing sets
price_y_train = ['price']
price_y_test = ['price']

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
plt.scatter(price_test, price_y_test,  color='black')
plt.plot(price_test, price_y_pred, color='red', linewidth=1)

plt.xticks(())
plt.yticks(())

plt.show()