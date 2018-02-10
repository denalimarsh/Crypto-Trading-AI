# coding=utf-8

from __future__ import division

import numpy as np
import pandas as pd
import pandas_datareader as web
import scipy.stats as stats

import matplotlib.pyplot as plt
from matplotlib import style
style.use('ggplot')

import MySQLdb

import sklearn
from sklearn import model_selection
from sklearn.linear_model import LinearRegression
from sklearn.datasets import load_boston

import pdb

from configparser import SafeConfigParser

config = SafeConfigParser()
config.read('../Config/config.ini')


class DataProcessor:

	def __init__(self):
		self.db = self.initialize_database()
		self.df = self.database_to_dataframe()

	def initialize_database(self):
		try:
			self.db = MySQLdb.connect(host=config.get('gdax-market-data', 'host'),
								user=config.get('gdax-market-data', 'user'),
								passwd=config.get('gdax-market-data', 'passwd'),
								db=config.get('gdax-market-data', 'db'))
			print('Database initialized!')
		except ValueError:
			print('Error connecting to database!')
		
		return self.db

	def database_to_dataframe(self):
		df_mysql = pd.read_sql('select * from ethereum;', con=self.db)
		df_mysql.set_index('time_stamp', inplace=True)
		return df_mysql

	def high_low_spread(self):
		max_price = self.df['price'].max()
		min_price = self.df['price'].min()
		mean_price = self.df['price'].mean()
		pdb.set_trace()


	def calc_market_stats(self):

		#calculate SMA at different time intervals
		self.sma_calc(200)
		self.sma_calc(500)
		self.sma_calc(1000)

		#calculate percentage change
		self.calc_percent_change()

	def calc_percent_change(self):

		'''
		Calculate percentage change from each price datapoint
		'''

		percent_change = []
		prev_price = 0
		count = 0

		for time, price in self.df['price'].iteritems():
			if count > 0:
				price_delta = (price-prev_price)/prev_price
				percent_change.append(price_delta)
			else:
				percent_change.append(None)
			count += 1
			prev_price = price

		#assign values back to the dataframe
		returns = pd.Series(percent_change)
		self.df = self.df.assign(returns=returns.values)
		self.df = self.df.rename(columns={'column_name': returns})

	def sma_calc(self, n):

		'''
		Calculate Simple Moving Average (SMA) over the preceeding n periods
		'''

		stack = []
		sma_list = []
		for i in range(0, n):
			sma_list.append(None)

		#iterate over data starting n periods out
		for x in range (n, len(self.df)):
			#get dataframe for preceeding n periods
			sma_df = self.df.iloc[(x-n):x]['price']

			#add prices to stack 
			for time, price in sma_df.iteritems():
				stack.append(price)

			#calculate Simple Moving Average (SMA)
			sma = 0
			while len(stack) >= 1:
				sma += stack.pop()
			sma = sma / n
			sma_list.append(sma)

		#Concatenate SMA list into dataframe
		sma_calc = pd.Series(sma_list)
		self.df = self.df.assign(column_name=sma_calc.values)

		#Rename to unique column name with count
		column_name = 'sma_{}'.format(n)
		self.df = self.df.rename(columns={'column_name': column_name})

def main_execute():
	processor = DataProcessor()
	processor.calc_market_stats()

	#plot the current data
	processor.df['price'].plot(c='r', linewidth=0.4)
	processor.df['sma_200'].plot(c='b', linewidth=0.4)
	processor.df['sma_500'].plot(c='g', linewidth=0.4)
	processor.df['sma_1000'].plot(c='y', linewidth=0.4)
	plt.show()

	processor.db.close()

main_execute()


#function to calculate exponential moving average
#WARNING: ema values incorrect

'''
def calculateEMA(dataframe, ticks):

	#prepare prices and multiplier
	df_tail = dataframe.tail(ticks)
	prices_list = df_tail['price'].tolist()
	prices_array = np.asarray(prices_list)

	#use stack for ema calculations
	ema_stack = []
	curr_index = 0
	ema_stack.append(prices_array[curr_index])
	multiplier = 2 / ticks + 1

	#calculate ema
	#while curr_index >= len(prices_array):
	while len(ema_stack) > 0:
		if curr_index != len(prices_array)-1:
			previous_ema = ema_stack.pop()
			current_ema = (prices_array[curr_index] - previous_ema) * multiplier + previous_ema
			ema_stack.append(current_ema)
			curr_index += 1
		else:
			ema = ema_stack.pop()
			print('Exponential Moving Average over {} ticks: {}'.format(ticks, ema))
			return ema
'''

#function to plot linear regression model 

'''
def show_plot(dataframe, ticks):

	df_tail = dataframe.tail(ticks)
	times = list(df_tail.index.values)
	prices = list(df_tail['price'].values)

	linear_mod = linear_model.LinearRegression()
	times = np.reshape(times,(len(times),1))
	linear_mod.fit(times,prices)

	plt.scatter(times,prices,color='yellow')
	plt.plot(times,linear_mod.predict(times),color='blue',linewidth=3)
	plt.show()

	return

'''

#function to predict price

'''

def price_prediction_test(processed_data):

		financial_data = processed_data

		boston = load_boston()
		bos = pd.DataFrame(boston.data)

		bos.head()
		bos.columns = boston.feature_names
		bos.head()

		bos['PRICE'] = boston.target

		#Y = boston housing price(also called “target” data in Python)
		#X = all the other features (or independent variables)

		X = bos.drop('PRICE', axis = 1)

		X_eth = financial_data.drop('price', axis = 1)

		#pdb.set_trace()

		lm = LinearRegression()

		#lm.fit() -> fits a linear model
		lm.fit(X_eth, financial_data.price)

		pd.DataFrame(zip(X_eth.columns, lm.coef_), columns = ['features', 'estimatedCoefficients'])

		#plot to show price vs predicted price:

		#lm.predict() functionality: Predict Y using the linear model with estimated coefficients

		plt.scatter(X_eth.volume, lm.predict(X_eth), c='b', s=2)
		plt.xlabel('Prices: $Y_i$')
		plt.ylabel('Predicted prices: $\hat{Y}_i$')
		plt.title('Price vs Predicted Prices: $Y_i$ vs $\hat{Y}_i$')
		plt.show()

def predict_price(dataframe, ticks, prediction_tick):

	#pair dates with ticks in dictionary

	df_tail = dataframe.tail(ticks)
	prices_list = list(df_tail['price'].values)
	for(prices_list)
	dates_list = list(df_tail.index.values)


	tick_list = []
	for x in range (0, ticks - 1):
		tick_list.add(x)

	prediction_date = dates_list[-prediction_tick]
	prediction = [prediction_date]

	linear_mod = linear_model.LinearRegression()
	dates = np.reshape(dates_list,(len(dates_list),1))
	prices = np.reshape(prices_list,(len(prices_list),1))

	linear_mod.fit(dates, prices)
	predicted_price = linear_mod.predict(prediction)
	return predicted_price[0][0],linear_mod.coef_[0][0],linear_mod.intercept_[0]

'''