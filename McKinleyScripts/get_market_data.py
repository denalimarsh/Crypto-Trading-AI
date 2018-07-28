# coding=utf-8

import MySQLdb
import decimal
import operator
import urllib.request
import urllib.error
from bs4 import BeautifulSoup
import pdb 
from datetime import datetime
import re
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint
from configparser import SafeConfigParser

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


  req = urllib.request.Request(url, headers=hdr)
  
  try:
    cryptocoin_html = urllib.request.urlopen(req)
  except urllib.error.HTTPError as e:
    print(e.fp.read())

  cryptocoin_soup = BeautifulSoup(cryptocoin_html, "html.parser")

  return cryptocoin_soup

def coin_setup():
  curr_time = datetime.now()

  #aurora_dao
  coins = []
  coin_names = ['bitcoin', 'ethereum', 'iota', 'substratum', '0x', 'icon', 'oysterpearl', 'ethorse', 'aelf', 'trac']


  for coin in coin_names:
    new_coin = Coin()
    new_coin.name = coin
    new_coin.datetime = curr_time
    coins.append(new_coin)

  return coins

def strip_to_float(object):
  non_decimal = re.compile(r'[^\d.]+')
  return float(non_decimal.sub('', object))

def get_coinmarketcap_data(coin):
  
  coinmarketcap_soup = ''

  if coin.name == 'ethorse':
    coinmarketcap_soup = access_website('https://coinmarketcap.com/currencies/ethorse/')
  elif coin.name == 'trac':
    coinmarketcap_soup = access_website('https://coinmarketcap.com/currencies/origintrail/')
  elif coin.name == 'jibrel':
    coinmarketcap_soup = access_website('https://coinmarketcap.com/currencies/jibrel-network/')
  elif coin.name == 'bitboost':
    coinmarketcap_soup = access_website('https://coinmarketcap.com/currencies/bitboost/')
  elif coin.name == 'auroradao':
    coinmarketcap_soup = access_website('https://coinmarketcap.com/currencies/aurora-dao/')
  else:
    print('Error: {} not found on Coin Market Cap.'.format(coin.name))

  #get price
  market_data = coinmarketcap_soup.find("div", attrs={"class": "col-lg-10"})
  current_price_data = market_data.find("span", attrs={"id": "quote_price"})
  current_price = current_price_data.get('data-usd')
  current_price_float = strip_to_float(current_price)
  coin.price = current_price_float

  '''
  #get market cap, volume
  subset_market_data = coinmarketcap_soup.find("div", attrs={"class": "row bottom-margin-2x"})
  market_cap_data = subset_market_data.find("span", attrs={"data-currency-market-cap"})
  market_cap = market_cap_data.get('data-usd')
  market_cap_float = strip_to_float(market_cap)
  coin.market_cap = market_cap_float
  '''

  return coin

def strip_cryptocoin_data(coin, market_data):

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

    return coin


def get_cryptocoin_market_data():

  #Open cryptocoin website
  cryptocoin_soup = access_website('https://www.worldcoinindex.com/')

  #Set up coins with names
  coins = coin_setup()

  print('Time: {}'.format(coins[0].datetime))
  
  #Get cryptocoin HTML block
  for coin in coins:
    market_data = cryptocoin_soup.find("tr", attrs={"data-naam": "{}".format(coin.name)})
    page_number = 0

    #Search cryptocoin HTML for coin name
    while market_data == None and page_number <= 5:
      page_number += 1
      circular_cryptocoin_soup = access_website('https://www.worldcoinindex.com/{}'.format(page_number))
      market_data = circular_cryptocoin_soup.find("tr", attrs={"data-naam": "{}".format(coin.name)})

    #if coin not found, search coinmarketcap
    if market_data == None:
      #print('\'{}\' not found on cryptocoin => searching coinmarketcap...'.format(coin.name, page_number))
      coin = get_coinmarketcap_data(coin)

      if coin.price == None:
        print('\'{}\' price not found on coinmarketcap.'.format(coin.name))

    else:
      coin = strip_cryptocoin_data(coin, market_data)

    #print(coin)

  print('Coin market data collected!\n')

  update_spreadsheet(coins)
  #store_market_data(coins)

def update_spreadsheet(coins):

  print ('\n...calculating positions...')

  scope = ['https://spreadsheets.google.com/feeds']
  creds = ServiceAccountCredentials.from_json_keyfile_name('../Config/sheets.json', scope)
  client = gspread.authorize(creds)

  sheet = client.open('Crypto Positions').sheet1
  sheet_linde = client.open('Crypto Positions - Linde Wang').sheet1

  for index, coin in enumerate(coins):
    coin = coins[index]
    row_number = sheet_switch(coin.name)
    row_number_linde = sheet_linde_switch(coin.name)

    if coin.price != 0 and row_number != 0:
      sheet.update_cell(row_number, 3, coin.price)

    if coin.price != 0 and row_number_linde != 0:
      sheet_linde.update_cell(row_number_linde, 3, coin.price)

  #print_positions(sheet)

def sheet_linde_switch(x):
  return{
    'ethereum': 4,
    'iota': 3,
    'substratum': 6,
    'icon': 5
  }.get(x, 0)

def sheet_switch(x):
  return{
    'bitcoin': 2,
    'ethereum': 3,
    'iota': 4,
    'substratum': 5,
    '0x': 6,
    'auradao': 7,
    'icon': 8, 
    'oysterpearl': 9,
    'bounty0x': 10,
    'ethorse': 11,
    'jibrel': 12,
    'aelf': 13,
    'trac': 14
  }.get(x, 0)

def store_market_data(coins):

  db = initialize_database('crypto-investments')

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

def print_positions(sheet):

  print('\n    IRA Positions:')
  print('ETH:    ' + sheet.cell(19,4).value + "   " + sheet.cell(19,5).value)

  print('\n    Holding Positions:')

  print('IOT:    ' + sheet.cell(25,4).value + "   " + sheet.cell(25,5).value)
  print('ICX:    ' + sheet.cell(26,4).value + "   " + sheet.cell(26,5).value)
  print('ZRX:    ' + sheet.cell(27,4).value + "   " + sheet.cell(27,5).value)
  print('ELF:    ' + sheet.cell(28,4).value + "   " + sheet.cell(28,5).value)
  print('TRAC:   ' + sheet.cell(29,4).value + "   " + sheet.cell(29,5).value)
  print('SUB:    ' + sheet.cell(33,4).value + "   " + sheet.cell(33,5).value)
  print('PRL:    ' + sheet.cell(34,4).value + "   " + sheet.cell(34,5).value)
  print('SHL:    ' + sheet.cell(35,4).value + "   " + sheet.cell(34,5).value)
  print('HORSE:  ' + sheet.cell(37,4).value + "   " + sheet.cell(37,5).value)
  print('HORSE:  ' + sheet.cell(38,4).value + "   " + sheet.cell(38,5).value)
  print('AURA:   ' + sheet.cell(39,4).value + "   " + sheet.cell(39,5).value)

  print('\n    Liquid Positions:')

  print('USD:    '  + sheet.cell(45,5).value)
  print('ETH:    '  + sheet.cell(46,5).value)

  #total_holdings = int(re.sub(r'\W+', '', (sheet.cell(40,5).value))) + int(re.sub(r'\W+', '', (sheet.cell(47,5).value)))

 # print('\nInvestments:  ' + str(total_holdings))

get_cryptocoin_market_data()

#df = database_to_dataframe('sql-market-data')
#print(df)


