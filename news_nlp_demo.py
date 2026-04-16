import csv
import datetime as dt
import os
import re
import time
from collections import Counter
from pathlib import Path

import requests


API_URL = "https://www.alphavantage.co/query"
DEFAULT_TICKERS = ["QQQ", "AAPL", "MSFT", "NVDA", "AMZN", "META"]
POSITIVE_WORDS = {
    "beat",
    "beats",
    "bullish",
    "gain",
    "gains",
    "growth",
    "higher",
    "improve",
    "improved",
    "improves",
    "outperform",
    "positive",
    "profit",
    "profits",
    "rebound",
    "rise",
    "rises",
    "strong",
    "surge",
    "surges",
    "upside",
}
NEGATIVE_WORDS = {
    "bearish",
    "cut",
    "cuts",
    "decline",
    "declines",
    "downside",
    "drop",
    "drops",
    "fall",
    "falls",
    "lower",
    "miss",
    "misses",
    "negative",
    "risk",
    "risks",
    "selloff",
    "slowdown",
    "weak",
    "warning",
}
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "its",
    "of",
    "on",
    "that",
    "the",
    "this",
    "to",
    "with",
    "will",
    "after",
    "by",
    "over",
    "new",
    "stock",
    "stocks",
    "nasdaq",
    "today",
    "etf",
}


def load_api_key() -> str:
    return os.getenv("ALPHAVANTAGE_API_KEY", "AHVAXANX4RZ305AS")


def fetch_news_for_ticker(api_key: str, ticker: str, limit: int = 10) -> list[dict]:
    params = {
        "function": "NEWS_SENTIMENT",
        "tickers": ticker,
        "limit": limit,
        "apikey": api_key,
    }
    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()
    if "feed" not in payload:
        raise RuntimeError(f"Alpha Vantage error for {ticker}: {payload}")
    return payload["feed"]


def is_today(timestamp: str, today_utc: dt.date) -> bool:
    published = dt.datetime.strptime(timestamp, "%Y%m%dT%H%M%S").date()
    return published == today_utc


def tokenize(text: str) -> list[str]:
    cleaned = re.sub(r"[^A-Za-z0-9\s]", " ", text.lower())
    return [
        token
        for token in cleaned.split()
        if len(token) > 2 and token not in STOPWORDS and not token.isdigit()
    ]


def local_sentiment_score(text: str) -> int:
    tokens = tokenize(text)
    positives = sum(token in POSITIVE_WORDS for token in tokens)
    negatives = sum(token in NEGATIVE_WORDS for token in tokens)
    return positives - negatives


def normalize_api_label(label: str) -> str:
    return label.replace("_", "-")


def main() -> None:
    api_key = load_api_key()
    output_dir = Path("/Users/cat/Documents/作业/5400/output")
    output_dir.mkdir(exist_ok=True)
    today_utc = dt.datetime.now(dt.UTC).date()

    rows: list[dict] = []
    for index, ticker in enumerate(DEFAULT_TICKERS):
        if index > 0:
            time.sleep(1.2)
        news_items = fetch_news_for_ticker(api_key, ticker)
        today_items = [item for item in news_items if is_today(item["time_published"], today_utc)]
        for item in today_items:
            combined_text = f'{item.get("title", "")} {item.get("summary", "")}'
            rows.append(
                {
                    "ticker_query": ticker,
                    "title": item.get("title", ""),
                    "source": item.get("source", ""),
                    "time_published": item.get("time_published", ""),
                    "overall_sentiment_label": normalize_api_label(item.get("overall_sentiment_label", "")),
                    "overall_sentiment_score": float(item.get("overall_sentiment_score", 0.0)),
                    "local_keyword_sentiment": local_sentiment_score(combined_text),
                    "summary": item.get("summary", ""),
                    "url": item.get("url", ""),
                }
            )

    deduped: list[dict] = []
    seen_urls = set()
    for row in sorted(rows, key=lambda item: (item["time_published"], item["ticker_query"]), reverse=True):
        if row["url"] in seen_urls:
            continue
        seen_urls.add(row["url"])
        deduped.append(row)

    if not deduped:
        print("No same-day news returned for the configured tickers.")
        return

    output_csv = output_dir / "today_stock_news_demo.csv"
    with output_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(deduped[0].keys()))
        writer.writeheader()
        writer.writerows(deduped)

    api_label_counts = Counter(row["overall_sentiment_label"] for row in deduped)
    token_counter = Counter()
    for row in deduped:
        token_counter.update(tokenize(f'{row["title"]} {row["summary"]}'))

    avg_api_sentiment = sum(row["overall_sentiment_score"] for row in deduped) / len(deduped)
    avg_local_sentiment = sum(row["local_keyword_sentiment"] for row in deduped) / len(deduped)

    print(f"Today UTC date: {today_utc.isoformat()}")
    print(f"Collected unique articles: {len(deduped)}")
    print(f"Average API sentiment score: {avg_api_sentiment:.3f}")
    print(f"Average local keyword sentiment: {avg_local_sentiment:.3f}")
    print("API sentiment distribution:")
    for label, count in sorted(api_label_counts.items()):
        print(f"  - {label}: {count}")
    print("Top keywords:")
    for word, count in token_counter.most_common(12):
        print(f"  - {word}: {count}")
    print("Sample articles:")
    for row in deduped[:5]:
        print(
            f"  - [{row['ticker_query']}] {row['title']} | "
            f"{row['overall_sentiment_label']} ({row['overall_sentiment_score']:.3f}) | "
            f"local={row['local_keyword_sentiment']}"
        )
    print(f"Saved CSV: {output_csv}")


if __name__ == "__main__":
    main()
