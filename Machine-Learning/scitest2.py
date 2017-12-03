# coding=utf-8

import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt 

import sklearn
from sklearn import model_selection
from sklearn.linear_model import LinearRegression
from sklearn.datasets import load_boston

import pdb

boston = load_boston()

bos = pd.DataFrame(boston.data)
bos.head()

bos.columns = boston.feature_names
bos.head()

bos['PRICE'] = boston.target

#Y = boston housing price(also called “target” data in Python)
#X = all the other features (or independent variables)

X = bos.drop('PRICE', axis = 1)

#pdb.set_trace()

lm = LinearRegression()

#lm.fit() -> fits a linear model
lm.fit(X, bos.PRICE)

print 'Estimated intercept coefficent:', lm.intercept_
print 'Number of coefficients:', len(lm.coef_)

pd.DataFrame(zip(X.columns, lm.coef_), columns = ['features', 'estimatedCoefficients'])


#plot to show price vs predicted price:

#lm.predict() functionality: Predict Y using the linear model with estimated coefficients

plt.scatter(bos.RM, lm.predict(X), s=2)
plt.xlabel('Prices: $Y_i$')
plt.ylabel('Predicted prices: $\hat{Y}_i$')
plt.title('Price vs Predicted Prices: $Y_i$ vs $\hat{Y}_i$')
plt.show()


#lm.score() -> Returns the coefficient of determination (R^2).
mseFull = np.mean((bos.PRICE - lm.predict(X)) ** 2)
print('Mean Squared Error: {}'.format(mseFull))

X_train, X_test, Y_train, Y_test = sklearn.model_selection.train_test_split(X, bos.PRICE, test_size=0.33, random_state = 5)

#print shape sizes:
'''
print X_train.shape
print X_test.shape
print Y_train.shape
print Y_test.shape

lm = LinearRegression()
lm.fit(X_train, Y_train)
pred_train = lm.predict(X_train)
pred_test = lm.predict(X_test)

print 'Fit a model X_train, and calculate MSE with Y_train:', np.mean((Y_train - lm.predict(X_train)) ** 2)
print 'Fit a model X_train, and calculate MSE with X_test', np.mean((Y_test - lm.predict(X_test)) ** 2)


plt.scatter(lm.predict(X_train), lm.predict(X_train) - Y_train, c='b', s=10, alpha=0.5)
plt.scatter(lm.predict(X_test), lm.predict(X_test) - Y_test, c='g', s=10)
plt.hlines(y = 0, xmin=0, xmax=50)
plt.title('Residual Plot using training (blue) and test (green) data')
plt.ylabel('Residuals')
plt.show()

'''