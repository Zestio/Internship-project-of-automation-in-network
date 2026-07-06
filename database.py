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
        detay TEXT,
        user_id INTEGER
    )
''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            host TEXT NOT NULL,
            port INTEGER NOT NULL,
            display_host TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

def log_ekle(host, islem, detay="", user_id=None):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO audit_log (tarih, host, islem, detay, user_id) VALUES (?, ?, ?, ?, ?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), host, islem, detay, user_id)
    )
    conn.commit()
    conn.close()

def log_listele(user_id=None):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    if user_id:
        c.execute("SELECT * FROM audit_log WHERE user_id = ? ORDER BY id DESC", (user_id,))
    else:
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

def kullanici_ekle(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def kullanici_bul(username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    return user

def kullanici_cihaz_ekle(user_id, host, port, display_host):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO user_devices (user_id, host, port, display_host) VALUES (?, ?, ?, ?)",
        (user_id, host, port, display_host)
    )
    conn.commit()
    conn.close()

def kullanici_cihazlari(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM user_devices WHERE user_id = ?", (user_id,))
    devices = c.fetchall()
    conn.close()
    return devices