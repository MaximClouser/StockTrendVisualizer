# https://finnhub.io/pricing
# 60 calls / minute
import websocket
import json
import pandas as pd
import plotly.graph_objs as go
import yfinance as yf
import threading
from datetime import datetime

import os
from dotenv import load_dotenv

# load env
load_dotenv()

API = os.getenv('FINNHUB_API_KEY')

# Initialize a Plotly figure
fig = go.Figure()
fig.add_scatter()

stock_data = {
    "timestamps": [],
    "prices": []
}


def update_plot(timestamp, price):
    print("UPDATED")
    stock_data["timestamps"].append(timestamp)
    stock_data["prices"].append(price)

    # Redefine the plot with updated data
    fig.data = []
    fig.add_scatter(x=stock_data["timestamps"], y=stock_data["prices"], mode='lines')



def on_message(ws, message):
    data = json.loads(message)
    if 'data' in data:
        for trade in data['data']:
            price = trade.get('p')
            timestamp = trade.get('t')
            if price is not None and timestamp is not None:
                timestamp = datetime.fromtimestamp(timestamp / 1000)
                # update_plot(timestamp, price)
                print(timestamp, price)


def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")
    print("Close status code:", close_status_code)
    print("Close message:", close_msg)

def on_open(ws):
    ws.send('{"type":"subscribe","symbol":"BINANCE:BTCUSDT"}')
    # ws.send('{"type":"subscribe","symbol":"BINANCE:BTC"}')
    # ws.send('{"type":"subscribe","symbol":"BINANCE:BTC/USD"}')
    # ws.send('{"type":"subscribe","symbol":"AMZN"}')
    # ws.send('{"type":"subscribe","symbol":"QQQ"}')
    # ws.send('{"type":"subscribe","symbol":"NASDAQ:QQQ"}')



def fetch_historical_data(symbol, period="1mo", interval="1m"):
    """
    Fetch historical stock data using Yahoo Finance.

    :param symbol: Stock symbol, e.g., 'AAPL' for Apple Inc.
    :param period: Data period to download (e.g., '1d', '1mo', '1y')
    :param interval: Data interval (e.g., '1m', '5m', '1d')
    :return: Pandas DataFrame containing historical stock data
    """
    stock = yf.Ticker(symbol)
    historical_data = stock.history(period=period, interval=interval)
    return historical_data



def start_websocket():
    websocket.enableTrace(enable_stack_trace)
    url = "wss://ws.finnhub.io?token=" + API
    ws = websocket.WebSocketApp(url, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
    ws.run_forever()


if __name__ == "__main__":
    historical_data = fetch_historical_data("BTC-USD", "1d", "1m")
    if not historical_data.empty:
        timestamps = historical_data.index.to_pydatetime()
        prices = historical_data['Close']
        for timestamp, price in zip(timestamps, prices):
            update_plot(timestamp, price)

    # thread = threading.Thread(target=start_websocket)
    # thread.start()

    # Display the plot
            
    fig.show()
    start_websocket()


    # try:
    #     while True:
    #         pass
    # except KeyboardInterrupt:
    #     print("Stopping WebSocket thread...")
    #     thread.join()
    #     print("Exited cleanly")
