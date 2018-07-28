# coding=utf-8

from __future__ import division
import statistics

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

	def __init__(self, intervals):
		self.db = self.initialize_database()
		self.df = self.database_to_dataframe()
		self.intervals = intervals
		self.calc_market_stats()

	def initialize_database(self):
		try:
			self.db = MySQLdb.connect(host=config.get('gdax-market-data', 'host'),
								user=config.get('gdax-market-data', 'user'),
								passwd=config.get('gdax-market-data', 'passwd'),
								db=config.get('gdax-market-data', 'db'))
			print('DataProcessor database initialized!')
		except ValueError:
			print('Error connecting to database!')
		
		return self.db

	def database_to_dataframe(self):
		df_mysql = pd.read_sql('select * from ethereum;', con=self.db)
		df_mysql.set_index('time_stamp', inplace=True)
		return df_mysql

	def get_dataframe_subset(self, row_count):
		subset_df = self.df.tail(row_count)
		return subset_df

	def high_low_spread(self):
		max_price = self.df['price'].max()
		min_price = self.df['price'].min()
		mean_price = self.df['price'].mean()

	def calc_market_stats(self):

		#calculate SMA at different time intervals
		self.sma_calc()

		#calculate Exponential Weighted Moving Average (EWMA) bands
		self.calc_bollinger_bands()

		#calculate buy-sell reccomendations
		#self.calc_buy_sell(intervals)

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

	def sma_calc(self):

		'''
		Calculate Simple Moving Average (SMA) over the preceeding n periods
		'''

		for i, period in enumerate(self.intervals):
			n = self.intervals[i]

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

	#does not currently work...
	def calc_ewma(self, n):

		'''
		Calculate Elastic Weighted Moving Average over the preceeding n periods
		'''

		ewma_list = []
		for i in range(0, n):
			ewma_list.append(None)

		multiplier = 2/(n+1)
		stack = []

		for x in range (n, len(self.df)):
			ewma_df = self.df.iloc[(x-n):x]['price']
			pdb.set_trace()

			for time, price in ewma_df.iteritems():
				stack.append(price)

			#calculate ewma
			ewma = 0
			while len(stack) >= 1:
				price = stack.pop()
				ewma = price*multiplier + (1-multiplier)*ewma
			ewma_list.append(ewma)

			pdb.set_trace()

		#Concatenate EWMA list into dataframe
		ewma_calc = pd.Series(ewma_list)
		self.df = self.df.assign(column_name=ewma_calc.values)

		#Rename to unique column name with count
		column_name = 'ewma_{}'.format(n)
		self.df = self.df.rename(columns={'column_name': column_name})

	def calc_bollinger_bands(self):

		'''
		Calculate the Bollinger Bands over the preceeding n periods
		'''

		n = self.intervals[2]

		upper_band_values = []
		lower_band_values = []

		for i in range(0, n*2):
			upper_band_values.append(None)
			lower_band_values.append(None)

		for x in range (n*2, len(self.df)):
			#get subset of dataframe as numpy arr
			mini_df = self.df.iloc[(x-n):x]['sma_{}'.format(n)]
			numpy_matrix = mini_df.as_matrix()

			#calculate standard deviation
			standard_dev = np.std(numpy_matrix)

			#calculate upper and lower bounds
			curr_sma = self.df['sma_{}'.format(n)][x]

			upper_band = curr_sma + (standard_dev*2)
			upper_band_values.append(upper_band)

			lower_band = curr_sma - (standard_dev*2)
			lower_band_values.append(lower_band)

		#Concatenate upper into dataframe
		upper_band_series = pd.Series(upper_band_values)
		self.df = self.df.assign(column_name=upper_band_series.values)
		column_name = 'sma_{}_upper'.format(n)
		self.df = self.df.rename(columns={'column_name': column_name})

		#Concatenate lower into dataframe
		lower_band_series = pd.Series(lower_band_values)
		self.df = self.df.assign(column_name=lower_band_series.values)
		column_name = 'sma_{}_lower'.format(n)
		self.df = self.df.rename(columns={'column_name': column_name})
	
	def plot(self, subset_df):

		#plot price, sma
		subset_df['price'].plot(c='r', linewidth=0.4, label='Price')
		subset_df['sma_{}'.format(self.intervals[0])].plot(c='b', linewidth=1, label='{} min'.format(self.intervals[0]))
		#subset_df['sma_{}'.format(intervals[1])].plot(c='g', linewidth=1, label='{} min'.format(intervals[1]))
		subset_df['sma_{}'.format(self.intervals[2])].plot(c='y', linewidth=1, label='{} min'.format(self.intervals[2]))

		#plot bollinger bands
		subset_df['sma_{}_upper'.format(self.intervals[2])].plot(c='black', linewidth=1.5, label='{} upper bound'.format(self.intervals[2]))
		subset_df['sma_{}_lower'.format(self.intervals[2])].plot(c='black', linewidth=1.5, label='{} lower bound'.format(self.intervals[2]))

		plt.title('ETH/USD Market on GDAX with SMA and Bollinger Bands')
		plt.ylabel('Price')
		plt.xlabel('Time')

		plt.legend()
		plt.show()
'''
def main_execute():
	processor = DataProcessor()

	intervals = [60, 120, 720]
	processor.calc_market_stats(intervals)

	subset_df = processor.get_dataframe_subset(3500)
	processor.calc_buy_sell(intervals, subset_df)

	#plot price, sma
	subset_df['price'].plot(c='r', linewidth=0.4, label='Price')
	subset_df['sma_{}'.format(intervals[0])].plot(c='b', linewidth=1, label='{} min'.format(intervals[0]))
	#subset_df['sma_{}'.format(intervals[1])].plot(c='g', linewidth=1, label='{} min'.format(intervals[1]))
	subset_df['sma_{}'.format(intervals[2])].plot(c='y', linewidth=1, label='{} min'.format(intervals[2]))

	#plot bollinger bands
	subset_df['sma_{}_upper'.format(intervals[2])].plot(c='black', linewidth=1.5, label='{} upper bound'.format(intervals[2]))
	subset_df['sma_{}_lower'.format(intervals[2])].plot(c='black', linewidth=1.5, label='{} lower bound'.format(intervals[2]))

	plt.title('ETH/USD Market on GDAX with SMA and Bollinger Bands')
	plt.ylabel('Price')
	plt.xlabel('Time')

	plt.legend()
	plt.show()

	processor.db.close()

main_execute()
'''
'''
def show_tail_plot(self, df_tail):

	times = list(df_tail.index.values)
	prices = list(df_tail['price'].values)

	linear_mod = linear_model.LinearRegression()
	times = np.reshape(times,(len(times),1))
	linear_mod.fit(times,prices)

	plt.scatter(times,prices,color='yellow')
	plt.plot(times,linear_mod.predict(times),color='blue',linewidth=3)
	plt.show()
'''

#function to plot linear regression model 

'''
def show_plot(self, n):

	df_tail = self.df.tail(n)
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