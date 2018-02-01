# import libraries
# coding: utf-8

import MySQLdb
import mysql

import operator
import urllib2
from bs4 import BeautifulSoup

import pdb 

import re

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint

from ConfigParser import SafeConfigParser

config = SafeConfigParser()
config.read('../Config/config.ini')

class Coin:

  def __init__(self):
    self.name = ''
    self.ticker = ''
    self.price = 0
    self.percent_change = 0
    self.daily_high = 0
    self.daily_low = 0
    self.daily_volume = 0
    self.market_cap = 0

  
def initializeDatabase():
  try:
    db = MySQLdb.connect(host=config.get('sql', 'host'),
              user=config.get('sql', 'user'),
              passwd=config.get('sql', 'passwd'),
              db=config.get('sql', 'sql-mckinley-holdings'))
    print('Database initialized!')
  except ValueError:
    print('Error connecting to database!')
  
  return db

def databaseToDataframe(database):
  df_mysql = pd.read_sql('select * from data;', con=database)
  df_mysql.set_index('time', inplace=True)
  return df_mysql

def get_currencies_prices(url, currencyPrices):

  currencies_page = url
  curr_page = urllib2.urlopen(currencies_page)
  currency_soup = BeautifulSoup(curr_page, "html.parser")

  iota_box = currency_soup.find("a", attrs={"href": "/currencies/iota/#markets"})
  iota_price = iota_box.text.strip() 
  currencyPrices.update({'IOT':iota_price})

  siacoin_box = currency_soup.find("a", attrs={"href": "/currencies/siacoin/#markets"})
  siacoin_price = siacoin_box.text.strip() 
  currencyPrices.update({'SC':siacoin_price})

  ethereum_box = currency_soup.find("a", attrs={"href": "/currencies/ethereum/#markets"})
  ethereum_price = ethereum_box.text.strip() 
  currencyPrices.update({'ETH':ethereum_price})

  bitcoin_box = currency_soup.find("a", attrs={"href": "/currencies/bitcoin/#markets"})
  bitcoin_price = bitcoin_box.text.strip()
  currencyPrices.update({'BTC':bitcoin_price})

  bitcoin_box = currency_soup.find("a", attrs={"href": "/currencies/bitcoin/#markets"})
  bitcoin_price = bitcoin_box.text.strip() 
  currencyPrices.update({'BTC':bitcoin_price})

  substratum_box = currency_soup.find("a", attrs={"href": "/currencies/substratum/#markets"})
  substratum_price = substratum_box.text.strip() 
  currencyPrices.update({'SUB':substratum_price})

  zerox_box = currency_soup.find("a", attrs={"href": "/currencies/0x/#markets"})
  zerox_price = zerox_box.text.strip() 
  currencyPrices.update({'ZRX':zerox_price})

def update_spreadsheet(prices):

  print ('\n...calculating positions...')

  #pdb.set_trace()

  scope = ['https://spreadsheets.google.com/feeds']
  creds = ServiceAccountCredentials.from_json_keyfile_name('../Config/sheets.json', scope)
  client = gspread.authorize(creds)

  sheet = client.open('Crypto Positions').sheet1

  #pdb.set_trace()
  '''
  sheet_jason = client.open('Crypto Positions - Jason Marsh').sheet1

  sheet_jason.update_cell(2, 2, prices['BTC'])
  sheet_jason.update_cell(3, 2, prices['ETH'])
  sheet_jason.update_cell(4, 2, prices['IOT'])
  sheet_jason.update_cell(5, 2, prices['SUB'])

  sheet_linde = client.open('Crypto Positions - Linde Wang').sheet1

  sheet_linde.update_cell(3, 3, prices['IOT'])
  sheet_linde.update_cell(4, 3, prices['ETH'])
  '''

  sheet.update_cell(2, 2, prices['BTC'])
  sheet.update_cell(3, 2, prices['ETH'])
  sheet.update_cell(4, 2, prices['IOT'])
  sheet.update_cell(5, 2, prices['SUB'])
  sheet.update_cell(6, 2, prices['SC'])

  print_positions(sheet)

def print_positions(sheet):

  print('\n    IRA Positions:')

  print('ETH:    ' + sheet.cell(10,4).value + "   " + sheet.cell(10,5).value)
  print('Total:  ' + sheet.cell(11,4).value + "    " + sheet.cell(11,5).value)

  print('\n    Holding Positions:')

  print('IOT:    ' + sheet.cell(15,4).value + "   " + sheet.cell(15,5).value)
  print('SUB:    ' + sheet.cell(16,4).value + "   " + sheet.cell(16,5).value)
  print('SC:     ' + sheet.cell(17,4).value + "   " + sheet.cell(17,5).value)
  print('Total:  ' + sheet.cell(18,4).value + "    " + sheet.cell(18,5).value)

  print('\n    Short Term Positions:')

  print('IOT:    ' + sheet.cell(22,4).value + "      " + sheet.cell(22,5).value)
  print('IOT:    ' + sheet.cell(23,4).value + "      " + sheet.cell(23,5).value)
  print('IOT:    ' + sheet.cell(24,4).value + "      " + sheet.cell(24,5).value)
  print('SUB:    ' + sheet.cell(25,4).value + "      " + sheet.cell(25,5).value)
  print('SC:     ' + sheet.cell(26,4).value + "      " + sheet.cell(26,5).value)
  print('Total:  ' + sheet.cell(27,4).value + "    " + sheet.cell(27,5).value)

  print('\nTotal: ' + sheet.cell(29,4).value + "  " +
   sheet.cell(29,5).value+'\n')

def print_prices(prices):

  print('\nCurrent Prices:')

  for name, price in prices:
    print (name + " : " + price)

def main_execute():
  prices = {'IOT':'', 'BTC':'', 'SC':'', 'ETH':'','ZRX':'','SUB':''}

  get_currencies_prices("https://coinmarketcap.com/all/views/all/", prices)

  sorted_prices = sorted(prices.items(), key=operator.itemgetter(1), reverse=True)
  #print print_prices(sorted_prices)

  update_spreadsheet(prices)

main_execute()

#get_cryptocoin_market_data("https://www.worldcoinindex.com/")


