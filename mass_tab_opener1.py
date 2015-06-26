import webbrowser
import json

def main():
    stock_list = json.load(open('stock_list2.txt'))
    b = webbrowser.get('firefox')

    for stock in stock_list:
        symbol = stock['symbol']
        b.open('https://www.google.com/finance?q=' + symbol)

main()
