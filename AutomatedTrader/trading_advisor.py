# coding=utf-8

from Data_Processing.data_processing import DataProcessor

import MySQLdb

import sklearn
from sklearn import model_selection
from sklearn.linear_model import LinearRegression
from sklearn.datasets import load_boston

import pdb

from configparser import SafeConfigParser

config = SafeConfigParser()
config.read('../Config/config.ini')

class Advisor:

	def __init__(self):
		self.df

	def calc_buy_sell(self, intervals, mini_df):

		#below_count = 0
		#above_count = 0

		row_count = 0

		selling_hold= True
		buying_hold = False

		buys = {}
		sells = {}

		for time, data in mini_df.iterrows():
			row_count += 1

			short_sma = data.sma_60
			medium_sma = data.sma_120
			long_sma = data.sma_720
			upper_bound = data.sma_720_upper
			lower_bound = data.sma_720_lower

			cresting_price = (0.02 * long_sma) + long_sma
			bottom_price = long_sma - (0.02 * long_sma)


			if short_sma != None or medium_sma != None or long_sma != None:

				if data.price < long_sma:
					if data.price > bottom_price and data.price > short_sma and buying_hold == False:
						buys[row_count] = data.price
						buying_hold = True
						selling_hold = False
						print('Execute buy at ${}, time: {}, row {}'.format(data.price, time, row_count))
				elif data.price > long_sma:
					if data.price > cresting_price and data.price < short_sma and selling_hold == False:
						sells[row_count] = data.price
						selling_hold = True
						buying_hold = False
						print('Execute sell - ${}, time: {}, row {}'.format(data.price, time, row_count))
				


		print('buys: {}'.format(buys))
		print('sells: {}'.format(sells))

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
