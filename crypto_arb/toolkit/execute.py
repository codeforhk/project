import price_crawler as crawler
import slack
import pandas as pd
import yaml

with open('config.yaml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

pricecrawler = crawler.PriceCrawler()
sc = slack.WebClient(token = config['config']['slack_credentials'])

hb_price = pricecrawler.hb_get()
po_price = pricecrawler.po_get()
price_df = pd.concat([po_price, hb_price])
price_df.columns = ['ask_p','ask_v','bid_p','bid_v','currency','exchange','time']
price_df = price_df[['time','exchange','currency','ask_p','ask_v','bid_p','bid_v']]
sc.chat_postMessage(channel="#testing",text= price_df.to_string(), as_user = False) 