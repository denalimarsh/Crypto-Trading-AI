
import MySQLdb
import numpy as numpy
from numpy import array
import pandas as pd

import matplotlib.pyplot as plt
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score
from sklearn import preprocessing

iris = load_iris()

print(iris.data)