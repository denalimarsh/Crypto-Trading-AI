# coding=utf-8

import pdb
import json
import numpy as np
import pandas as pd
import MySQLdb
import ccxt
import dateutil.parser
import time
import pprint

from configparser import SafeConfigParser

config = SafeConfigParser()
config.read('../Config/config.ini')

pp = pprint.PrettyPrinter(indent=1)


class Bot:
	'Exchange plugin to facilitate online trading'

	def __init__(self):
		self.exchange = self.initialize_exchange()
		self.db = self.initialize_database('gdax-market-data')

	def __repr__(self):
		pass

	def initialize_exchange(self):
		self.exchange = ccxt.gdax()
		self.exchange.fetch_markets()
		self.initialize_api()
		return self.exchange

	def initialize_api(self):
		try:
			self.exchange.apiKey = config.get('gdax-api', 'api_key')
			self.exchange.secret = config.get('gdax-api', 'secret')
			self.exchange.password = config.get('gdax-api', 'password')
		except:
			print('\nError connecting to {}'.format(self.exchange.id))
		finally:
			print('\nConnected to {}\'s API...'.format(self.exchange.id))

	def initialize_database(self, database_name):
	  try:
	    self.db = MySQLdb.connect(host=config.get('%s' % database_name, 'host'),
	              user=config.get('%s' % database_name, 'user'),
	              passwd=config.get('%s' % database_name, 'passwd'),
	              db=config.get('%s' % database_name, 'db'))
	    print('Database \'%s\' initialized!' % config.get('%s' % database_name, 'db'))
	  except ValueError:
	    print('Error connecting to %s.' % database_name)
	  return self.db

	def close_database(self):
		self.db.close()

	def check_balance(self):
		balance = self.exchange.fetch_balance()

		available_eth = balance.get('ETH').get('free')
		used_eth = balance.get('ETH').get('used')
		total_eth = balance.get('ETH').get('total')

		available_usd = balance.get('USD').get('free')
		used_usd = balance.get('USD').get('used')
		total_usd = balance.get('USD').get('total')

		print('\n\tBalances:\nUSD: {}\nETH: {}\n'.format(available_usd, available_eth))

	def sell_order_limit(self, market, amount, price):
		order = self.exchange.create_limit_sell_order ('{}'.format(market), amount, price, {})
		order_id = order.get('info').get('id')
		print('Order {} placed! Selling {} ETH at ${}.'.format(order_id, amount, price))
		return order_id

	def buy_order_limit(self, market, amount, price):
		try:
			order = self.exchange.create_limit_buy_order ('{}'.format(market), amount, price, {})
			print('Order {} placed! Buying {} ETH at ${}.'.format(order_id, amount, price))
			order_id = order.get('info').get('id')
			return order_id
		except:
			print('\nAn error occured (potentially insufficient funds).')

	def cancel_order(self, order_id):
		try:
			self.exchange.cancel_order('{}'.format(order_id))
			print('Order canceled: {}'.format(order_id))
		except:
			print('\nERROR. Cannot cancel order: {}'.format(order_id))

	def fetch_my_trades(self):
		trades = self.exchange.fetch_my_trades(symbol = 'ETH/USD', params = {})

		print('\n\tTrades:')
		for trade in trades:
			pp.pprint(trade)

	def database_to_dataframe(self):
		df_mysql = pd.read_sql('select * from ethereum;', con=self.db)
		df_mysql.set_index('time_stamp', inplace=True)
		return df_mysql

bot = Bot()
bot.check_balance()

#df = bot.database_to_dataframe()
#bot.fetch_my_trades()

order_id = bot.sell_order_limit('ETH/USD', 0.01, 2000)
#order_id = bot.buy_order_limit('ETH/USD', 1.5, 851)
bot.cancel_order(order_id)

#sma rules:
# = Buy Rule: buy if (60 min && 150 min are below 540 lower bound) && 60 min crossed 150 min upwards

# = Exit Rule: exit 50% if(While(60 && 120 min are above 540 min) 60 min falls below 120 min)
		# 	   exit 50% if ()
