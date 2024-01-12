# StockTrendVisualizer  
(Under Construction)  

About:  
A real time stock price monitor providing live prices and trend prediction using time series prediction from Nixtla.
Future additions will include real-time prediction capability from custom trained time series transformer models (exploring Autoformer and Informer models)  

Install requirements:  
`pip install -r requirements.txt`

Create a `.env` file with Nixtla and Finnhub API keys:  
`FINNHUB_API_KEY = <Your_Finnhub_key>`  
`TIMEGPT_TOKEN = <Your_nixtl_key>`

Acquire keys (should be free): https://docs.nixtla.io/ and https://finnhub.io/docs/api/introduction  

Run:  
`streamlit run app.py`