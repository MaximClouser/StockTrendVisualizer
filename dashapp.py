from live_data import LiveStream
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import yfinance as yf


app = Dash(__name__)

live_stream = LiveStream()

# def fetch_historical_data(symbol="BTC-USD", interval="1m", start_date="2024-1-05", end_date="2024-1-06" ):
#     """
#     Fetch historical stock data using Yahoo Finance.

#     :param symbol: Stock symbol, e.g., 'AAPL' for Apple Inc.
#     :param interval: Data interval (e.g., '1m', '5m', '1d')
#     :return: Pandas DataFrame containing historical stock data
#     """
#     stock = yf.Ticker(symbol)
#     historical_data = stock.history(start=start_date, end=end_date, interval=interval)
#     return historical_data


app.layout = html.Div([
    html.Div(children='My First App with Data and a Graph'),
    dcc.Graph(id='main-graph'),
    dcc.Interval(
        id='interval-component',
        interval=1*1000,  # in milliseconds
        n_intervals=0
    )
])


@callback(Output('main-graph', 'figure'), Input('interval-component', 'n_intervals'))
def update_graph(n):
    # Fetch live data from the LiveStream instance
    live_data = live_stream.get_data() 
    df = pd.DataFrame(live_data, columns=['Timestamp', 'Price'])

    # Plot the data
    fig = px.line(df, x='Timestamp', y='Price')
    return fig


# @callback(Output('main-graph', 'figure'), Input('interval-component', 'n_intervals'))
# def update_graph(n):

#     if n == 0:# initial call
#         df = fetch_historical_data()
#     else:
#         df = fetch_historical_data()
    
#     fig = px.line(df, x=df.index, y='Close')
#     return fig


if __name__ == '__main__':
    # app.run(debug=True)

    try:
        app.run_server(debug=True)
    except KeyboardInterrupt:
        # Handle the keyboard interrupt (Ctrl+C)
        live_stream.stop_websocket()
        print("Interrupted by user, shutting down...")
    # finally:
    #     # Ensure WebSocket is closed when the app stops
    #     live_stream.stop_websocket()
    #     print("WebSocket closed.")