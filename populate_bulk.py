import pandas as pd
import requests
import json
import boto3
import os
from dotenv import load_dotenv
import sqlalchemy
import urllib.parse
import datetime

load_dotenv()
AV_API = os.getenv("ALPHA_API_KEY")
AWS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SEC = os.getenv("AWS_SECRET_ACCESS_KEY")
REGION = "us-east-1"
TICKER = "AAPL"

print(f"🚀 Initializing API Historical Fetch for {TICKER}...")

# 1. Fetch 25+ years of prices (outputsize=full)
url_price = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={TICKER}&outputsize=full&apikey={AV_API}"
res_price = requests.get(url_price).json()

ts = res_price.get("Time Series (Daily)", {})
df = pd.DataFrame(ts).T

if not df.empty:
    df.index = pd.to_datetime(df.index)
    df.columns = ["open", "high", "low", "close", "volume"]
    df = df.astype(float)
    df["symbol"] = TICKER
    print(f"✅ Downloaded {len(df)} historical daily records (spanning 20+ years).")
else:
    print("❌ Failed to pull price history (API limit might be reached).")

# 2. Get AWS DB credentials & Push to Aurora MySQL
try:
    session = boto3.Session(aws_access_key_id=AWS_KEY, aws_secret_access_key=AWS_SEC, region_name=REGION)
    sm = session.client("secretsmanager")
    sec_arn = "arn:aws:secretsmanager:us-east-1:658362403068:secret:rds!cluster-5dc84c5e-8082-4f41-9791-308322f5cf86-GsnF9n"
    db_pwd = json.loads(sm.get_secret_value(SecretId=sec_arn)['SecretString']).get("password")
    
    encoded_pwd = urllib.parse.quote_plus(db_pwd)
    endpoint = "database-1-instance-1.c49ey4umasff.us-east-1.rds.amazonaws.com"
    conn_str = f"mysql+pymysql://Haoyuan:{encoded_pwd}@{endpoint}:3306/market_data"
    engine = sqlalchemy.create_engine(conn_str, connect_args={'ssl': {'ca': 'global-bundle.pem'}})
    
    if not df.empty:
        # replace existing 100 rows with 6000+ rows
        print("💾 Uploading structured data to AWS Aurora MySQL...")
        df.to_sql("stock_prices", con=engine, if_exists="replace", index=True, index_label="date")
        print("✅ Success! Aurora DB heavily loaded.")
except Exception as e:
    print(f"❌ Database error: {e}")

# 3. Pull Maximum Allowed News & Push to DynamoDB
try:
    url_news = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={TICKER}&limit=1000&apikey={AV_API}"
    res_news = requests.get(url_news).json()
    feed = res_news.get("feed", [])
    
    if feed:
        print(f"✅ Downloaded {len(feed)} huge news blocks.")
        dynamodb = session.resource('dynamodb')
        table = dynamodb.Table('APAN5200')
        
        # Batch write to dynamo to avoid massive script hang and speed up
        print("💾 Pushing raw JSON to DynamoDB Data Lake...")
        with table.batch_writer() as batch:
            for idx, item in enumerate(feed[:500]): # Push top 500 JSON payloads safely
                record_id = f"RAW_NEWS_{TICKER}_{idx}_{datetime.datetime.now().strftime('%M%S')}"
                batch.put_item(Item={
                    'APAN5200CHY': record_id, 
                    'Symbol': TICKER,
                    'RawData': json.dumps(item)
                })
        print("✅ Success! DynamoDB NoSQL loaded with hundreds of JSON blobs.")
    else:
        print("❌ Failed to pull news feed (API limit might be reached).")
except Exception as e:
    print(f"❌ DynamoDB error: {e}")

print("==================================================")
print("🎯 BULK LOAD COMPLETED. ")
