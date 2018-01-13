# coding=utf-8

import MySQLdb

import decimal

import operator
import urllib2
from bs4 import BeautifulSoup

import pdb 
from datetime import datetime
import re

import pandas as pd

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint

from ConfigParser import SafeConfigParser

config = SafeConfigParser()
config.read('../Config/config.ini')

class Coin:

  def __init__(self):
    self.name = ''
    self.datetime = ''
    self.price = 0
    self.high = 0
    self.low = 0
    self.volume = 0
    self.market_cap = 0

  def __repr__(self):
    return 'Name: %s, Price: %s, High: %s, Low: %s, Volume: %s, Market Cap: %s' % \
    (self.name, self.price, self.high, self.low, self.volume, self.market_cap)

def initialize_database(database_name):
  try:
    db = MySQLdb.connect(host=config.get('%s' % database_name, 'host'),
              user=config.get('%s' % database_name, 'user'),
              passwd=config.get('%s' % database_name, 'passwd'),
              db=config.get('%s' % database_name, 'db'))
    print('Database \'%s\' initialized!' % config.get('%s' % database_name, 'db'))
  except ValueError:
    print('Error connecting to %s.' % database_name)
  
  return db

def access_website(url):

  hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}


  req = urllib2.Request(url, headers=hdr)
  
  try:
      cryptocoin_html = urllib2.urlopen(req)
  except urllib2.HTTPError, e:
      print e.fp.read()

  cryptocoin_soup = BeautifulSoup(cryptocoin_html, "html.parser")

  return cryptocoin_soup

def coin_setup():
  curr_time = datetime.now()

  coins = []
  coin_names = ['bitcoin', 'ethereum', 'iota', 'substratum', 'siacoin']


  for coin in coin_names:
    new_coin = Coin()
    new_coin.name = coin
    new_coin.datetime = curr_time
    coins.append(new_coin)

  return coins

def strip_to_float(object):
  non_decimal = re.compile(r'[^\d.]+')
  return float(non_decimal.sub('', object))

def get_cryptocoin_market_data():

  #Open cryptocoin website
  cryptocoin_soup = access_website('https://www.worldcoinindex.com/')

  #Set up coins with names
  coins = coin_setup()


  print('Time: {}'.format(coins[0].datetime))
  
  #Search cryptocoin HTML for each coin name
  for coin in coins:
    market_data = cryptocoin_soup.find("tr", attrs={"data-naam": "{}".format(coin.name)})

    if market_data == None:
      print('\'{}\' not found on page 1. Searching the next page...'.format(coin.name))
      secondary_cryptocoin_soup = access_website('https://www.worldcoinindex.com/2')
      market_data = secondary_cryptocoin_soup.find("tr", attrs={"data-naam": "{}".format(coin.name)})

      if market_data == None:
        print('\'{}\' not found on page 2. Searching the next page...'.format(coin.name))
        secondary_cryptocoin_soup = access_website('https://www.worldcoinindex.com/3')
        market_data = secondary_cryptocoin_soup.find("tr", attrs={"data-naam": "{}".format(coin.name)})

    #Get relevant market data
    current_price_data = market_data.find("td", attrs={"number pricekoers lastprice"})
    current_price = current_price_data.get('data-sort-value')
    current_price_float = strip_to_float(current_price)
    coin.price = current_price_float

    high_price_data = market_data.find("td", attrs={"number pricekoers highprice mob-hide-col"})
    high_price = high_price_data.get('data-sort-value')
    high_price_float = strip_to_float(high_price)
    coin.high = high_price_float

    low_price_data = market_data.find("td", attrs={"number pricekoers lowprice mob-hide-col"})
    low_price = low_price_data.get('data-sort-value')
    low_price_float = strip_to_float(low_price)
    coin.low = low_price_float

    volume_data = market_data.find("td", attrs={"number pricekoers volume mob-hide-col"})
    volume = volume_data.get('data-sort-value')
    volume_float = strip_to_float(volume)
    coin.volume = volume_float

    market_cap_data = market_data.find("td", attrs={"number pricekoers marketcap mob-hide-col"})
    market_cap = market_cap_data.get('data-sort-value')
    market_cap_float = strip_to_float(market_cap)
    coin.market_cap = market_cap_float

    print(coin)

  print('Coin market data collected!\n')

  store_market_data(coins)


def store_market_data(coins):

  db = initialize_database('sql-market-data')

  print('\nStoring market data in SQL database...\n')

  #Insert coin market data into SQL database
  cur = db.cursor()

  #for coin in coins:
  coin = coins[0]

  print('TO BE STORED: {}'.format(coin))

  pdb.set_trace()

  try:
    cur.execute ("""INSERT INTO %s (datetime, price, high, low, volume, market_cap) VALUES (%s,%s,%s,%s,%s,%s);""", 
      (coin.name, coin.datetime, coin.price, coin.high, coin.low, coin.volume, coin.market_cap))
    db.commit()
  except:
    db.rollback()

  cur.close()
  db.close()


def database_to_dataframe(database):
  db = initialize_database(database)
  df_mysql = pd.read_sql('select * from bitcoin;', con=db)
  #df_mysql.set_index('datetime', inplace=True)

  db.close()

  return df_mysql

get_cryptocoin_market_data()

df = database_to_dataframe('sql-market-data')
print(df)


