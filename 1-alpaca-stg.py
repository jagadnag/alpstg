#!/usr/bin/env python

import alpaca_trade_api as tradeapi
import time
import requests
import json
import schedule

key_id='PK5XD8GNLWGZR54MF0EZ'
secret_key='R7ti/gvk9mwSalLNUpHEyhTFYz0i5MSrpCSYsx7w'

api = tradeapi.REST(
    key_id,
    secret_key,
    'https://paper-api.alpaca.markets', api_version='v2'
)

webhook_url = 'https://hooks.slack.com/services/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'

#stock_list = ['SPY','AAPL', 'MSFT', 'TTD', 'LULU', 'ROKU', 'TLT', 'GLD', 'IAU', 'QQQ', 'AMD', 'TSLA' 'XLK', 'XLF', 'XLY', 'XLI', 'XLB', 'XLC', 'XLRE', 'XLV', 'XLU', 'XLP']

stock_list = ['SPY','AAPL', 'MSFT', 'AMD', 'XLK', 'XLF', 'XLY', 'XLI', 'XLB', 'XLC', 'XLRE', 'XLV', 'XLU', 'XLP']
price_alert = {}

# Get our account information.
account = api.get_account()

# Check if our account is restricted from trading.
if account.trading_blocked:
    print('Account is currently restricted from trading.')

# Check how much money we can use to open new positions.
print('${} is available as buying power.'.format(account.buying_power))

# Check our current balance vs. our balance at the last market close
balance_change = float(account.equity) - float(account.last_equity)
print(f'Today\'s portfolio balance change: ${balance_change}')

def main():
    # Check if the market is open now.
    clock = api.get_clock()
    print('The market is {}'.format('open.' if clock.is_open else 'closed.'))

    if clock.is_open == False:
        print("Market is not yet open.. waiting")
        time.sleep(60*60)
        main()
        
    while clock.is_open == True:
        # Check all the stocks in the stock list
        for stock in stock_list:
            barset = api.get_barset(stock, '15Min', limit=16)
            stock_bars = barset[stock]
        
            # See how much stock moved in that timeframe.
            hour_open = stock_bars[0].o
            hour_close = stock_bars[-1].c
            percent_change = (hour_close - hour_open) / hour_open * 100
            percent_change = round(percent_change, 2)
    
            price_alert [stock] = percent_change
            #print('{} moved {}% over the last 8hrs'.format(stock, percent_change))
            #msg = {'text': '{} moved {}% over the last 8hrs'.format(stock, percent_change)}
            #requests.post(webhook_url, data=json.dumps(msg))
            
            # If stock moving up, 10 positions are taken
            if percent_change > 1.0:
                print('Taking long position on {}'.format(stock))
                symbol = stock
                api.submit_order(
                symbol= stock,
                qty=10,
                side='buy',
                type='market',
                time_in_force='gtc'
                )
            # If stock not moving up, no positions are taken
            #elif percent_change > -1.0:
                #if current_position == True:
                  #liquidate positon
                  #if no_positions_left
                      #pass  
            else:
                pass
        print(price_alert)
        msg = {'text': 'TRADE_ALERT > {}'.format(price_alert)}
        requests.post(webhook_url, data=json.dumps(msg))
    
        # Wait for 60 mins
        print('Sleeping for 60min...')    
        time.sleep(60*60)
        
        # Starting the loop again, if market is open
        print('-' * 60)
        print('Starting the Algo..')
        print('-' * 60)
        clock = api.get_clock()
        if clock.is_open == False:
            print('Market is close for today..')

if __name__ == "__main__":
	main()
