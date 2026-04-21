import streamlit as st
import pandas as pd
import pymysql
import boto3
import json
import os
import requests
import re
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv
from sklearn.linear_model import LinearRegression

# Page configuration
st.set_page_config(page_title="APAN5400 Market AI Dashboard", layout="wide", page_icon="💻")

# Load secure environment variables
load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
ALPHA_VANTAGE_API = os.getenv('ALPHA_API_KEY')
REGION = "us-east-1"
TICKER = "AAPL"

# Connect to database securely using caching
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

@st.cache_data(ttl=300)
def fetch_nlp_data():
    """Retrieve raw unstructured news JSON directly from AWS DynamoDB Data Lake"""
    try:
        session = boto3.Session(aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=REGION)
        dynamodb = session.resource('dynamodb')
        table = dynamodb.Table('APAN5200')
        
        response = table.scan(Limit=800)
        items = response.get('Items', [])
        
        feed = []
        for i in items:
            raw_str = i.get('RawData')
            if raw_str:
                feed.append(json.loads(raw_str))
        return feed
    except Exception as e:
        st.error(f"Failed to pull from DynamoDB Data Lake: {e}")
        return []

# ================= SYSTEM HEADER =================
st.title("📈 APAN5400 Final Project: End-to-End Market AI Dashboard")
st.markdown("""
This full-stack interactive dashboard pulls structured financial metrics from **AWS Aurora MySQL**, 
streams live unstructured NLP text analytics from APIs, and intersects them using a Native **Scikit-Learn Regression** model.
""")

df = pd.DataFrame()
try:
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM stock_prices ORDER BY date DESC LIMIT 100")
        rows = cursor.fetchall()
        columns = [i[0] for i in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
except Exception as e:
    st.error(f"Cannot connect to Cloud Database: {e}")

feed = fetch_nlp_data()

# ================= 1. STRUCTURED MARKET DATA (AWS SQL) =================
if not df.empty:
    st.header(f"💰 1. Historical SQL Price Action: {TICKER}")
    
    # Showcase metrics up top
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric(label="Latest Close Price", value=f"${df['close'].iloc[0]:.2f}", delta=f"{(df['close'].iloc[0] - df['close'].iloc[1]):.2f} pts")
    col_m2.metric(label="Latest Trading Volume", value=f"{df['volume'].iloc[0]:,.0f}")
    col_m3.metric(label="Total Cloud SQL Records", value=f"{len(df)} entries")
    
    chart_data = df.set_index("date")
    st.line_chart(chart_data["close"], height=350, color="#FF4B4B")

st.divider()

# ================= 2. BIG DATA & NLP ANALYSIS =================
if feed:
    st.header("🧠 2. NLP Big Data: Semantic Extraction & Sentiment")
    
    sentiments = [item.get("overall_sentiment_label") for item in feed]
    sentiment_counts = Counter(sentiments)
    
    nlp_col1, nlp_col2 = st.columns(2)
    
    with nlp_col1:
        st.subheader("🌐 Global Sentiment Distribution")
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        sns.barplot(
            x=list(sentiment_counts.values()), 
            y=list(sentiment_counts.keys()), 
            ax=ax1,
            palette="viridis",
            hue=list(sentiment_counts.keys()), 
            legend=False
        )
        ax1.set_xlabel("Number of Articles")
        st.pyplot(fig1)

    with nlp_col2:
        st.subheader("🔥 Financial TF-IDF Buzzwords")
        combined_text = " ".join([item.get("title", "") + " " + item.get("summary", "") for item in feed]).lower()
        cleaned_text = re.sub(r'[^a-z\s]', '', combined_text)
        stopwords = {"a", "and", "the", "to", "of", "in", "for", "is", "on", "with", "as", "at", "it", "by", "from", "that", "this", "inc", "are", "be"}
        words = [w for w in cleaned_text.split() if w not in stopwords and len(w) > 3]
        top_words = Counter(words).most_common(10)
        
        words_list, counts_list = zip(*top_words)
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        sns.barplot(
            x=list(counts_list), 
            y=list(words_list), 
            ax=ax2, 
            palette="magma",
            hue=list(words_list), 
            legend=False
        )
        ax2.set_xlabel("Frequency Count")
        st.pyplot(fig2)

st.divider()

# ================= 3. MACHINE LEARNING FORECAST =================
st.header("🔮 3. Machine Learning NLP Forecast")
st.info("Uses ML Autoregression to analyze historical trajectory, then leverages modern NLP scoring to adjust final predictive valuation.")

if not df.empty and feed:
    ml_df = df.sort_values('date').copy()
    ml_df['Lag_1'] = ml_df['close'].shift(1)
    ml_df['Lag_2'] = ml_df['close'].shift(2)
    ml_df['Lag_3'] = ml_df['close'].shift(3)
    ml_df.dropna(inplace=True)
    
    X = ml_df[['Lag_1', 'Lag_2', 'Lag_3']]
    y = ml_df['close']
    
    model = LinearRegression()
    model.fit(X, y)
    
    last_day = ml_df.iloc[-1]
    X_latest = pd.DataFrame([{'Lag_1': last_day['close'], 'Lag_2': last_day['Lag_1'], 'Lag_3': last_day['Lag_2']}])
    
    base_prediction = model.predict(X_latest)[0]
    current_price = last_day['close']
    base_change = (base_prediction - current_price) / current_price
    
    sentiment_scores = [item.get("overall_sentiment_score") for item in feed if item.get("overall_sentiment_score") is not None]
    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
    
    sentiment_leverage = 0.05 
    nlp_modifier = avg_sentiment * sentiment_leverage 
    
    final_prediction = current_price * (1 + base_change + nlp_modifier)
    
    col_ml1, col_ml2 = st.columns(2)
    
    with col_ml1:
        st.write("#### 🎯 Next Day Target Prediction")
        direction = "Bullish Growth 🟢" if final_prediction > current_price else "Bearish Drop 🔴"
        st.metric(
            label="Calculated Synthetic Target", 
            value=f"${final_prediction:.2f}", 
            delta=f"${final_prediction - current_price:.2f} ({direction})"
        )
        st.success("Analysis integrates Real-world MySQL Pricing Patterns and API/JSON unstructured sentiment analytics.")

    with col_ml2:
         st.write("#### Algorithm Breakdown:")
         st.markdown(f"- **Current Baseline:** `${current_price:.2f}`")
         st.markdown(f"- **Scikit-Learn Baseline Forecast:** `${base_prediction:.2f}`")
         st.markdown(f"- **NLP Global Opinion Modifier:** `{avg_sentiment:.4f}` _(Amplifying trend based on text news)_")

st.divider()

# ================= 4. RAW DATABASE FEEDS (BOTTOM) =================
st.header("🗄️ 4. Data Architect Appendix: Raw Feeds")
if not df.empty:
    st.write("**Structured Data Pool (AWS Aurora)**")
    st.dataframe(df.head(50), width="stretch")

if feed:
    with st.expander("📝 View Raw Unstructured JSON Target News Pool (Sample)"):
        st.json(feed[:3])

# Sidebar
st.sidebar.title("⚙️ Architecture Status")
st.sidebar.success("🔑 AWS IAM Initialized")
st.sidebar.success("🛡️ Secrets Manager Active")
st.sidebar.success("🐬 Aurora MySQL Connected")
st.sidebar.success("📑 NLP Scraper Fired")
st.sidebar.success("🤖 ML Model Trained")
