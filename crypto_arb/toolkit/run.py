import price_crawler as crawler
import time
import datetime

c = crawler.PriceCrawler()

while True:
    
    print(str(datetime.datetime.now()))
    c.execute(store_arb_history = True)
    time.sleep(60)
