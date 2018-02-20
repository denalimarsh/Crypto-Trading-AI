# coding=utf-8

import decimal

import urllib.request
import urllib.error
import winsound
from bs4 import BeautifulSoup

import jsbeautifier
import pdb 
import time
import re
import sys

import pynput
from pynput.mouse import Button, Controller

import win32api
import win32con

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint

from configparser import SafeConfigParser

config = SafeConfigParser()
config.read('../Config/config.ini')

class WebBot:

  def __init__(self):
    self.tx_hashes = self.load_trades()
    self.country_count = self.check_my_countries()

  def access_website(self, url):

    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
         'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
         'Accept-Encoding': 'none',
         'Accept-Language': 'en-US,en;q=0.8',
         'Connection': 'keep-alive'}


    req = urllib.request.Request(url, headers=hdr)
    
    try:
      html = urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
      print(e.fp.read())

    soup = BeautifulSoup(html, "html.parser")

    return soup

  def check_my_countries(self):

    etherscan_html = self.access_website('https://etherscan.io/token/0x92cB5F1FbabbcbDd891B9Cbd8E9a056c8c1eEbEF?a=0x053a12c6db0c0ca74bce3673d8e760c72a3fd078')
    full_text = etherscan_html.find("table", attrs={"class": "table"})

    count_string= ''
    for element in full_text(text=re.compile(r'\d CCC')):
      count_string = element.parent
    
    non_decimal = re.compile(r'[^\d.]+')
    count = non_decimal.sub('', '{}'.format(count_string))

    return int(count)

  def get_contract_trs(self):
    table1 = self.access_website('https://etherscan.io/txs?a=0x92cB5F1FbabbcbDd891B9Cbd8E9a056c8c1eEbEF')
    table2 = table1.find('tbody')
    contracts = table2.find_all('tr')
    return contracts

  def load_trades(self):
    contracts = self.get_contract_trs()
    tx_hashes = []

    for contract in contracts:
      tx_hash = contract.find('span', attrs={'class':'address-tag'})
      tx_hashes.append('{}'.format(tx_hash.text))

    return tx_hashes

  def check_world_countries(self):

    table1 = self.access_website('https://etherscan.io/txs?a=0x92cB5F1FbabbcbDd891B9Cbd8E9a056c8c1eEbEF')
    table2 = table1.find('tbody')
    contracts = table2.find_all('tr')

    eth_regex = re.compile(r'.*Ether')

    for contract in contracts:
      tx_hash = contract.find('span', attrs={'class':'address-tag'})

      #pdb.set_trace()

      #For new trades:
      if tx_hash.text not in self.tx_hashes:

        #Get ETH amount
        td_tags = contract.find_all('td')
        eth_amount = td_tags[len(td_tags)-2].text

        #Trade confirmed or denied?
        fail_title = contract.find('font', attrs={'title':'TxReceipt Status FAIL'})
        if fail_title != None:
          title_text = fail_title.attrs['title']
          if title_text == 'TxReceipt Status FAIL':
            print('Failed transaction for {}'.format(eth_amount))
        else:
          print('Country traded for {}'.format(eth_amount))

        #add to tx hash list
        self.tx_hashes.append('{}'.format(tx_hash.text))

  def notify(self):
    print('Country Traded!')
    winsound.PlaySound('audio/GameShowWheel.wav', winsound.SND_FILENAME)
    winsound.PlaySound('audio/ChaChing.wav', winsound.SND_FILENAME)

def start_stream(delay):
    print('starting stream...')

    bot = WebBot()

    while True:
      curr_count = bot.check_my_countries()

      if curr_count != bot.country_count:
        bot.notify()
        bot.country_count = curr_count
      else:
        print('Countries: {}'.format(bot.country_count))

      bot.check_world_countries()

      time.sleep(delay)

start_stream(500)

'''
def buy_cheapest_country():

  mouse = Controller()

  #price arrow
  mouse.position = (3430, 800)
  mouse.press(Button.left)
  mouse.release(Button.left)

  mouse.move(-110, 30)
  mouse.press(Button.left)
  mouse.release(Button.left)

  time.sleep(1)

  #scroll down (using scroll-bar)
  mouse.position = (3830, 40)
  mouse.press(Button.left)
  mouse.move(0, 10)
  mouse.release(Button.left)

  
  #price ascending
  mouse.position = (3325, 829)
  mouse.press(Button.left)
  mouse.release(Button.left)

  #scroll down
  mouse.scroll(0, 4)

  #buy button (cheapest country)
  mouse.position = (2497, 909)
  mouse.press(Button.left)
  mouse.release(Button.left)
  
'''