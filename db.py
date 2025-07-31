import sqlite3

def get_connection():
    conn = sqlite3.connect("expenses.db")
    #conn.set_trace_callback(print)  # Log all SQL statements
    return conn

def connect_db():
    return get_connection()

def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            note TEXT
        )
    """)
    conn.commit()
    conn.close()
