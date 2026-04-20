import boto3
import pymysql
import json
import os
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
REGION = "us-east-1"

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=REGION
)

print("="*50)
print("📊 CHECKING DATABASE VOLUMES...")
print("="*50)

# ----- 1. Check DynamoDB -----
try:
    dynamodb = session.resource('dynamodb')
    table = dynamodb.Table('APAN5200')
    
    # scan for exact count (safe for small tables)
    response = table.scan(Select='COUNT')
    count = response['Count']
    print(f"📦 [NoSQL DynamoDB] 'APAN5200' Table Record Count: {count} JSON documents")
except Exception as e:
    print(f"❌ [DynamoDB] Failed to get count. Error: {e}")

# ----- 2. Check Aurora MySQL -----
try:
    client = session.client('secretsmanager')
    secret_arn = "arn:aws:secretsmanager:us-east-1:658362403068:secret:rds!cluster-5dc84c5e-8082-4f41-9791-308322f5cf86-GsnF9n"
    response = client.get_secret_value(SecretId=secret_arn)
    secret = json.loads(response['SecretString'])
    db_password = secret.get('password')
    
    connection = pymysql.connect(
        host='database-1-instance-1.c49ey4umasff.us-east-1.rds.amazonaws.com',
        user='Haoyuan',
        password=db_password,
        database='market_data',
        port=3306,
        ssl={'ca': 'global-bundle.pem'}
    )
    
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES;")
        tables = [t[0] for t in cursor.fetchall()]
        
        if not tables:
            print(f"🗃️ [SQL Aurora] 'market_data' Database is currently EMPTY (0 tables).")
        else:
            print(f"🗃️ [SQL Aurora] Found tables: {tables}")
            for table_name in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                row_count = cursor.fetchone()[0]
                print(f"   -> Table '{table_name}' has {row_count} rows of data.")
    connection.close()
    
except Exception as e:
    print(f"❌ [Aurora MySQL] Failed to get count. Error: {e}")

print("="*50)
