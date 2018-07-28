# coding=utf-8

from pytrends.request import TrendReq

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from matplotlib import style
style.use('ggplot')

import sklearn
from sklearn import model_selection
from sklearn.linear_model import LinearRegression
from sklearn.datasets import load_boston

import datetime
import pdb

def fetch_data():
  # Login to Google. Only need to run this once, the rest of requests will use the same session.
  pytrend = TrendReq()

  # Create payload and capture API tokens. Only needed for interest_over_time(), interest_by_region() & related_queries()
  pytrend.build_payload(kw_list=['bitcoin', 'ethereum', 'iota'])

  #get interest over time
  google_trends_imported_df = pytrend.interest_over_time()
  google_trends_full_df = google_trends_imported_df.drop('isPartial', axis = 1)

  #import historical ethereum price data
  eth_data_imported_df = pd.read_csv('eth_usd_weekly_historical_data.csv')
  #prepare data: index ethereum dataframe by datetime
  my_dates = pd.to_datetime(eth_data_imported_df['Date'])
  eth_data_drop_date = eth_data_imported_df.drop('Date', axis = 1)
  eth_data_indexed = eth_data_drop_date.set_index(my_dates)
  eth_data_full_df = eth_data_indexed.iloc[::-1]

  #get the last 36 weeks of data from both dataframes
  eth_data_df = eth_data_full_df[-36:]
  google_trends_df = google_trends_full_df[-36:]

  processed_trend_data = pd.concat([eth_data_df, google_trends_df], axis=1)

  #pdb.set_trace()

  return processed_trend_data

def price_prediction(processed_data):

  financial_data = processed_data.dropna(thresh=8)

  
  #Y = boston housing price(also called “target” data in Python)
  #X = all the other features (or independent variables)

  #pdb.set_trace()

  x_independent_variables = financial_data.drop('Price', axis = 1)

  lm = LinearRegression()

  #lm.fit() -> fits a linear model
  lm.fit(x_independent_variables, financial_data.Price)

  print 'Estimated intercept coefficent:', lm.intercept_
  print 'Number of coefficients:', len(lm.coef_)

  pd.DataFrame(zip(x_independent_variables.columns, lm.coef_), columns = ['features', 'estimatedCoefficients'])

  #lm.predict() -> predict Y using the linear model with estimated coefficients

  #plot axis labels and title
  plt.xlabel('Google Trends Weekly Score')
  plt.ylabel('Market Price $USD')
  plt.title('Market Price and Google Trends Analytics (ETH)')

  #plot data points
  plt.scatter(x_independent_variables.ethereum, lm.predict(x_independent_variables), c='b', s=2)

  #plot correlation betwee- linear regression
  m, b = np.polyfit(x_independent_variables.ethereum, lm.predict(x_independent_variables), 1)
  plt.plot(x_independent_variables.ethereum, lm.predict(x_independent_variables), '.')
  plt.plot(x_independent_variables.ethereum, m*x_independent_variables.ethereum + b, '-')

  plt.show()



data_block = fetch_data()
price_prediction(data_block)






'''

# Interest by Region
interest_by_region_df = pytrend.interest_by_region()
print(interest_by_region_df.head())

# Related Queries, returns a dictionary of dataframes
related_queries_dict = pytrend.related_queries()
print(related_queries_dict)

# Get Google Hot Trends data
trending_searches_df = pytrend.trending_searches()
print(trending_searches_df.head())

# Get Google Top Charts
#input categories:
#https://trends.google.com/trends/topcharts#vm=cat&geo=US&date=201710&cid=business_and_politics

top_charts_df = pytrend.top_charts(cid='actors', date=201611)
print(top_charts_df.head())

# Get Google Keyword Suggestions
suggestions_dict = pytrend.suggestions(keyword='cryptocurrency')
print(suggestions_dict)

'''