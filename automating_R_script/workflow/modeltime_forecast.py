# Import libraries ----

import yfinance as yf #financial data
import pandas as pd #data wrangling/manipulation
import subprocess as sp #calling R script in Python flow
import datetime #date handling out of R table
from prefect import task, flow #automation

# Def func to get data (part 1 separate steps) ----
@task(
    name="Extract Financial Data",
    retries=2,
    retry_delay_seconds=3
)
def extract_fin_prices(ticker: str = "BTC-USD", period: str = "6h", interval: str = "5m") -> pd.DataFrame:
    fin_data = yf.download(
        tickers = ticker,
        period = period,
        interval = interval
    )

    return fin_data

# Def func to store as csv ----
@task(
    name="Save Price Data as a File"
)
def save_to_csv(df: pd.DataFrame, path: str) -> None:
    df.to_csv(path_or_buf = path, index = True)

# Def func to run R script ----
@task(
    name="Run R modeltime script"
)
def modeltime_forecast(r_path: str = "../separate_steps/modeling.R") -> None:
    call_command = " ".join(["Rscript", r_path])
    res = sp.call(call_command, shell = True)
    return res

# Read in csv of forecasts and print out target price, pct change, and time ----
@task(
    name="Process Forecast and Return Summary"
)
def process_forecast(forecast_path: str = "../data/fin_forecast.csv") -> pd.DataFrame:
    forecast_df = pd.read_csv(forecast_path)
    time_calc = datetime.datetime.strptime(forecast_df.max(axis=0).Datetime, "%Y-%m-%dT%H:%M:%SZ").strftime("%H:%M:%S UTC on %m/%d/%y")
    max_val = forecast_df.iloc[-1]["Adj Close"]
    min_val = forecast_df.iloc[0]["Adj Close"]
    pct_delta = round(((max_val/min_val)-1)*100, ndigits = 2)
    raw_delta = round(max_val - min_val, ndigits=2)
    print(f"The R models forecast a {pct_delta}% (${raw_delta}) change from ${round(min_val, ndigits=2)} to ${round(max_val, ndigits=2)} by {time_calc}")

    return(forecast_df)

# Prefect Workflow ----
@flow(
    name="Financial Data Pipeline + Forecast",
    log_prints=True
)
def prefect_flow(
    tickers = "BTC-USD",
    period = "6h",
    interval = "5m",
    path = "C:/Users/cdawg/git_repos/py_hackaround/automating_R_script/data/fin_data.csv",
    r_path = "C:/Users/cdawg/git_repos/py_hackaround/automating_R_script/separate_steps/modeling.R",
    forecast_path = "C:/Users/cdawg/git_repos/py_hackaround/automating_R_script/data/fin_forecast.csv"
):
    print(f">>> Extracting financial information of {tickers}")
    fin_df = extract_fin_prices(ticker = tickers, period = period, interval = interval)
    print(f">>> Saving prices as a file at {path}")
    save_to_csv(fin_df, path)
    print(f">>> Modeling via R script at {r_path}")
    res_check = modeltime_forecast(r_path)
    print(f">>> Processing forecast data at {forecast_path}")
    forecast_df = process_forecast(forecast_path)


# MAIN PROGRAM RUN ----
if __name__ == "__main__":
    prefect_flow(
        tickers = "BTC-USD",
        period = "6h",
        interval = "5m",
        path = "C:/Users/cdawg/git_repos/py_hackaround/automating_R_script/data/fin_data.csv",
        r_path = "C:/Users/cdawg/git_repos/py_hackaround/automating_R_script/separate_steps/modeling.R",
        forecast_path = "C:/Users/cdawg/git_repos/py_hackaround/automating_R_script/data/fin_forecast.csv"
    )


# PREFECT BUILD STEPS ----
# prefect deployment build .\workflow\modeltime_forecast.py:prefect_flow --name test_flow --interval 60
# (set params in YAML)
# prefect deployment apply prefect_flow-deployment.yaml
# prefect deployment ls
# prefect deployment run "Financial Data Pipeline + Forecast/test_flow"
# prefect orion start (prefect server start) [orion was deprecasted in favor of server]
# prefect agent start --work-queue "default"