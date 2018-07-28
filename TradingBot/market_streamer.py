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


class MarketStreamer:
	'Collect and store ethereum market data from a public online exchange'

	def __init__(self):
		self.exchange = self.initialize_exchange()
		self.db = self.initialize_database('gdax-market-data')

	def initialize_exchange(self):
		self.exchange = ccxt.gdax()
		self.exchange.fetch_markets()
		return self.exchange

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

	def fetch_ticker(self, market_id):
		ticker = self.exchange.fetch_ticker('{}'.format(market_id))

		last = ticker['last']
		market_volume = ticker['baseVolume']
		date_time = dateutil.parser.parse(ticker['datetime'])

		print('${}, {}'.format(last, date_time))
		self.store_market_data(last, market_volume, date_time)

	def store_market_data(self, price, market_volume, time_stamp):
		self.cursor = self.db.cursor()
		try:
			self.cursor.execute("""INSERT INTO ethereum VALUES (%s,%s,%s)""",(price, time_stamp, market_volume))
			self.db.commit()
		except:
			self.db.rollback()
		self.cursor.close()

	def start_market_stream(self, market, tick_delay):
		print('{} market, {} second intervals:'.format(market, tick_delay))
		while True:
			self.fetch_ticker(market)
			time.sleep(tick_delay)


streamer = MarketStreamer()
streamer.start_market_stream('ETH/USD', 60)
streamer.close_database()
