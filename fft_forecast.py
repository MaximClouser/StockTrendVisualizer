import numpy as np
import pandas as pd
from scipy.fft import fft, ifft

import yfinance as yf
import pytz

def fetch_historical_data():
    # df = yf.download(tickers=self.yahoo_symbol, period="5y", interval="1m", auto_adjust=True, prepost=False)
    stock = yf.Ticker("QQQ")
    # historical_data = stock.history(period="1d", interval="1m")
    historical_data = stock.history(period="5y", interval="1d")
    eastern = pytz.timezone('US/Eastern')
    historical_data.index = historical_data.index.tz_convert(eastern)
    return [(index, row['Close']) for index, row in historical_data.iterrows()]


def fft_forecast(data, N=1024, N_first=1, N_last=3, futureBars=50):
    # Forward FFT
    fft_values = fft(data, n=N)
    # Filtering based on selected frequency components
    filtered_fft = np.zeros_like(fft_values)
    for i in range(N_first, N_last + 1):
        if i < len(fft_values):
            filtered_fft[i] = fft_values[i]
            if i != 0:  # Mirror the frequency component for the negative frequencies
                filtered_fft[-i] = fft_values[-i]

    # Inverse FFT to get filtered time series
    filtered_time_series = ifft(filtered_fft)

    # Forecasting future values
    future_values = []
    for future_time in range(1, futureBars + 1):
        future_value = 0.0
        for j in range(N_first, N_last + 1):
            frequency = 2 * np.pi * j / N
            amplitude_re = filtered_fft[j].real
            amplitude_im = filtered_fft[j].imag
            future_value += amplitude_re * np.cos(frequency * future_time) - amplitude_im * np.sin(frequency * future_time)
        future_values.append(future_value)

    return filtered_time_series.real, future_values  # Return filtered series and future predictions

# Example usage:
# filtered_series, predictions = fft_forecast(data['Close'], N=256, N_first=1, N_last=36, futureBars=120)

data = fetch_historical_data()
print(len(data))
last_256 = data[-1024:]
data = [float(data_point[1]) for data_point in last_256]

filtered_series, predictions = fft_forecast(data)
print(predictions)