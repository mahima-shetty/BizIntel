# streamlit_ui/utils/researcher_prefs.py

import sqlite3
import os

DB_PATH = os.path.join("streamlit_ui", "db", "prefs.db")

# ─────────────────────────────────────────────
# 📥 Load Researcher Preferences
def load_researcher_prefs(email: str) -> dict:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT ticker, depth FROM researcher_preferences WHERE email = ?;
        """, (email,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return {}

        return {
            "ticker": row[0],
            "depth": row[1]
        }
    except Exception as e:
        print(f"[ERROR] Failed to load researcher prefs: {e}")
        return {}

# ─────────────────────────────────────────────
# 💾 Save Researcher Preferences
def save_researcher_prefs(email: str, prefs_dict: dict) -> None:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS researcher_preferences (
                email TEXT PRIMARY KEY,
                ticker TEXT,
                depth TEXT,
                FOREIGN KEY(email) REFERENCES users(email)
            );
        """)

        cursor.execute("""
            INSERT INTO researcher_preferences (email, ticker, depth)
            VALUES (?, ?, ?)
            ON CONFLICT(email) DO UPDATE SET
                ticker = excluded.ticker,
                depth = excluded.depth;
        """, (
            email,
            prefs_dict.get("ticker", "AAPL"),
            prefs_dict.get("depth", "standard")
        ))

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[ERROR] Failed to save researcher prefs: {e}")
