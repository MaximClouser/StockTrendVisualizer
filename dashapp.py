from live_data import LiveStream
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import yfinance as yf
import atexit



app = Dash(__name__)

live_stream = LiveStream()



app.layout = html.Div([
    html.Div(children='My First App with Data and a Graph'),
    dcc.Graph(id='main-graph'),
    dcc.Interval(
        id='interval-component',
        interval=1*500,  # in milliseconds 1*1000
        n_intervals=0
    )
])


@callback(Output('main-graph', 'figure'), Input('interval-component', 'n_intervals'))
def update_graph(n):
    # Fetch live data from the LiveStream instance
    live_data = live_stream.get_data() 
    print(live_data[-1])
    df = pd.DataFrame(live_data, columns=['Timestamp', 'Price'])

    # Plot the data
    fig = px.line(df, x='Timestamp', y='Price')
    return fig

# Function to close the WebSocket and release resources
def shutdown():
    live_stream.stop_websocket()
    print("Shutting down: WebSocket closed.")

# Register the shutdown function
atexit.register(shutdown)

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
    # try:
    #     app.run_server(debug=True)
    # except KeyboardInterrupt:
    #     print("Interrupted by user, shutting down...")