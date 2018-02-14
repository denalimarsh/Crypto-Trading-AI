# coding=utf-8

from data_processing import DataProcessor

import numpy as np
import pandas as pd
import pandas_datareader as web
import scipy.stats as stats

import matplotlib.pyplot as plt
from matplotlib import style
style.use('ggplot')


import sklearn
from sklearn import model_selection
from sklearn.linear_model import LinearRegression
from sklearn.datasets import load_boston

import pdb

class Advisor:

	def __init__(self, intervals):
		self.processor = DataProcessor(intervals)

	def calc_buy_sell(self, intervals, mini_df):

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
	intervals = [60, 120, 720]
	advisor = Advisor(intervals)

	subset_df = advisor.processor.get_dataframe_subset(3500)

	advisor.calc_buy_sell(intervals, subset_df)
	advisor.processor.plot(subset_df)

	advisor.processor.db.close()

main_execute()
