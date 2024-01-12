from live_data import LiveStream
from series_predictor import PredictSeries
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import time
from datetime import datetime, timedelta
import threading

STOCKS = ['QQQ'] # 'BTC', 'VTI' 
INTERVALS = ['1 Minute'] # '5 Minutes', '10 Minutes'
THEMECOLOR = 'blue'

st.markdown(f"<h1 style='text-align: center; color: {THEMECOLOR};'>Stock Price Monitor</h1>", unsafe_allow_html=True)

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

# series predictor
if "predict_series" in st.session_state:
    predict_series = st.session_state.predict_series
else:
    predict_series = PredictSeries()
    st.session_state.predict_series = predict_series

# get new prediction flag
if "create_prediction" in st.session_state:
    create_prediction = st.session_state.create_prediction
else:
    create_prediction = False
    st.session_state.create_prediction = create_prediction

# cleanup resources on shutdown
def on_app_close():
    if "live_data_stream" in st.session_state:
        live_data_stream = st.session_state.live_data_stream
        live_data_stream.stop_websocket()
        print("Gracefully Ended Program!")

# button to kill and cleanup
if st.button("KILL PROGRAM"):
        on_app_close()

if st.button("Get New Prediction"):
    st.session_state.create_prediction = True

# get data from DS object
def fetch_data():
    return live_data_stream.get_data(), live_data_stream.get_current_price(), live_data_stream.get_open_price(), live_data_stream.get_last_interval_price()


def update_metric(current_price, open_price, price_str):
    delta = round(((current_price - open_price) / open_price) * 100, 2)
    delta = str(delta) + "%"
    metric_placeholder.metric("Price", price_str, delta=delta)


# update chart
graph_title = f"{selected_stock} ({selected_interval} Interval)"
while True:

    new_data, current_price, open_price, last_price = fetch_data()
    if not current_price:
        current_price = 0
    price_str = "$" + str(current_price)

    update_metric(current_price, open_price, price_str)

    if st.session_state.create_prediction:
        st.session_state.create_prediction = False
        prediction_thread = threading.Thread(target=predict_series.generate_prediction, args=(new_data, 15))
        prediction_thread.start()
        
    
    # Update the chart with the new data
    fig = px.line(new_data, x=0, y=1, title=graph_title, labels={0: 'Time', 1: 'Price'}, markers=True)
    fig.update_traces(
        hovertemplate='Time: %{x}<br>Price: %{y}',
        line=dict(color=THEMECOLOR),
        marker=dict(size=3)
    )

    new_prediction = predict_series.get_prediction()
    if new_prediction:
        fig.add_scatter(x=new_prediction[0], y=new_prediction[1], mode='lines', 
                        name='Smart Series Prediction', line=dict(color='rgba(218, 112, 214, 0.3)', width=7))

    # Update layout for panning and zooming
    fig.update_layout(
        title={
            'text': graph_title,
            'y': 0.9,
            'x': 0.01,
            'xanchor': 'left',
            'yanchor': 'top',
            'font': {
                'family': "Arial, sans-serif",
                'size': 24,
                'color': THEMECOLOR
            }
        },
        uirevision='constant',  # maintain user's interactions
        dragmode='pan',  # enable panning
        hovermode='closest',
        xaxis=dict(
            autorange=True,
            rangeslider=dict(visible=False),  # disable range slider
            tickformat='%I:%M %p',
            title="Time",
            title_font={"color": THEMECOLOR},
            tickfont={"color": THEMECOLOR}  
        ),
        yaxis=dict(
             autorange=True, 
             title="Price",
             title_font={"color": THEMECOLOR},
             tickfont={"color": THEMECOLOR} 
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.5,
            xanchor='center',
            x=0.5
        )
    )
    line_color = "green" if current_price >= last_price else "red"
    fig.add_hline(y=current_price, line_dash="dot", annotation_text=f"{price_str}", 
                  annotation_position="bottom right", line_color=line_color)

    # Configurations for enabling mouse wheel zoom
    config = {
        'staticPlot': False,
        'scrollZoom': True
    }

    chart_placeholder.plotly_chart(fig, use_container_width=True, config=config)

    # Update every second
    time.sleep(1)