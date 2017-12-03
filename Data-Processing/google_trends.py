from pytrends.request import TrendReq
import pandas as pd

import datetime
import pdb

# Login to Google. Only need to run this once, the rest of requests will use the same session.
pytrend = TrendReq()

# Create payload and capture API tokens. Only needed for interest_over_time(), interest_by_region() & related_queries()
pytrend.build_payload(kw_list=['bitcoin', 'ethereum', 'iota'])

# Interest Over Time
interest_over_time_df = pytrend.interest_over_time()

eth_data_imported_df = pd.read_csv('eth_usd_weekly_historical_data.csv')

#store dates
my_dates = pd.to_datetime(eth_data_imported_df['Date'])

eth_data_drop_date = eth_data_imported_df.drop('Date', axis = 1)

eth_data_df = eth_data_drop_date.set_index(my_dates)


'''
for curr_date in eth_historical_data['Date']:
  print('Before: %s' % curr_date)
  datetime.strptime(curr_date, '%Y-%m-%d')
  print('After: %s' % curr_date)
'''


pdb.set_trace()

#print(interest_over_time_df)

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