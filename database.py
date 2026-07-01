import sqlite3
from datetime import datetime

DB_FILE = "audit.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih TEXT,
            host TEXT,
            islem TEXT,
            detay TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_ekle(host, islem, detay=""):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO audit_log (tarih, host, islem, detay) VALUES (?, ?, ?, ?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), host, islem, detay)
    )
    conn.commit()
    conn.close()
    

def log_listele():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM audit_log ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def log_temizle():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM audit_log")
    conn.commit()
    conn.close()