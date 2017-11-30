# import libraries
# coding: utf-8

import operator
import urllib2
from bs4 import BeautifulSoup

import pdb 

import re

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint

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

  #add btc to spreadsheet
  #btcPrice = sheet.cell(7,3).value
  sheet.update_cell(3, 3, prices['ETH'])
  sheet.update_cell(8, 3, prices['IOT'])
  sheet.update_cell(9, 3, prices['SUB'])
  sheet.update_cell(10, 3, prices['ZRX'])
  sheet.update_cell(11, 3, prices['SC'])

  print_positions(sheet)

def print_positions(sheet):

  print('\n    Frozen Positions:')

  print('ETH:    ' + sheet.cell(3,4).value + "   " + sheet.cell(3,5).value)
  #print('Total:  ' + sheet.cell(4,4).value + "   " + sheet.cell(4,5).value)

  print('\n    Liquid Positions:')

  print('IOT:    ' + sheet.cell(8,4).value + "      " + sheet.cell(8,5).value)
  print('SUB:    ' + sheet.cell(9,4).value + "      " + sheet.cell(9,5).value)
  print('ZRX:    ' + sheet.cell(10,4).value + "        " + sheet.cell(10,5).value)
  print('SC:     ' + sheet.cell(11,4).value + "      " + sheet.cell(11,5).value)
  print('Total:  ' + sheet.cell(12,4).value + "    " + sheet.cell(12,5).value)

  print('\nTotal: ' + sheet.cell(14,4).value + "  " +
   sheet.cell(14,5).value+'\n')

def print_prices(prices):

  print('\nCurrent Prices:')

  for name, price in prices:
    print (name + " : " + price)

def main_execute():
  prices = {'IOT':'', 'BTC':'', 'SC':'', 'ETH':'','ZRX':'','SUB':''}

  get_currencies_prices("https://coinmarketcap.com/all/views/all/", prices)

  sorted_prices = sorted(prices.items(), key=operator.itemgetter(1), reverse=True)
  print print_prices(sorted_prices)

  update_spreadsheet(prices)

main_execute()


