from live_data import LiveStream
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import time
from datetime import datetime, timedelta

STOCKS = ['QQQ'] # 'BTC', 'VTI' 
INTERVALS = ['1 Minute'] # '5 Minutes', '10 Minutes'

st.title("Stock Price Monitor")

# Create columns for the dropdowns
col1, col2, col3 = st.columns(3)
with col1:
    metric_placeholder = st.empty()
with col2:
    selected_stock = st.selectbox('Select Stock', STOCKS)
with col3:
    selected_interval = st.selectbox('Select Interval', INTERVALS)

chart_placeholder = st.empty()

# live data object
if "live_data_stream" in st.session_state:
    live_data_stream = st.session_state.live_data_stream
else:
    live_data_stream = LiveStream()
    st.session_state.live_data_stream = live_data_stream

# cleanup resources on shutdown
def on_app_close():
    if "live_data_stream" in st.session_state:
        live_data_stream = st.session_state.live_data_stream
        live_data_stream.stop_websocket()
        print("Gracefully Ended Program!")

# button to kill and cleanup
if st.button("KILL PROGRAM"):
        on_app_close()

# get data from DS object
def fetch_data():
    return live_data_stream.get_data(), live_data_stream.get_current_price(), live_data_stream.get_last_interval_price()

# update chart
while True:
    new_data, current_price, last_price = fetch_data()

    if not current_price:
         current_price = 0
    if not last_price:
         last_price = current_price
    
    delta = current_price - last_price
    price = "$" + str(current_price)
    metric_placeholder.metric("Price", price, delta=delta)

    # Update the chart with the new data
    fig = px.line(new_data, x=0, y=1, title="Stock Price Over Time (1-minute Interval)", labels={0: 'Time', 1: 'Price'}, markers=True)

    fig.update_traces(
        hovertemplate='Time: %{x}<br>Price: %{y}',
        line=dict(color='blue'),
        marker=dict(size=3)
    )

    # Update layout for panning and zooming
    fig.update_layout(
        uirevision='constant',  # maintain user's interactions
        dragmode='pan',  # enable panning
        hovermode='closest',
        xaxis=dict(
            autorange=True,
            rangeslider=dict(visible=False),  # disable range slider
            tickformat='%I:%M %p',
            title="Time"
        ),
        yaxis=dict(
             autorange=True, 
             title="Price"
        ),
    )

    # Configurations for enabling mouse wheel zoom
    config = {
        'staticPlot': False,
        'scrollZoom': True
    }

    chart_placeholder.plotly_chart(fig, use_container_width=True, config=config)

    # Update every second
    time.sleep(1)
