from datetime import datetime #save prediction time with srilankan time
import pytz #to handle timezone 
import sqlite3

DB_NAME = "users.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    cursor.execute("PRAGMA table_info(users)") #chekcing role column exist in the user table
    columns = [col[1] for col in cursor.fetchall()]

    if "role" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")

    cursor.execute("UPDATE users SET role='user' WHERE role IS NULL")

    # Prediction history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        input_text TEXT,
        ocr_text TEXT,
        prediction TEXT,
        confidence REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("SELECT * FROM users WHERE username='admin'") #checking first admin user in exist in the database if not then admin user will create
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users(username,password,role) VALUES(?,?,?)",
            ("admin","admin123","admin")
        )

    conn.commit()
    conn.close()

def add_user(username, password):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, password, "user")
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT role FROM users WHERE username=? AND password=?",
        (username, password)
    )

    row = cursor.fetchone()
    conn.close()

    if row:
        return row[0]   # now this is 'admin' or 'user'
    return None

def save_prediction(username, input_text, ocr_text, prediction, confidence):
    # 1. Define the Sri Lankan Timezone
    sl_timezone = pytz.timezone('Asia/Colombo')
    
    # 2. Get the current time in Sri Lanka
    # Format it as a string so SQLite stores it correctly
    sl_time = datetime.now(sl_timezone).strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO history (username, input_text, ocr_text, prediction, confidence,created_at) 
    VALUES (?, ?, ?, ?, ?,?) 
    """, (username, input_text, ocr_text, prediction, confidence,sl_time))
    conn.commit()
    conn.close()

init_db()