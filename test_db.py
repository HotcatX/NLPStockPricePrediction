import boto3
import pymysql
import json

import os
from dotenv import load_dotenv

load_dotenv()

# ================= Configuration =================
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', 'YOUR_IAM_KEY')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', 'YOUR_IAM_SECRET')
REGION = "us-east-1"

print("="*50)
print("Initializing AWS Session...")
session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=REGION
)

# ================= 1. Test DynamoDB =================
print("\n[TEST 1] Testing DynamoDB Connection...")
try:
    dynamodb = session.resource('dynamodb')
    table = dynamodb.Table('APAN5200')
    status = table.table_status
    print(f"✅ DynamoDB Connection SUCCESS! Table status: {status}")
except Exception as e:
    print(f"❌ DynamoDB Connection FAILED. Error: {e}")

# ================= 2. Test Secrets Manager (Get Password) =================
print("\n[TEST 2] Retrieving Aurora Password from Secrets Manager...")
db_password = None
try:
    client = session.client('secretsmanager')
    secret_arn = "arn:aws:secretsmanager:us-east-1:658362403068:secret:rds!cluster-5dc84c5e-8082-4f41-9791-308322f5cf86-GsnF9n"
    response = client.get_secret_value(SecretId=secret_arn)
    secret = json.loads(response['SecretString'])
    db_password = secret.get('password')
    print("✅ Successfully retrieved password from Secrets Manager.")
except Exception as e:
    print(f"❌ Failed to retrieve Secret. Error: {e}")

# ================= 3. Test Aurora MySQL =================
if db_password:
    print("\n[TEST 3] Testing Aurora MySQL Connection...")
    try:
        connection = pymysql.connect(
            host='database-1-instance-1.c49ey4umasff.us-east-1.rds.amazonaws.com',
            user='Haoyuan',
            password=db_password,
            database='market_data',
            port=3306,
            ssl={'ca': 'global-bundle.pem'}
        )
        print("✅ Aurora MySQL Connection SUCCESS!")
        
        with connection.cursor() as cursor:
            # Let's see if the stock_prices table exists
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            table_names = [t[0] for t in tables]
            print(f"📈 Tables found in 'market_data' database: {table_names}")
            
        connection.close()
    except Exception as e:
        print(f"❌ Aurora MySQL Connection FAILED. Error: {e}")

print("="*50)
