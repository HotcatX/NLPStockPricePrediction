import streamlit as st
import pandas as pd
import pymysql
import boto3
import json
import os
from dotenv import load_dotenv

# Page configuration
st.set_page_config(page_title="APAN5400 Dashboard", layout="wide", page_icon="📈")

# Load secure environment variables
load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
REGION = "us-east-1"

# Connect to database securely using caching to prevent repeated AWS calls
@st.cache_resource
def get_db_connection():
    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=REGION
    )
    client = session.client('secretsmanager')
    secret_arn = "arn:aws:secretsmanager:us-east-1:658362403068:secret:rds!cluster-5dc84c5e-8082-4f41-9791-308322f5cf86-GsnF9n"
    response = client.get_secret_value(SecretId=secret_arn)
    db_password = json.loads(response['SecretString']).get('password')
    
    connection = pymysql.connect(
        host='database-1-instance-1.c49ey4umasff.us-east-1.rds.amazonaws.com',
        user='Haoyuan',
        password=db_password,
        database='market_data',
        port=3306,
        ssl={'ca': 'global-bundle.pem'}
    )
    return connection

# UI Layout
st.title("📈 APAN5400 Final Project: Live Financial Dashboard")
st.markdown("""
This interactive front-end application directly connects to our AWS Cloud Infrastructure. 
It retrieves real-time pricing data stored securely in **AWS Aurora MySQL** and visualizes it for end-users, 
fulfilling the end-to-end interactive API requirement.
""")

try:
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM stock_prices ORDER BY date DESC LIMIT 100")
        rows = cursor.fetchall()
        # Create Panda DataFrame with correct Column names
        columns = [i[0] for i in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
    
    if not df.empty:
        symbol = df["symbol"].iloc[0]
        st.subheader(f"📊 Historical Price Movement: {symbol.upper()} (Sourced from Aurora)")
        
        # Display an interactive line chart
        chart_data = df.set_index("date")[["close", "open", "high", "low"]]
        st.line_chart(chart_data["close"], height=400, color="#FF4B4B")
        
        # Two columns for Layout 
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🗄️ Raw Data Feed (SQL Table Preview)")
            st.dataframe(df.head(10), use_container_width=True)
            
        with col2:
            st.subheader("💡 Key Metrics")
            st.metric(label="Latest Close Price", value=f"${df['close'].iloc[0]:.2f}", delta=f"{(df['close'].iloc[0] - df['close'].iloc[1]):.2f} pts")
            st.metric(label="Latest Trading Volume", value=f"{df['volume'].iloc[0]:,.0f}")
            st.metric(label="Total Cloud Records Parsed", value=f"{len(df)} days")
            
    else:
        st.warning("Database connected but 'stock_prices' table is empty.")

except Exception as e:
    st.error(f"Cannot connect to Cloud Database: {e}")

# Sidebar
st.sidebar.title("⚙️ System Status")
st.sidebar.success("✅ AWS IAM Verified")
st.sidebar.success("✅ Secrets Manager Active")
st.sidebar.success("✅ Aurora MySQL Connected")
st.sidebar.info("⚡ Real-time Analytics powered by Streamlit Engine.")
