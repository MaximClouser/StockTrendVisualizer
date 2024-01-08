from live_data import LiveStream
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import time
from datetime import datetime, timedelta


st.title("Stock Price Monitor")
metric_placeholder = st.empty()
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


# with st.sidebar:
#     st.subheader("Current Price")
#     # Display the current price or data here
#     st.text("$100.00")  # Replace this with your actual price data

#     # Add buttons in the sidebar panel
#     if st.button("Button 1"):
#         st.write("Button 1 was clicked!")

#     if st.button("Button 2"):
#         st.write("Button 2 was clicked!")




# update chart
while True:

    new_data, current_price, last_price = fetch_data()
    # st.session_state["df"] = pd.concat([st.session_state["df"], new_data])
    if not current_price:
         current_price = 0
    if not last_price:
         last_price = current_price
    
    delta = current_price - last_price
    price = "$" + str(current_price)
    metric_placeholder.metric("Price", price, delta=delta)

    # Update the chart with the new data
    fig = px.line(new_data, x=0, y=1, title="Stock Price Over Time", labels={0: 'Time', 1: 'Price'}, markers=True)

    fig.update_traces(hovertemplate='Time: %{x}<br>Price: %{y}')

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






# from live_data import LiveStream
# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import numpy as np
# import time
# from datetime import datetime, timedelta


# st.title("Stock Price Monitor")
# chart_placeholder = st.empty()

# # live data object
# if st.session_state.live_data_stream in st.session_state:
#     live_data_stream = st.session_state.live_data_stream
# else:
#     live_data_stream = LiveStream()
#     st.session_state.live_data_stream = live_data_stream


# # Initialize session state
# if "df" not in st.session_state:
#     # Initial dataset with a starting date and price
#     start_date = datetime.now().date() - timedelta(days=30)  # 30 days ago
#     start_price = 100  # Starting price of the stock
#     st.session_state["df"] = pd.DataFrame({
#         'date': [start_date],
#         'price': [start_price]
#     })




# def fetch_new_data(latest_date, latest_price):
#     # Simulating the next date
#     next_date = latest_date + timedelta(days=1)

#     # Simulating the price change
#     price_change = np.random.uniform(-1, 1)  # Random float between -1 and 1
#     next_price = max(latest_price + price_change, 0.01)  # Ensure price doesn't go below 0.01

#     return pd.DataFrame({'date': [next_date], 'price': [next_price]})




# while True:
#     # Get the latest date and price
#     latest_date = st.session_state["df"]['date'].iloc[-1]
#     latest_price = st.session_state["df"]['price'].iloc[-1]

#     # Update data
#     new_data = fetch_new_data(latest_date, latest_price)
#     st.session_state["df"] = pd.concat([st.session_state["df"], new_data])

#     # Update the chart with the new data
#     fig = px.line(st.session_state["df"], x="date", y="price", title="Stock Price Over Time", markers=True)

#     # Update layout for panning and zooming
#     fig.update_layout(
#         uirevision='constant',  # maintain user's interactions
#         dragmode='pan',  # enable panning
#         xaxis=dict(
#             autorange=True,
#             rangeslider=dict(visible=False),  # disable range slider
#         ),
#         yaxis=dict(autorange=True),
#     )

#     # Configurations for enabling mouse wheel zoom
#     config = {
#         'staticPlot': False,
#         'scrollZoom': True
#     }

#     chart_placeholder.plotly_chart(fig, use_container_width=True, config=config)

#     # Update every second (or your desired frequency)
#     time.sleep(1)

