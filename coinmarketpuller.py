# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 22:26:01 2021

@author:
"""

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import pandas as pd

url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
parameters = {
'id':'1,1027,2,74,52,2,2010,1975,512'
}
headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': ',
}

session = Session()
session.headers.update(headers)

import sqlite3
conn = sqlite3.connect('TestDB1.db',timeout = 10)
c = conn.cursor()
#c.execute('CREATE TABLE prices (data_symbol,data_slug,time,price_usd,volume)')
conn.commit()

try:
  response = session.get(url, params=parameters)
  data = json.loads(response.text)
  data["data"] = [data["data"][k] for k in data["data"].keys()]
  x=pd.json_normalize(pd.json_normalize(data).explode("data").to_dict(orient="records"))
  for index,x in x.iterrows():
      c.execute('insert into prices(data_symbol,data_slug,time,price_usd,volume) values (?,?,?,?,?)',
                (x['data.symbol'],x['data.slug'],x['status.timestamp'],x['data.quote.USD.price'],
                 x['data.quote.USD.volume_24h']))
      conn.commit()
except (ConnectionError, Timeout, TooManyRedirects) as e:
  print(e)
  
  
data = c.execute('select * from prices')
data = pd.DataFrame(data)
print(data)
