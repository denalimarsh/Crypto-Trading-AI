import pdb
import ccxt
import pprint
import time

pp = pprint.PrettyPrinter(indent=1)

print('\n                   IOT/USD Market on Bitfinex:')

exchange = ccxt.bitfinex () 
exchange.load_markets ()

#pdb.set_trace()

iota_ticker = exchange.fetch_ticker('IOTA/BTC')

#pp.pprint(iota_ticker)

high = str(iota_ticker['high'])
low = str(iota_ticker['low'])
last = str(iota_ticker['last'])
quote_volume = str(iota_ticker['quoteVolume'])
#duration = str(iota_ticker['timestamp'])

pp.pprint('Current: $' + last + ' Period: 24 hours' + ' High: $' + high + ' Low: $' + 
	low + ' Volume: $' + quote_volume)
	 #+ ' Volume: $' + quote_volume
	 

print('\n                       OrderBook:')

delay = 2
count = 0
while(count < 100):
	count += 1
	orderbook = exchange.fetch_order_book ('IOTA/USD')
	bid = orderbook['bids'][0][0] if len (orderbook['bids']) > 0 else None
	ask = orderbook['asks'][0][0] if len (orderbook['asks']) > 0 else None
	spread = (ask - bid) if (bid and ask) else None
	print ('Bid:', bid, 'Ask:', ask, 'Spread:', "%.8f" % spread)
	time.sleep(delay)

#15 min ticks, 20 short average 42 long
