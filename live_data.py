# https://finnhub.io/pricing
# 60 calls / minute
import websocket
import json
import pandas as pd
import plotly.graph_objs as go
import yfinance as yf
import threading
from datetime import datetime

class LiveStream():

    def __init__(self):
        # constants:
        self.API_KEY = "cmcnu91r01qjutgrvbagcmcnu91r01qjutgrvbb0"
        self.url = "wss://ws.finnhub.io?token=" + self.API_KEY
        self.enable_stack_trace = False

        # yahoo
        self.yahoo_symbol = "BTC-USD"
        self.interval = "1m"
        self.start_date = "2024-1-05"
        self.end_date = "2024-1-06"

        #finnhub
        self.finnhub_symbol = "BINANCE:BTCUSDT"

        # initialize historic data
        self.data = self.fetch_historical_data()

        # update with live data
        self.ws_app = None
        self.ws_thread = None
        self.start_websocket()

        
    def fetch_historical_data(self):
        stock = yf.Ticker(self.yahoo_symbol)
        historical_data = stock.history(start=self.start_date, end=self.end_date, interval=self.interval)
        return [(index, row['Close']) for index, row in historical_data.iterrows()]


    def on_message(self, ws, message):
        data = json.loads(message)
        if 'data' in data:
            for trade in data['data']:
                price = trade.get('p')
                timestamp = trade.get('t')
                if price is not None and timestamp is not None:
                    timestamp = datetime.fromtimestamp(timestamp / 1000)
                    self.data.append((timestamp, price))
                    # return price, timestamp


    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws, close_status_code, close_msg):
        print("Close status code:", close_status_code)
        print("Close message:", close_msg)

    def on_open(self, ws):
        subscription_message = json.dumps({"type": "subscribe", "symbol": self.finnhub_symbol})
        ws.send(subscription_message)
        # ws.send('{"type":"subscribe","symbol":"AMZN"}')
        # ws.send('{"type":"subscribe","symbol":"QQQ"}')
        # ws.send('{"type":"subscribe","symbol":"NASDAQ:QQQ"}')

    def start_websocket(self):
        websocket.enableTrace(self.enable_stack_trace)
        self.ws_app = websocket.WebSocketApp(self.url, on_message=self.on_message, on_error=self.on_error, on_close=self.on_close, on_open=self.on_open)
        self.ws_thread = threading.Thread(target=self.ws_app.run_forever)
        # threading.Thread(target=self.ws_app.run_forever).start()
        self.ws_thread.start()


    def stop_websocket(self):
        if self.ws_app is not None:
            self.ws_app.close()
            self.ws_thread.join()


if __name__ == '__main__':
    live = LiveStream()