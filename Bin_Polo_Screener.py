# Welcome to my cryptocurrency arbitrage tracker for Binance and Poloniex

# We will be using the following libraries (API wrappers), which you should download and install before using this script

# 1) Binance API Wrapper for Python: https://python-binance.readthedocs.io/en/latest/
# Type the following into your console, in order to install: python -m pip install python-binance
# Else: Download repository from Github and copy binance folder into project

# 2) Poloniex API Wrapper for Python: https://github.com/s4w3d0ff/python-poloniex
# For all API Methods, see: https://poloniex.com/support/api/
# Type the following into your console, in order to install: python -m pip install https://github.com/s4w3d0ff/python-poloniex/archive/v0.4.7.zip
# Else: Download repository from Github and copy binance folder into project

# You will need to create a Public and Private key to access the Binance and Poloniex APIs and utilize their full potential. Do this before using this script
# and save the keys in the keys.json file that is included.

from binance.client import Client
import json
import os.path, math
from poloniex import Poloniex, Coach
import re
import sys
myCoach = Coach(timeFrame=1.0, callLimit=6) # creates a coach that stops me from breaking the 6 pings a sec limit of the Poloniex API



#+++++++++++++++++++++++++++++++++++++++++++++++ USER INPUT +++++++++++++++++++++++++++++++++++

#Choose the percentage difference that should exist between cryptocurrencies on the two exchanges, before they are displayed in the console by the script (1 = 1%).
perc_diff = 1.0

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# The exit function is meant to kill the script, if an error occurs
def exit():
    print("KILLED.")
    sys.exit()
    return

# The underscore function inserts an underscore into the Binance ticker,in order for us to compare their tickers with those of Poloniex.
# The function searches for one of the four currencies that are used to trade on Binance into all other currencies (BTN, BTC, USDT, ETH)
# and then inserts the underscore in front of it.
def add_underscore(ticker):
    sep = "_"
    format_check = re.search(r"USDT", ticker)
    if format_check:
        firstpart = ticker[:-4]
        secondpart = ticker[-4:]
        new_pair = firstpart + sep + secondpart
        return new_pair
    else:
        firstpart = ticker[:-3]
        secondpart = ticker[-3:]
        new_pair = firstpart + sep + secondpart
        return new_pair

# The swapper function swaps two tickers in a market label (BTC_LTC becomes LTC_BTC), in order to account for differences between APIs
def swapper(word):
    return "_".join(word.split("_")[::-1])



# We define the json file as a variable and check if it is in the same path as our .py file. The Json file stores our Private and Public keys for the Poloniex and
# Binance APIs.
datafilename = "keys.json"
if(os.path.isfile(datafilename) == False):
    print("data file does not exist.\n")
    exit()


# Define a variable that loads the JSON file storing my public and private keys
dataf = json.load(open(datafilename))

# Define variables that simplify the process of making API requests. I'm passing my Public and Private keys into the "Client" and "Poloniex" functions included in the Binance and Python libraries. The "couch" stops me from making more than 6 requests per second.
bin_client = Client(dataf["Binance"]["Public"], dataf["Binance"]["Secret"])
polo_client = Poloniex(key=dataf["Poloniex"]["Public"], secret=dataf["Poloniex"]["Secret"], coach=myCoach)


# Defines two variables that contain the JSON lists of cryptocurrency tickers and their respective highest/lowests bids/asks. These can
# be parsed by us, in order to compare matching cryptocurrency pairs. We need to match all markets first though (see below)
polo_crypto_markets = polo_client.returnTicker()
bin_crypto_markets = bin_client.get_orderbook_tickers()

# Loops through every cryptocurrency pair trading on poloniex and compares it to every pair available on Binance
for polo_market in polo_crypto_markets:
    for bin_market in bin_crypto_markets:

        # Due to differing formatting conventions, we add an underscore ("_") to the pair, in order to match Binance's with Poloniex's formatting
        bin_mkt_formated = add_underscore(bin_market["symbol"])

        # We also swap the order of the market (i.e. BTC_LTC to LTC_BTC) in order to not miss any pairs
        bin_mkt_swapped = swapper(bin_mkt_formated)

        # We check whether the formated or swapped version of the Binance market matches the Poloniex market and use that market's bid and ask to calculate
        # the difference between the markets
        bin_mkt = None
        if polo_market == bin_mkt_formated:
            bin_mkt = bin_mkt_formated
        elif polo_market == bin_mkt_swapped:
            bin_mkt = bin_mkt_swapped
        else:
            continue


        # Calculates the absolute percentage difference between the lowest Ask available on one exchange (at which you buy) and the highest Bid (at which you can sell).
        # It compares this absolute percentage difference to the predefined cut-off at which a trade is profitable for the user. If true, a print statement posts the
        # currency pair and the amount of percent that can be made.
        buy_bin_sell_polo = 100*abs(float(bin_market["bidPrice"])-float(polo_crypto_markets[polo_market]["lowestAsk"]))/(float(polo_crypto_markets[polo_market]["lowestAsk"]))
        buy_polo_sell_bin = 100*abs(float(polo_crypto_markets[polo_market]["highestBid"])-float(bin_market["askPrice"]))/(float(bin_market["askPrice"]))

        if buy_bin_sell_polo >= perc_diff:
            print("BUY " + polo_market + " on Poloniex: " + polo_crypto_markets[polo_market]["lowestAsk"] + " and SELL on Binance: " + bin_market["askPrice"] + ". " + str(round(buy_bin_sell_polo,4)) + "% Percentage difference.")
        elif buy_polo_sell_bin >= perc_diff:
            print("BUY " + bin_mkt + " on Binance: " + bin_market["askPrice"]  + " and SELL on Poloniex: " + polo_crypto_markets[polo_market]["highestBid"] + ". " + str(round(buy_polo_sell_bin,4)) + "% Percentage difference.")



# Conclusion:
# Hope you can use this script in conjunction with a fee calculator to scout out cryptocurrency pairs that make for profitable trading opportunities.

# Possible improvements:

# 1) Check whether markets are OPEN or UNDER MAINTENANCE

# 2) Incorporate the DEPTH of the markets by counting bid and ask quantities, until they match your trade volume. Here is my code:

"""
if buy_bin_sell_polo >= perc_diff:
        polo_depth_btc = polo_client.returnOrderBook("polo_market")
        for ask in polo_depth_btc["asks"]:
            liquidity += float(ask[1])
            if liquidity >= polo_balance_usdt:
                execute_ask = float(ask[0])
                polo_client.buy("polo_market", execute_ask, (polo_balance_usdt/execute_ask))
                print("Sold " + str(polo_balance_usdt) + " USDT at ask: " + str(execute_ask) + " for " + polo_market + ".")
                liquidity = 0

"""

# 3) Take a look at the withdraw fees on each exchange before trading:
# Poloniex: https://www.anythingcrypto.com/exchange-withdrawal-fees/poloniex
# Binance: https://www.anythingcrypto.com/exchange-withdrawal-fees/binance

# 4) Take into account the trading fees on each exchange:
# Poloniex: https://poloniex.com/fees/
# Binance: https://support.binance.com/hc/en-us/articles/115000429332-Fee-Structure-on-Binance

# If you make a ton of money, feel free to leave a tip ;)
# BTC: 3ENEzBEUgNgrSchcVxoN7Xz6MKo6daiMf4
# ETH: 0xee566d86877001Aab039FA2A2508B5bB59d3cF25





