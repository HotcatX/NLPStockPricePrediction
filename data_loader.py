import requests
import pandas as pd

API_KEY = "9SMJWT4DNUDBHM80"

url = "https://www.alphavantage.co/query"
params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": "SPY",
    "apikey": API_KEY
}

res = requests.get(url, params=params)
data = res.json()

# error handling
if "Time Series (Daily)" not in data:
    print("API error:", data)
    exit()

ts = data["Time Series (Daily)"]

df = pd.DataFrame(ts).T
df.index = pd.to_datetime(df.index)
df = df.sort_index()

df.columns = ["open", "high", "low", "close", "volume"]
df = df.astype(float)

print(df.head())
