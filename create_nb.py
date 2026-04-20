import nbformat as nbf

nb = nbf.v4.new_notebook()

cells = []

# Title
cells.append(nbf.v4.new_markdown_cell("""# APAN5400 Final Project: Market Sentiment and Price Correlation Analysis System

## 1. Project Overview
This project integrates stock market data with news information, utilizing NLP techniques to analyze market sentiment and explore the correlation between sentiment and price movements.

## 2. Technical Architecture Integration
This notebook demonstrates the **Local Compute + Cloud Storage** architecture:
*   **Data Collection**: Alpha Vantage API (Runs locally)
*   **NoSQL Data Lake**: AWS DynamoDB (Active - Storing raw JSON)
*   **SQL Relational DB**: AWS Aurora MySQL (Pending Firewall Access - Storing metrics)
*   **Security Management**: AWS Secrets Manager"""))

# Imports
cells.append(nbf.v4.new_code_cell("""import requests
import pandas as pd
import boto3
import pymysql
import json
import time
import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()"""))

# Credentials
cells.append(nbf.v4.new_markdown_cell("""## 3. Cloud Access Config (AWS Credentials)"""))
cells.append(nbf.v4.new_code_cell("""# It is recommended to use python-dotenv to protect these keys
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', 'YOUR_IAM_KEY')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', 'YOUR_IAM_SECRET')
REGION = "us-east-1"

# Initialize AWS Boto3 Session
session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=REGION
)
print("✅ AWS Boto3 Session Initialized.")"""))

# Data ingestion
cells.append(nbf.v4.new_markdown_cell("""## 4. Alpha Vantage Data Ingestion
Fetch latest market data to push to the cloud data lake."""))
cells.append(nbf.v4.new_code_cell("""ALPHA_VANTAGE_API = os.getenv('ALPHA_API_KEY', '9SMJWT4DNUDBHM80')
TICKER = "AAPL"
url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={TICKER}&apikey={ALPHA_VANTAGE_API}"

response = requests.get(url)
market_data = response.json()

print(f"Successfully fetched daily timeseries for {TICKER}.")"""))

# DynamoDB
cells.append(nbf.v4.new_markdown_cell("""## 5. Storage Pipeline 1: Push Raw JSON to DynamoDB (NoSQL)
**Status: ACTIVE**  
We store the exact JSON payload returned by the API into DynamoDB (Table: `APAN5200`) as unstructured NoSQL records. This provides us a raw Data Lake."""))
cells.append(nbf.v4.new_code_cell("""try:
    dynamodb = session.resource('dynamodb')
    table = dynamodb.Table('APAN5200')
    
    # Generate a unique record ID 
    record_id = f"{TICKER}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Put item into DynamoDB. 
    table.put_item(
        Item={
            'APAN5200CHY': record_id, 
            'Symbol': TICKER,
            'RawData': json.dumps(market_data)
        }
    )
    print(f"✅ SUCCESS: Inserted raw JSON for {TICKER} into AWS DynamoDB!")
    print(f">>> Record ID: {record_id}")
except Exception as e:
    print("❌ DynamoDB Insertion Failed:", e)"""))

# Aurora
cells.append(nbf.v4.new_markdown_cell("""## 6. Storage Pipeline 2: Extract Metrics & Push to Aurora MySQL (SQL)
**Status: READY PENDING CLOUD FIREWALL ACCESS**  
This section pulls the DB password securely from `AWS Secrets Manager`, formats the raw NoSQL JSON into an analytical structured Pandas dataframe, and inserts it into `AWS Aurora MySQL`."""))

cells.append(nbf.v4.new_code_cell("""# 6.1 Clean the NoSQL data into a structured Pandas Dataframe for SQL Insertion
ts = market_data.get("Time Series (Daily)", {})
df = pd.DataFrame(ts).T
df.index = pd.to_datetime(df.index)
df.columns = ["open", "high", "low", "close", "volume"]
df = df.astype(float)
df['symbol'] = TICKER

print("Cleaned SQL-ready Dataframe Sample:")
df.tail(3)"""))

cells.append(nbf.v4.new_code_cell("""# 6.2 Retrieve Password securely from AWS Secrets Manager 
try:
    client = session.client('secretsmanager')
    secret_arn = "arn:aws:secretsmanager:us-east-1:658362403068:secret:rds!cluster-5dc84c5e-8082-4f41-9791-308322f5cf86-GsnF9n"
    response = client.get_secret_value(SecretId=secret_arn)
    aurora_password = json.loads(response['SecretString']).get('password')
    print("✅ SUCCESS: Password securely retrieved from AWS Secrets Manager.")
except Exception as e:
    print("❌ Failed to retrieve password:", e)
    aurora_password = None"""))

cells.append(nbf.v4.new_code_cell("""# 6.3 Placeholder: Insert dataframe into Aurora MySQL via PyMySQL / SQLAlchemy
print(\"\\n--- Aurora MySQL Connection Setup ---\")
print(\"Status: Awaiting AWS Security Group modification to allow outbound local IP on port 3306.\")
print(\"Once firewall is opened, the following block handles the bulk push:\\n\")

'''
if aurora_password:
    import sqlalchemy
    
    # Connect using SQLAlchemy Engine config (with SSL mapping)
    endpoint = \"database-1-instance-1.c49ey4umasff.us-east-1.rds.amazonaws.com\"
    connection_str = f\"mysql+pymysql://Haoyuan:{aurora_password}@{endpoint}:3306/market_data\"
    
    engine = sqlalchemy.create_engine(
        connection_str, 
        connect_args={'ssl': {'ca': 'global-bundle.pem'}}
    )
    
    # Execute bulk load from Pandas directly to AWS Aurora SQL 'stock_prices' table
    df.to_sql(name='stock_prices', con=engine, if_exists='append', index=True, index_label='date')
    print(\"Data successfully pushed to AWS Aurora MySQL.\")
'''"""))

nb['cells'] = cells
with open('Project_Analysis.ipynb', 'w') as f:
    nbf.write(nb, f)
print("Notebook successfully generated using nbformat.")
