# Crypto-Trading-AI

An artificial intelligence to trade cryptocurrency based off future market predictions constructed from historical market data, relevant financial trends, and social media metrics. This project includes a collection of miscellaneous python scripts for cryptocurrency investing, trading, and data analysis.

*This project is currently under development*

### Description

The MarketStreamer class is used to store current ETH/USD market prices into a MySQL database at regular intervals. The price data is extracted by the DataProcessor class, which calculates financial statistics such as the simple moving average, estimated moving average, and several bollinger volitility bands over a specified time period and plots the result. The TradingAdvisor class then implements algorithms on top of the processed dataset to reccomend buy/sell trades on the ETH/USD market. Then, the Bot class connects directly to the exchange and facilitates the reccomended trade.  

### Configuration

Rename the example configuration file `config_template.ini` to `config.ini`.

Update `config.ini` with your local SQL database's information to store and access saved prices. Currently, MarketStreamer saves three strings into the table 'ethereum', using the database configuration found under 'gdax-market-data'.

Update `config.ini` with your exchange's api key and login information to both stream current prices and execute live trades on the market. Be careful about exposing your private information - do not fork this repository, update your information, and then push it to a public repository.

This project was developed with Python 3.6.4.

### Setup

After cloning the repository, start MarketStreamer to populate your database with current ETH/USD prices:
```
python market_streamer.py
```

Once your database has been populated, run TradingAdvisor with
```
python trading_advisor.py
``` 

*WARNING: The bot will execute realtime trades on the ethereum mainnet if instructed to - be careful with your money.*

Execute trades on GDAX with the Bot class:
```
python gdax_bot.py
```