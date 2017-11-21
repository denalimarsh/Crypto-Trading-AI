
import MySQLdb
import numpy as numpy
from numpy import array
import pandas as pd

import matplotlib.pyplot as plt
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score
from sklearn import preprocessing

this_list = []
for x in range(0, 1000):
  this_list.append(x)


ts = pd.Series(this_list, index=date_range('1/1/2000', periods=1000))

ts = ts.cumsum()

ts.plot()