# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 17:17:59 2021

@author: jorda
"""

import praw
import pandas as pd
import datetime as dt
import sqlite3
conn = sqlite3.connect('TestDB1.db')
c = conn.cursor()
#c.execute('CREATE TABLE comments (id,body,created_datetime,score)')
conn.commit()
pd.set_option("display.max_colwidth", 100000)
reddit = praw.Reddit(client_id='JKuwICzPpSy0Ow' , client_secret= 'T3p1P7pdZ8x5opxv9RNOVHKdeOxsIw',user_agent='JFTESTEROO')
stream = reddit.subreddit('Cryptocurrency').stream.comments(skip_existing=True)

for x in stream:
    c.execute('insert into comments(id,body,created_datetime,score) values (?,?,?,?)',(x.id,x.body,x.created_utc,x.score))
    conn.commit()
    print(x.id)
