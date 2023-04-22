# Import libraries ----

import yfinance as yf #financial data
import pandas as pd #data wrangling/manipulation
import datetime

# Read in csv of forecasts and print out target price, pct change, and time ----

forecast = pd.read_csv("../data/fin_forecast.csv")

max_date = forecast.max(axis=0).Datetime
min_date = forecast.min(axis=0).Datetime

time_calc = datetime.datetime.strptime(max_date, "%Y-%m-%dT%H:%M:%SZ").strftime("%H:%M:%S UTC on %m/%d/%y")

max_val = forecast.iloc[-1]["Adj Close"]
min_val = forecast.iloc[0]["Adj Close"]

pct_delta = round(((max_val/min_val)-1)*100, ndigits = 2)
raw_delta = round(max_val - min_val, ndigits=2)

print(f"The R models forecast a {pct_delta}% (${raw_delta}) change from {round(min_val, ndigits=2)} to {round(max_val, ndigits=2)} by {time_calc}")



def process_forecast(forecast_path: str = "../data/fin_forecast.csv") -> pd.DataFrame:
    forecast_df = pd.read_csv(forecast_path)
    time_calc = datetime.datetime.strptime(forecast_df.max(axis=0).Datetime, "%Y-%m-%dT%H:%M:%SZ").strftime("%H:%M:%S UTC on %m/%d/%y")
    max_val = forecast_df.iloc[-1]["Adj Close"]
    min_val = forecast_df.iloc[0]["Adj Close"]
    pct_delta = round(((max_val/min_val)-1)*100, ndigits = 2)
    raw_delta = round(max_val - min_val, ndigits=2)
    print(f"The R models forecast a {pct_delta}% (${raw_delta}) change from {round(min_val, ndigits=2)} to {round(max_val, ndigits=2)} by {time_calc}")

    return(forecast_df)

process_forecast()