import sqlite3
import os

# ✅ Define the DB path
DB_PATH = "streamlit_ui/db/prefs.db"
print("🛠️ Using DB:", DB_PATH)

def get_connection():
    return sqlite3.connect(DB_PATH)

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # 🧑‍💼 Users table — core user info and role
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        user_type TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 🚀 Startup Founder preferences
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS founder_preferences (
        email TEXT PRIMARY KEY,
        topic TEXT,
        count INTEGER,
        funding_count INTEGER,
        sources TEXT,
        notification_frequency TEXT,
        FOREIGN KEY(email) REFERENCES users(email)
    );
    """)

    # 📊 Analyst preferences
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analyst_preferences (
    email TEXT PRIMARY KEY,
    sector TEXT,
    topic TEXT,
    region TEXT,
    count INTEGER,
    tickers TEXT,  
    sources TEXT,
    notification_frequency TEXT,
    FOREIGN KEY(email) REFERENCES users(email)
    );
    """)

    # 🔬 Researcher preferences
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS researcher_preferences (
        email TEXT PRIMARY KEY,
        topic TEXT,
        keywords TEXT,
        time_range TEXT,
        sources TEXT,
        FOREIGN KEY(email) REFERENCES users(email)
    );
    """)

    conn.commit()
    conn.close()
    print("✅ Database tables created successfully.")

# 🔧 Run this only when the file is executed directly
if __name__ == "__main__":
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    create_tables()
