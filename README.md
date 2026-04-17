# Project Proposal: Financial Market Sentiment and Price Correlation Analysis System

## 1. Core Architecture
**Historical Backtesting (Big Data Foundation) + End-to-End Real-time Analysis (Demo Showcase)**
*   **Scalability**: Leverage historical news and market datasets from Kaggle (1GB+) to simulate large-scale backtesting and validate strategy effectiveness.
*   **Real-time Analysis**: Utilize Alpha Vantage API to dynamically pull daily data, demonstrating the live data flow within the pipeline.

## 2. Tech Stack
*   **Data Ingestion**: Alpha Vantage API (News & Prices)
*   **SQL Database**: PostgreSQL (Stores structured indicators, correlated price and sentiment scores)
*   **NoSQL Database**: MongoDB (Acts as a data lake, storing raw, unstructured news JSON data)
*   **Big Data Processing**: PySpark (Used for processing millions of historical records, performing distributed word cloud analysis and sentiment computation)
*   **Frontend Showcase**: Flask / FastAPI (Lightweight dashboard)

## 3. Data Pipeline
1.  **Data Lake Ingestion (Stage 1)**: Raw JSON data pulled from Alpha Vantage is directly persisted into **MongoDB** to ensure data integrity and facilitate future field extensions.
2.  **ETL & Structuring (Stage 2)**: Cleaned stock indicators, tickers, dates, and formatted market data are written into **PostgreSQL**.
3.  **Distributed Analysis (Stage 3)**: **PySpark** reads unstructured text from MongoDB and market data from PostgreSQL:
    *   **NLP Processing**: Computes sentiment scores and extracts hot keywords from millions of historical news entries.
    *   **Aggregation**: Calculates the correlation between sentiment indicators and stock price volatility.
4.  **Showcase Layer (Stage 4)**: The Flask service extracts aggregated results from the database and visualizes them via a Dashboard:
    *   Sentiment Trends vs. Price Fluctuations
    *   Industry Keyword Clouds
    *   Stock Sentiment Comparison Rankings

## 4. Project Highlights
*   **Necessity of Big Data**: To handle the full-text analysis, word cloud extraction, and sentiment computation of millions of historical news entries, we introduced PySpark for distributed processing, overcoming the performance bottlenecks of single-machine processing.
*   **Hybrid Storage Architecture**: Combines the rigorous relational capabilities of SQL (for financial metrics) with the flexible schema of NoSQL (for news text), demonstrating targeted handling of different data formats.