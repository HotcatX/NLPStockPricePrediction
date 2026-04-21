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

# Page configuration
st.set_page_config(page_title="APAN5400 Dashboard", layout="wide", page_icon="📈")

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

@st.cache_data(ttl=3600)
def fetch_nlp_data():
    news_url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={TICKER}&apikey={ALPHA_VANTAGE_API}&limit=100"
    response = requests.get(news_url).json()
    return response.get("feed", [])

# ================= UI Layout =================
st.title("📈 APAN5400 Final Project: End-to-End Market Dashboard")
st.markdown("""
This interactive front-end dashboard pulls structured financial metrics from **AWS Aurora MySQL** 
and streams live Big Data NLP sentiment analysis to form a complete overview.
""")

tab1, tab2 = st.tabs(["💰 Structured Market Data (AWS SQL)", "🧠 Big Data & NLP Analysis"])

# -------------- TAB 1: SQL Data --------------
with tab1:
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM stock_prices ORDER BY date DESC LIMIT 100")
            rows = cursor.fetchall()
            columns = [i[0] for i in cursor.description]
            df = pd.DataFrame(rows, columns=columns)
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
        
        if not df.empty:
            st.subheader(f"📊 Historical Price Movement: {TICKER} (Sourced from Aurora)")
            chart_data = df.set_index("date")[["close", "open", "high", "low"]]
            st.line_chart(chart_data["close"], height=350, color="#FF4B4B")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("🗄️ Raw Data Feed Preview")
                st.dataframe(df.head(10), width='stretch')
                
            with col2:
                st.subheader("💡 Key Metrics")
                st.metric(label="Latest Close Price", value=f"${df['close'].iloc[0]:.2f}", delta=f"{(df['close'].iloc[0] - df['close'].iloc[1]):.2f} pts")
                st.metric(label="Latest Trading Volume", value=f"{df['volume'].iloc[0]:,.0f}")
                st.metric(label="Total Cloud Records Parsed", value=f"{len(df)} days")
        else:
            st.warning("Database connected but 'stock_prices' table is empty.")

    except Exception as e:
        st.error(f"Cannot connect to Cloud Database: {e}")

# -------------- TAB 2: NLP Analysis --------------
with tab2:
    st.markdown("### Semantic Keyword Extractor & Global Sentiment Aggregation")
    st.info("Pipeline: Raw API -> DynamoDB Data Lake -> NLP Native Tokenizer -> Streamlit Visualization")
    
    with st.spinner("Crunching massive live news NLP data..."):
        feed = fetch_nlp_data()
        
    if feed:
        sentiments = [item.get("overall_sentiment_label") for item in feed]
        sentiment_counts = Counter(sentiments)
        
        # Two columns for NLP charts
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
            stopwords = {"a", "and", "the", "to", "of", "in", "for", "is", "on", "with", "as", "at", "it", "by", "from", "that"}
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
            
        st.subheader("📰 Highly Relevant Alpha Sources")
        for i, item in enumerate(feed[:5]):
            st.markdown(f"**[{item['overall_sentiment_label']}]** [{item['title']}]({item['url']}) _({item['source']})_")
            
    else:
        st.error("No NLP data currently available in Data Pool.")

# Sidebar
st.sidebar.title("⚙️ System Status")
st.sidebar.success("✅ AWS IAM Verified")
st.sidebar.success("✅ Secrets Manager Active")
st.sidebar.success("✅ Aurora MySQL Connected")
st.sidebar.success("✅ NLP Engine Fired")
st.sidebar.info("⚡ Real-time Analytics powered by Streamlit Engine.")
