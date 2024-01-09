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
        # self.yahoo_symbol = "BTC-USD"
        self.yahoo_symbol = "QQQ"
        self.interval = "1m"
        self.period = "1d"
        self.time_zone = 'US/Eastern'

        #finnhub
        # self.finnhub_symbol = "BINANCE:BTCUSDT"
        self.finnhub_symbol = "QQQ"

        # initialize historic data
        self.open_price = None
        self.data = self.fetch_historical_data()
        self.current_data_point = self.data[-1]
        self.last_interval_data_point = self.current_data_point
        self.last_minute = self.current_data_point[0].minute

        # update with live data websocket
        self.enable_stack_trace = False
        self.ws_app = None
        self.ws_thread = None
        self.start_websocket()


    def get_open_price(self):
        return self.open_price
    

    def get_last_interval_price(self):
        if self.last_interval_data_point:
            return float(self.last_interval_data_point[1])
        

    def get_current_price(self):
        if self.current_data_point:
            return float(self.current_data_point[1])
        

    def get_data(self):
        return self.data
    
        
    def fetch_historical_data(self):
        # df = yf.download(tickers=self.yahoo_symbol, period="5y", interval="1m", auto_adjust=True, prepost=False)
        stock = yf.Ticker(self.yahoo_symbol)
        historical_data = stock.history(period=self.period, interval=self.interval)
        eastern = pytz.timezone(self.time_zone)
        historical_data.index = historical_data.index.tz_convert(eastern)
        self.open_price = historical_data.iloc[0]['Open'] if not historical_data.empty else None
        return [(index, row['Close']) for index, row in historical_data.iterrows()][-self.window:] # trim to window size
    
    
    def is_closing_point(self, time_stamp):
        # only for 1m as of now, need to adapt later!
        if self.interval == "1m":
            # print(data_point, raw_timestamp%6000)
            if time_stamp.minute != self.last_minute:
                self.last_minute = time_stamp.minute
                return True
        return False


    def add_data(self, data_point, raw_timestamp):
        self.current_data_point = data_point
        if self.is_closing_point(data_point[0]):
            self.data.append(data_point)
            self.last_interval_data_point = data_point
        else:
            self.data[-1] = data_point

        if len(self.data) > self.window:
            self.data.pop(0)


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
        print(f"WebSocket error: {error}")


    def on_close(self, ws, close_status_code, close_msg):
        print("Close status code:", close_status_code)
        print("Close message:", close_msg)


    def on_open(self, ws):
        subscription_message = json.dumps({"type": "subscribe", "symbol": self.finnhub_symbol})
        ws.send(subscription_message)


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

    time.sleep(5)
    live.get_current_price()

    # print("FRESH: ", live.data[-1])

    # print("DATA: ", live.data[-5:])

    # print(live.data[-60:])

    live.stop_websocket()

    # print("DATA: ", live.data[-5:])
