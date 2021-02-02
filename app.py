# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 17:39:01 2021

@author: jorda
"""

import pandas as pd
import datetime as dt
import sqlite3
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ALL
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
coins = ['dogecoin','bitcoin','ethereum','xrp','litecoin','cardano','chainlink','stellar']
col_names = ['data_symbol','data_slug','time','price_usd','volume']
conn = sqlite3.connect('TestDB1.db',timeout = 10)
c = conn.cursor()


def generate_backdata():
    data = c.execute('select * from comments')
    data = pd.DataFrame(data,columns=['id','body','created_datetime','score'])
    data['body'] = data['body'].str.lower()
    data['dogecoin'] = data['body'].str.contains('doge')
    data['bitcoin'] =data['body'].str.contains('btc|bitcoin')
    data['ethereum'] =data['body'].str.contains('eth|ethereum')
    data['xrp'] = data['body'].str.contains('xrp|ripple')
    data['polkadot']= data['body'].str.contains('dot|polkadot')
    data['litecoin']= data['body'].str.contains('ltc|litecoin')
    data['cardano']= data['body'].str.contains('ada|cardano')
    data['chainlink']= data['body'].str.contains('chainlink')
    data['stellar']= data['body'].str.contains('xlm|stellar')
    data['created_datetime'] = data['created_datetime'].apply(lambda x: dt.datetime.utcfromtimestamp(x))
    data['trunc_date'] = data['created_datetime'].dt.floor('h')
    return data

def generate_coin_specific_data(coin):
    price_data = c.execute('select * from prices where data_slug = "' + coin +'"')
    price_data = pd.DataFrame(price_data)
    price_data.columns = col_names
    price_data['time']=pd.to_datetime(price_data['time'])
    price_data['trunc_date'] = price_data ['time'].dt.floor('h')
    price_data = price_data.groupby(['trunc_date','data_slug'])['price_usd'].mean()
    price_data = price_data.reset_index()
    over_time = generate_backdata().groupby(['trunc_date',coin])['body'].count()
    over_time = over_time.reset_index()
    over_time = over_time[over_time[coin]]
    over_time['trunc_date'] = pd.to_datetime(over_time['trunc_date'],utc = True)
    over_time_final = pd.merge(over_time,price_data,how = 'left',left_on ='trunc_date', right_on = 'trunc_date')
    return over_time_final

def plotter(var):
    #pltz = px.bar(generate_coin_specific_data(var), x="trunc_date", y="body", labels = {'trunc_date':'Comment Time','body':'Count of Comments'},color=var)
    df = generate_coin_specific_data(var)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    
    fig.add_trace(
        go.Bar(
            x=df['trunc_date'],
            y=df['body'],
            
        ),
        secondary_y = False
        )
    fig.add_trace(
        go.Scatter(
            x=df['trunc_date'],
            y=df['price_usd']
        ),secondary_y = True)
    min_range = df['price_usd'].min()*0.1
    max_range = df['price_usd'].max()*1.5
    print(min_range)
    fig.update_xaxes(title_text = 'Time')
    fig.update_yaxes(range=[min_range,max_range],secondary_y=True)


    return fig


def generate_table(dataframe, max_rows = 10):
       return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])

def plot_charts_all(coins):
    lis = []
    for coin in coins:
        fig = plotter(coin)
        lis.append(html.H4(children = 'Posts mentioning ' + coin))
        lis.append(
                dcc.Graph(
                id=coin,
                figure=fig))
        lis.append(
            dcc.Interval(
            id= {'type':'input_type','id':coin},
            interval=1*30000, # in milliseconds
            n_intervals=0))
    return lis



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div( children = html.Div(plot_charts_all(coins)))

@app.callback(
    Output({
        'type': 'input-type',
        'id': ALL
    }, 'figure'),
    [Input({'type':'input_type','id':ALL}, 'n_intervals')])
def update_graph(n):
    return plot_charts_all(coins)


if __name__ == '__main__':
     app.run_server()