import codecs
import decimal
import json
from prettytable import PrettyTable
import time
import urllib.request
import sys
from termcolor import colored, cprint

# Yahoo YQL API stuff
utf_decoder = codecs.getreader("utf-8")
stocks_base_URL = 'https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20yahoo.finance.quote%20where%20symbol%20in%20('
URL_end = ')&format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys&callback='

def quote_fetch(stock_list):
    """Get info for all stocks in list from Yahoo YQL."""
    query = stocks_base_URL
    for stock in stock_list:
        query = query + "%22" + stock['symbol'] + "%22" + "%2C"
    query = query[:-3]
    query += URL_end
    api_response = urllib.request.urlopen(query)
    data = json.load(utf_decoder(api_response))['query']['results']['quote']
    return data

def get_price(symbol, data):
    """Extract current price from Yahoo data."""
    for i in data:
        if i['symbol'] == symbol:
            return decimal.Decimal(i['LastTradePriceOnly'])

def make_table_default():
    """Make a new table with the default formatting."""
    table = PrettyTable(["Name", "Sym", "Ur Lo", colored("-Gap %", 'red'), colored("Cur $", 'cyan'), colored("+Gap %", 'green'), "Ur Hi", "Alrt", "LBP", "Flg", "Qt", "LTD", "Notes"])
    table.align = "r"
    table.align["Name"] = "l"
    table.align["Sym"] = "l"
    table.align["Notes"] = "l"
    table.align["Qt"] = "c"
    table.align["Flg"] = "c"
    table.align["LBP"] = "c"
    table.align["LTD"] = "l"
    return table

def fill_table_entry_full(s, data, table):
    """Populate the table with financial data for the current entry."""
    name = s['name']
    flag = s['flag']
    symbol = s['symbol']
    cur_price = get_price(symbol, data)
    alert = ""
    shares = s['shares']
    notes = s['notes']
    lbp = s['lim_buy_price']
    last_target_update = s['last_target_update']
    
    if flag == '':
        return # Flag toggle.
    
    your_low = round(decimal.Decimal(s['low_price']), 2) # Represents a good buying price.
    low_off = round(100 * (cur_price - your_low) / cur_price, 2)
    your_hi = round(decimal.Decimal(s['high_price']), 2) # Represents a good selling price.
    hi_off = round(100 * (your_hi - cur_price) / cur_price, 2)
    
    cur_price = round(cur_price, 2)
    
    if cur_price < your_low:
        alert = "BUY!"
    elif cur_price > your_hi and your_hi > 0:
        alert = "SELL!"

    if shares == '0':
        shares = ''

    table.add_row([name, symbol, your_low, low_off, cur_price, hi_off, your_hi, alert, lbp, flag, shares, last_target_update, notes])

def fill_table_entry_portfolio(s, data, table):
    """Populate table with data for current entry with owned shares."""
    shares = s['shares']
    if shares == '0':
        return
    name = s['name']
    symbol = s['symbol'] 
    alert = ""
    lbp = s['lim_buy_price']
    flag = s['flag']
    notes = s['notes']
    last_target_update = s['last_target_update']
    cur_price = get_price(symbol, data)

    your_low = round(decimal.Decimal(s['low_price']), 2) # Represents a good buying price.
    low_off = round(100 * (cur_price - your_low) / cur_price, 2)
    your_hi = round(decimal.Decimal(s['high_price']), 2) # Represents a good selling price.
    hi_off = round(100 * (your_hi - cur_price) / cur_price, 2)
    
    cur_price = round(cur_price, 2)
    
    if cur_price < your_low:
        alert = "BUY!"
    elif cur_price > your_hi and your_hi > 0:
        alert = "SELL!"
    
    table.add_row([name, symbol, your_low, low_off, cur_price, hi_off, your_hi, alert, lbp, flag, shares, last_target_update, notes])    

def print_charts(full, portfolio):
    """Format and display the data view to the user."""
    print("\nLBP = Limit Buy Price - Buy price for limit orders placed.")
    print("\nWATCH LIST:")
    #full.sortby = "Symbol"
    full.sortby = colored("-Gap %", 'red')
    #full.sortby = "Name"
    print(full)
    portfolio.sortby = colored("-Gap %", 'red')
    print("\nCURRENT HOLDINGS:")
    print(portfolio)

def main():
    stock_list = json.load(open('stock_list3.txt'))
    data = quote_fetch(stock_list)
    full = make_table_default()
    portfolio = make_table_default()

    for s in stock_list:
        fill_table_entry_full(s, data, full)
        fill_table_entry_portfolio(s, data, portfolio)

    print_charts(full, portfolio)

main()
