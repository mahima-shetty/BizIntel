# utils/analyst_prefs.py

import sqlite3
import os

DB_PATH = os.path.join("streamlit_ui", "db", "prefs.db")

# ─────────────────────────────────────────────
# 📥 Load Analyst Preferences (Structured Fields)
def load_analyst_prefs(email):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT sector, topic, region, count, sources, notification_frequency
            FROM analyst_preferences WHERE email = ?;
        """, (email,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return {}

        return {
            "sector": row[0],
            "topic": row[1],
            "region": row[2],
            "count": row[3],
            "sources": row[4].split(",") if row[4] else [],
            "notification_frequency": row[5]
        }
    except Exception as e:
        print(f"[ERROR] Failed to load analyst prefs: {e}")
        return {}

# ─────────────────────────────────────────────
# 💾 Save Analyst Preferences (Structured Fields)
def save_analyst_prefs(email, prefs_dict):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analyst_preferences (
                email TEXT PRIMARY KEY,
                sector TEXT,
                topic TEXT,
                region TEXT,
                count INTEGER,
                sources TEXT,
                notification_frequency TEXT,
                FOREIGN KEY(email) REFERENCES users(email)
            );
        """)

        cursor.execute("""
            INSERT INTO analyst_preferences (email, sector, topic, region, count, sources, notification_frequency)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(email) DO UPDATE SET
                sector = excluded.sector,
                topic = excluded.topic,
                region = excluded.region,
                count = excluded.count,
                sources = excluded.sources,
                notification_frequency = excluded.notification_frequency;
        """, (
            email,
            prefs_dict.get("sector", ""),
            prefs_dict.get("topic", ""),
            prefs_dict.get("region", ""),
            int(prefs_dict.get("count", 5)),
            ",".join(prefs_dict.get("sources", [])),
            prefs_dict.get("notification_frequency", "Weekly")
        ))

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[ERROR] Failed to save analyst prefs: {e}")
