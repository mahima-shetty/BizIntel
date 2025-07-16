import sqlite3
from datetime import datetime
import os

DB_PATH = "streamlit_ui/db/prefs.db"

def save_kpi_snapshot(email, ticker, kpi_dict, date=None):
    date = date or datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for k, v in kpi_dict.items():
        cursor.execute("""
            INSERT INTO kpi_history (email, ticker, date, kpi_key, kpi_value)
            VALUES (?, ?, ?, ?, ?)
        """, (email, ticker, date, k, str(v)))

    conn.commit()
    conn.close()




def save_news_article(email, article):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO news_history (email, title, content, source, url, date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        email,
        article.get("title", ""),
        article.get("content", "") or article.get("description", ""),
        article.get("source", ""),
        article.get("url", ""),
        datetime.now().strftime("%Y-%m-%d")
    ))

    conn.commit()
    conn.close()


def load_kpi_history(email, tickers=None, days=30):
    from datetime import datetime, timedelta
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if tickers is None:
        cursor.execute("""
            SELECT ticker, date, kpi_key, kpi_value
            FROM kpi_history
            WHERE email = ? AND date >= ?
            ORDER BY date DESC
        """, (email, cutoff_date))
    elif isinstance(tickers, str):
        cursor.execute("""
            SELECT ticker, date, kpi_key, kpi_value
            FROM kpi_history
            WHERE email = ? AND ticker = ? AND date >= ?
            ORDER BY date DESC
        """, (email, tickers, cutoff_date))
    elif isinstance(tickers, list):
        placeholders = ",".join("?" for _ in tickers)
        query = f"""
            SELECT ticker, date, kpi_key, kpi_value
            FROM kpi_history
            WHERE email = ? AND ticker IN ({placeholders}) AND date >= ?
            ORDER BY date DESC
        """
        cursor.execute(query, [email, *tickers, cutoff_date])
    else:
        raise ValueError("tickers must be None, str, or list")

    rows = cursor.fetchall()
    conn.close()

    history = {}
    for ticker, date, key, value in rows:
        history.setdefault(ticker, {}).setdefault(date, {})[key] = value
    return history



def load_news_history(email, days=30):
    from datetime import datetime, timedelta
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, content, source, url, date
        FROM news_history
        WHERE email = ? AND date >= ?
        ORDER BY date DESC
    """, (email, cutoff_date))
    rows = cursor.fetchall()
    conn.close()

    return [{
        "title": title,
        "content": content,
        "source": source,
        "url": url,
        "date": date
    } for title, content, source, url, date in rows]
