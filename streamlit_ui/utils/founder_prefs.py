from streamlit_ui.db.init_db import get_connection

def save_founder_prefs(email, prefs):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO founder_preferences
        (email, topic, count, funding_count, sources, notification_frequency)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        email,
        prefs.get("topic"),
        prefs.get("count"),
        prefs.get("funding_count"),
        ",".join(prefs.get("sources", [])),
        prefs.get("notification_frequency")
    ))

    conn.commit()
    conn.close()

def load_founder_prefs(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT topic, count, funding_count, sources, notification_frequency
        FROM founder_preferences WHERE email = ?
    """, (email,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "topic": row[0],
            "count": row[1],
            "funding_count": row[2],
            "sources": row[3].split(",") if row[3] else [],
            "notification_frequency": row[4],
        }
    return {}
