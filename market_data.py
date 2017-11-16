# coding=utf-8

import json
import ccxt
import MySQLdb
import dateutil.parser
import time
from ConfigParser import SafeConfigParser

config = SafeConfigParser()
config.read('config.ini')

def initializeDatabase():
	try:
		db = MySQLdb.connect(host=config.get('sql', 'host'),
							user=config.get('sql', 'user'),
							passwd=config.get('sql', 'passwd'),
							db=config.get('sql', 'db'))
		print('Database initialized!')
	except ValueError:
		print('Error connecting to database!')
	
	return db

#parameterize exchange_title
def initializeExchange():
	print('Initializing connection to GDAX...')
	try:
		exchange = ccxt.gdax()
		try:
			initializeExchangeAPI(exchange)
		except:
			print('Error connecting to exchange: %s API' % exchange.id)
	except:
		print('Error connecting to exchange: %s' % exchange.id)
	print('Connection to GDAX initalized!')
	return exchange

def initializeExchangeAPI(exchange):
	exchange.apiKey = config.get('gdax', 'api_key')
	exchange.secret = config.get('gdax', 'secret')
	exchange.password = config.get('gdax', 'password')

def storeMarketData(exchange, market):
	exchange_markets = exchange.load_markets()
	ticker = exchange.fetch_ticker(market)
	tick_price = ticker['last']
	tick_high = ticker['high']
	tick_low = ticker['low']
	tick_volume = ticker['quoteVolume']
	tick_time = dateutil.parser.parse(ticker['datetime'])

	#print(ticker)

	print('Price: {} at {}'.format(tick_price, tick_time))

	cur = db.cursor()
	try:
		cur.execute ("""INSERT INTO data (price, high, low, volume, time) VALUES (%s,%s,%s,%s,%s);""", 
			(tick_price, tick_high, tick_low, tick_volume, tick_time))
		db.commit()
	except:
		db.rollback()
	cur.close()

def clearDatabase():
	print('\nClearing database...\n')
	cur = db.cursor()
	try:
		cur.execute ("""TRUNCATE TABLE data;""")
		db.commit()
	except:
		db.rollback()
	print('Database cleared!')
'''
#DOES NOT WORK (yet)

def removeDatabaseRows(n):
	print('\nRemoving the last %d rows...' % n)
	cur = db.cursor()
	try:
		cur.execute ("""DELETE FROM data WHERE time IN (SELECT TOP %s time FROM data ORDER BY time DESC);""", n)
		db.commit()
	except:
		db.rollback()
	print('%d rows removed' % n)
'''
def startMarketDataStream(exchange, market, tick_delay):
	print(market)
	while True:
		storeMarketData(exchange, market)
		time.sleep(tick_delay)

#print(ccxt.exchanges)

db = initializeDatabase()
exchange = initializeExchange()
startMarketDataStream(exchange, 'ETH/USD', 15)
#clearDatabase()
db.close()