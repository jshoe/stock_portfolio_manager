from pprint import pprint
from prettytable import PrettyTable
from termcolor import colored, cprint
import codecs
import decimal
import getopt
import json
import sys
import time
import urllib.request

def quote_fetch(stock_list):
    """Get info for all stocks in list from Yahoo YQL."""
    utf_decoder = codecs.getreader("utf-8")
    stocks_base_URL = 'https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20yahoo.finance.quote%20where%20symbol%20in%20('
    URL_end = ')&format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys&callback='

    query = stocks_base_URL
    for stock in stock_list:
        query = query + "%22" + stock['symbol'] + "%22" + "%2C"
    query = query[:-3]
    query += URL_end
    api_response = urllib.request.urlopen(query)
    data = json.load(utf_decoder(api_response))['query']['results']['quote']
    return data

def fetch_stock_history(stock):
    """Loads historical data for a single stock from Yahoo YQL."""
    utf_decoder = codecs.getreader("utf-8")
    stocks_base_URL = 'https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20yahoo.finance.historicaldata%20where%20symbol%20%3D%20'
    URL_end = '%20and%20startDate%20%3D%20%222014-07-16%22%20and%20endDate%20%3D%20%222015-07-16%22&format=json&diagnostics=true&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys&callback='

    query = stocks_base_URL + "%22" + stock + "%22" + "%2C"
    query = query[:-3] + URL_end
    api_response = urllib.request.urlopen(query)
    historical_data = json.load(utf_decoder(api_response))['query']['results']['quote']
    return historical_data

def fetch_all_historical_data(stock_list):
    """Loads historical data for all the stocks in list from Yahoo YQL."""
    result = fetch_stock_history("YHOO")
    with open('historical/YHOO.txt', 'w') as outfile:
        json.dump(result, outfile, indent = 2)

def get_price(symbol, data):
    """Extract current price from Yahoo data."""
    for i in data:
        if i['symbol'] == symbol:
            return decimal.Decimal(i['LastTradePriceOnly'])

def make_table_default():
    """Make a new table with the default formatting."""
    table = PrettyTable(["Name", "Sym", "Ur Lo", colored("-Gap %", 'red'), colored("Cur $", 'cyan'), colored("+Gap %", 'green'), "Ur Hi", "Alrt", "LBP", "Flg", "Qt", "LTD", "Notes"])
    table.align = "r"
    table.align["Flg"] = "c"
    table.align["LBP"] = "c"
    table.align["LTD"] = "l"
    table.align["Name"] = "l"
    table.align["Notes"] = "l"
    table.align["Qt"] = "c"
    table.align["Sym"] = "l"
    return table

def fill_table_entry(s, data, table, mode):
    """Populate the table with financial data for the current entry."""
    alert = ""
    flag = s['flag']
    last_target_update = s['last_target_update']
    lbp = s['lim_buy_price']
    name = s['name']
    notes = s['notes']
    shares = s['shares']
    symbol = s['symbol']
    cur_price = get_price(symbol, data)
    
    your_low = round(decimal.Decimal(s['low_price']), 2) # Represents a good buying price.
    low_off = round(100 * (cur_price - your_low) / cur_price, 2)
    your_hi = round(decimal.Decimal(s['high_price']), 2) # Represents a good selling price.
    hi_off = round(100 * (your_hi - cur_price) / cur_price, 2)
    
    if mode == "full" and flag == '':
        return # Flag toggle.
    elif mode == "portfolio" and shares == "0":
        return

    cur_price = round(cur_price, 2)
    
    if cur_price < your_low:
        alert = "BUY"
    elif cur_price > your_hi and your_hi > 0:
        alert = "SELL"

    if shares == '0':
        shares = ''

    table.add_row([name, symbol, your_low, low_off, cur_price, hi_off, your_hi, alert, lbp, flag, shares, last_target_update, notes])

def print_charts(full, portfolio, sort_by):
    """Format and display the data view to the user."""
    print("")
    print("LBP (Limit Buy Price) - Buy price for limit orders placed.")
    print("LTD (Last Target Date) - Last time your price target was updated.")
    print("Ur Hi (Your High) - A good selling price for you.")
    print("Ur Lo (Your Low) - A good buying price for you.")
    print("\nWATCH LIST:")

    if sort_by == '-Gap' or sort_by == '':
        sort_by = colored("-Gap %", 'red')
    elif sort_by == 'Cur':
        sort_by = colored("Cur $", 'cyan')
    elif sort_by == '+Gap':
        sort_by = colored("+Gap %", 'green')

    full.sortby = sort_by
    portfolio.sortby = sort_by

    print(full)
    print("\nCURRENT HOLDINGS:")
    print(portfolio)

def parse_options(argv):
    """Process any command line arguments."""
    sort_by = ""
    try:
        opts, args = getopt.getopt(argv, "s:", ["sort_by="])
    except getopt.GetoptError:
        print("Argument error.")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-s", "--sort_by"):
             sort_by = arg
    return sort_by

def main():
    """Show user their default chart view."""
    sort_by = parse_options(sys.argv[1:])
    stock_list = json.load(open('stock_list3.txt'))
    data = quote_fetch(stock_list)
    full = make_table_default()
    portfolio = make_table_default()

    for s in stock_list:
        fill_table_entry(s, data, full, "full")
        fill_table_entry(s, data, portfolio, "portfolio")

    #fetch_all_historical_data(json.load(open('stock_list3.txt')))
    print_charts(full, portfolio, sort_by)

main()
