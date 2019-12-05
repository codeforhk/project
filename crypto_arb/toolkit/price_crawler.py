import os
import time
import requests
import pandas as pd
import io
import datetime
import yaml
import slack

class PriceCrawler():
    
    '''
    This code gets price from two exchanges.
    
    Example:
        pc = PriceCrawler()
        pc.po_get() # Gets price from polonix
        pc.hb_get() # Gets price from huobi
        pc.get_arb() # Compares and check for arbitrage opportunities
        pc.find_arb( 'etcbtc', price_df) # Gets 
    
    '''
    
    def __init__(self):
        with open('config.yaml') as file:
            self.config = yaml.load(file, Loader=yaml.FullLoader)
    
    def po_get(self):
        
        '''
        Code to get price from poloniex
        '''
        
        tics = ['BTC_ETH','BTC_ETC']
        prices = []
        for ticker in tics:
            a = eval(requests.get(self.config['config']['polonix'].format(ticker)).content)
            tic = ticker.lower().replace('btc','').replace('_','').replace('neos','neo')+'btc'
            df = [a['asks'][0][0], a['asks'][0][1], a['bids'][0][0],a['bids'][0][1],tic,'po']
            df = pd.DataFrame([df])
            t = datetime.datetime.now()
            df['time'] = t
            prices.append(df)
        print(str(t) + '  ' + 'get price from Polonix')

        return pd.concat(prices)

    def hb_get(self):
        
        '''
        Code to get price from Huobi
        '''
        
        tics = ['ethbtc', 'etcbtc']
        prices = []
        for ticker in tics:
            r = requests.get(self.config['config']['huobi'].format(ticker))
            temp = eval(r.content)['tick']
            df = pd.DataFrame(temp['asks'][0]+temp['bids'][0]+[ticker,'hb']).transpose()
            t = datetime.datetime.now()
            df['time'] = t
            prices.append(df)
            
        print(str(t) + '  ' + 'get price from Huobi')
        
        return pd.concat(prices)
    
    def find_arb(self, currency, price_df):
        price_comparison = price_df[price_df.currency==currency]
        min_ask = min(price_comparison.ask_p.astype(float))
        max_bid = max(price_comparison.bid_p.astype(float))
        if min_ask<max_bid:
            
            print('Arbitrage opporuntiy for {}'.format(currency))
            
            return(price_comparison)
        else:
            
            print('No arbitrage opporuntiy for {}'.format(currency))
            
            return(price_comparison.head(0))    
    
    def execute(self, notify = False, store_price_history = False, store_arb_history = False):
        sc = slack.WebClient(token = self.config['config']['slack_credentials'])

        hb_price = self.hb_get()
        po_price = self.po_get()
        price_df = pd.concat([po_price, hb_price])
        price_df.columns = ['ask_p','ask_v','bid_p','bid_v','currency','exchange','time']
        price_df = price_df[['time','exchange','currency','ask_p','ask_v','bid_p','bid_v']]
        arb_df = pd.concat([self.find_arb(i, price_df) for i in ['etcbtc','ethbtc']])
        
        path = os.path.dirname(os.getcwd())+'/data'
        self.price_df = price_df
        
        if store_price_history:
            
            with open(path+'/price_history.csv', 'a') as f:
                price_df.to_csv(f, header=False)

        if len(arb_df)>0:
            
            if store_arb_history:
                with open(path+'/arb_history.csv', 'a') as f:
                    arb_df.to_csv(f, header=False)
            
            if notify:
                sc.chat_postMessage(channel="#testing",text= price_df.to_string(), as_user = False)
        