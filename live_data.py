# https://finnhub.io/pricing
# 60 calls / minute
import websocket
import json
import yfinance as yf
import threading
from datetime import datetime
from pandas import Timestamp
import time
import os
from dotenv import load_dotenv
import pytz

# load env
load_dotenv()

class LiveStream():

    def __init__(self):
        # constants:
        api_key = os.getenv('FINNHUB_API_KEY')
        self.url = "wss://ws.finnhub.io?token=" + api_key
        self.window = 100

        # yahoo
        self.yahoo_symbol = "BTC-USD"
        self.interval = "1m"
        self.period = "1d"
        self.time_zone = 'US/Eastern'

        #finnhub
        self.finnhub_symbol = "BINANCE:BTCUSDT"

        # initialize historic data
        self.data = self.fetch_historical_data()
        # print("HISTORY Start: ", self.data[0])
        # print("HISTORY END: ", self.data[-1])

        # update with live data websocket
        self.enable_stack_trace = False
        self.ws_app = None
        self.ws_thread = None
        self.start_websocket()


    def get_data(self):
        return self.data[-self.window:]
        
        
    def fetch_historical_data(self):
        # df = yf.download(tickers=self.yahoo_symbol, period="5y", interval="1m", auto_adjust=True, prepost=False)
        stock = yf.Ticker(self.yahoo_symbol)
        historical_data = stock.history(period = self.period, interval=self.interval)
        eastern = pytz.timezone(self.time_zone)
        historical_data.index = historical_data.index.tz_convert(eastern)
        return [(index, row['Close']) for index, row in historical_data.iterrows()]
    

    def add_data(self, data_point, raw_timestamp):
        # only for 1m as of now, need to adapt later!
        time = raw_timestamp % 6000
        if time == 0:
            self.data.append(data_point)
        else:
            self.data[-1] = data_point


    def on_message(self, ws, message):
        data = json.loads(message)
        if 'data' in data:
            for trade in data['data']:
                price = trade.get('p')
                raw_timestamp = trade.get('t')
                if price is not None and raw_timestamp is not None:
                    timestamp = Timestamp(raw_timestamp, unit='ms', tz=self.time_zone)
                    new_data_point = (timestamp, price)
                    self.add_data(new_data_point, raw_timestamp)


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
        self.ws_thread.start()


    def stop_websocket(self):
        if self.ws_app is not None:
            self.ws_app.close()
            self.ws_thread.join()
            print("Closed Websocket!")


if __name__ == '__main__':
    live = LiveStream()

    # print("DATA: ", live.data[-5:])

    time.sleep(120)

    # print("FRESH: ", live.data[-1])

    # print("DATA: ", live.data[-5:])

    # print(live.data[-60:])

    live.stop_websocket()

    # print("DATA: ", live.data[-5:])
