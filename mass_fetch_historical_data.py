import codecs
import json
import os
import os.path
import urllib.request

def main():
    fetch_all_historical_data(json.load(open('stock_list3.txt')))

def fetch_stock_history(stock):
    """Loads historical data for a single stock from Yahoo YQL."""
    utf_decoder = codecs.getreader("utf-8")

    for year in reversed(range(2005, 2016)):
        year = str(year)
        start_date = year + "-01-01"
        end_date = year + "-12-31"
        stocks_base_URL = 'https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20yahoo.finance.historicaldata%20where%20symbol%20%3D%20'
        URL_end = '%20and%20startDate%20%3D%20%22' + start_date + '%22%20and%20endDate%20%3D%20%22' + end_date + '%22&format=json&diagnostics=true&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys&callback='

        query = stocks_base_URL + "%22" + stock + "%22" + "%2C"
        query = query[:-3] + URL_end
        api_response = urllib.request.urlopen(query)

        try:
            year_data = json.load(utf_decoder(api_response))['query']['results']['quote']
        except TypeError: # Means no stock data for the year.
            return
        path = "historical/" + stock + "/" + stock + "_" + year + ".txt"
        try:
            os.makedirs("historical/" + stock)
        except FileExistsError:
            pass
        open(path, "a") # Creates txt file if it doesn't exist.
        with open(path, 'w') as outfile:
            json.dump(year_data, outfile, indent = 2)

def fetch_all_historical_data(stock_list):
    """Loads historical data for all the stocks in list from Yahoo YQL."""
    for stock in stock_list:
        path = "historical/" + stock['symbol']
        if os.path.isdir(path): # Skip if data folder already exists.
            continue
        fetch_stock_history(stock['symbol'])
   
main()
