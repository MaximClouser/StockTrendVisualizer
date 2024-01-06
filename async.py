import dashapp
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import plotly.graph_objs as go
import pandas as pd
import threading
import yfinance as yf
import websocket
import json
from datetime import datetime


API = "cmcnu91r01qjutgrvbagcmcnu91r01qjutgrvbb0"

# Initialize stock data
stock_data = {
    "timestamps": [],
    "prices": []
}

# Dash app setup
app = dashapp.Dash(__name__)
app.layout = html.Div([
    dcc.Graph(id='live-graph', animate=True),
    dcc.Interval(
        id='graph-update',
        interval=1*1000,  # in milliseconds
        n_intervals=0
    ),
])

@app.callback(
    Output('live-graph', 'figure'),
    [Input('graph-update', 'n_intervals')]
)
def update_graph_scatter(n):
    trace = go.Scatter(
        x=list(stock_data["timestamps"]),
        y=list(stock_data["prices"]),
        name='Scatter',
        mode= 'lines+markers'
    )

    return {'data': [trace],
            'layout': go.Layout(
                xaxis=dict(range=[min(stock_data["timestamps"]), max(stock_data["timestamps"])]),
                yaxis=dict(range=[min(stock_data["prices"]), max(stock_data["prices"])])
            )}

# WebSocket functions
def on_message(ws, message):
    data = json.loads(message)
    if 'data' in data:
        for trade in data['data']:
            price = trade.get('p')
            timestamp = trade.get('t')
            if price is not None and timestamp is not None:
                timestamp = datetime.fromtimestamp(timestamp / 1000)
                stock_data["timestamps"].append(timestamp)
                stock_data["prices"].append(price)

def start_websocket():
    websocket.enableTrace(True)
    url = "wss://ws.finnhub.io?token=" + API
    ws = websocket.WebSocketApp(url, on_message=on_message)
    ws.run_forever()

if __name__ == '__main__':
    # Run WebSocket in a separate thread
    thread = threading.Thread(target=start_websocket)
    thread.start()

    # Run Dash app
    app.run_server(debug=True)
