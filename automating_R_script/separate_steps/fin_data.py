# Get data from yfinance ----

## Import packages ----
import yfinance as yf
import pandas as pd

## Get data ----
fin_data = yf.download(
    tickers = "CVX",
    period = "3h",
    interval = "5m"

)

## Write data to csv for R access ----
pd.DataFrame(fin_data).to_csv("../data/fin_data.csv")
