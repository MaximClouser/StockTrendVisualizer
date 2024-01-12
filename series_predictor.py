import os
import pandas as pd
from nixtlats import TimeGPT
from dotenv import load_dotenv

load_dotenv()


class PredictSeries():


    def __init__(self):

        api_key = os.getenv('TIMEGPT_TOKEN')
        self.timegpt = TimeGPT(token=api_key)
        self.prediction = None


    def get_prediction(self):
        return self.prediction


    def clean(self, data):
        # convert to df
        df = pd.DataFrame(data, columns=['ds', 'y'])
        # Format the 'ds' column to match the API's expected datetime format
        df['ds'] = df['ds'].dt.strftime('%Y-%m-%d %H:%M:%S%z')
        # Convert 'ds' column to datetime objects
        df['ds'] = pd.to_datetime(df['ds'])
        # Set 'ds' as the index
        df.set_index('ds', inplace=True)
        # Resample to one-minute intervals and fill missing values with the previous row
        # df = df.resample('T').ffill()
        # Reset the index and rename the columns if needed
        df.reset_index(inplace=True)
        return df


    def generate_prediction(self, data, horizon=15, finetune_steps=None):
        # remove gaps / duplicates
        df = self.clean(data)
        # get prediction
        timegpt_fcst_with_history_df = self.timegpt.forecast(df=df, h=horizon, finetune_steps=100, time_col='ds', target_col='y', add_history=True, freq='min')
        # convert predicted data frame to time and price lists
        times = timegpt_fcst_with_history_df['ds'].tolist()
        prices = timegpt_fcst_with_history_df['TimeGPT'].tolist() 
        # save
        self.prediction = times, prices
