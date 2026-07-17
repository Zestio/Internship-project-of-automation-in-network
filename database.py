# ============================================================
# VERİTABANI YÖNETİM MODÜLÜ
# SQLite tabanlı — kullanıcı, cihaz, audit log ve geçmiş
# ============================================================

import sqlite3
from datetime import datetime

# Veritabanı dosya adı
DB_FILE = "audit.db"


def _get_conn():
    """Veritabanı bağlantısı döner. Her fonksiyon kendi bağlantısını açıp kapatır."""
    return sqlite3.connect(DB_FILE)


# ============================================================
# TABLO OLUŞTURMA
# ============================================================

def init_db():
    """
    Uygulama başlangıcında çağrılır.
    Mevcut tablolar silinmez — sadece yoksa oluşturulur (IF NOT EXISTS).
    """
    conn = _get_conn()
    c = conn.cursor()

    # Kullanıcılar tablosu — rol: 'admin' veya 'readonly'
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role     TEXT DEFAULT 'admin'
        )
    ''')

    # Kullanıcı cihazları tablosu — her kullanıcı birden fazla cihaz ekleyebilir
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_devices (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            host         TEXT NOT NULL,
            port         INTEGER NOT NULL,
            display_host TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Audit log tablosu — backup, config diff, config apply işlemleri
    c.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih   TEXT,
            host    TEXT,
            islem   TEXT,
            detay   TEXT,
            user_id INTEGER
        )
    ''')

    # Cihaz durum geçmişi — interface down olayları
    c.execute('''
        CREATE TABLE IF NOT EXISTS device_history (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih     TEXT,
            user_id   INTEGER,
            host      TEXT,
            hostname  TEXT,
            interface TEXT,
            status    TEXT
        )
    ''')

    conn.commit()
    conn.close()


def init_device_history():
    """Geriye dönük uyumluluk için bırakıldı. Tablo artık init_db() içinde oluşturulur."""
    pass


# ============================================================
# AUDİT LOG İŞLEMLERİ
# ============================================================

def log_ekle(host, islem, detay="", user_id=None):
    """
    Audit log tablosuna yeni kayıt ekler.
    islem: 'BACKUP', 'CONFIG DIFF', 'CONFIG APPLY' gibi işlem tipleri
    """
    conn = _get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO audit_log (tarih, host, islem, detay, user_id) VALUES (?, ?, ?, ?, ?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), host, islem, detay, user_id)
    )
    conn.commit()
    conn.close()


def log_listele(user_id=None):
    """
    Audit log kayıtlarını döner. 
    user_id verilirse sadece o kullanıcının kayıtları, verilmezse tümü.
    """
    conn = _get_conn()
    c = conn.cursor()
    if user_id:
        c.execute(
            "SELECT * FROM audit_log WHERE user_id = ? ORDER BY id DESC",
            (user_id,)
        )
    else:
        c.execute("SELECT * FROM audit_log ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows


def log_temizle():
    """Audit log tablosundaki tüm kayıtları siler. Geri alınamaz."""
    conn = _get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM audit_log")
    conn.commit()
    conn.close()


# ============================================================
# KULLANICI İŞLEMLERİ
# ============================================================

def kullanici_ekle(username, password, role='admin'):
    """
    Yeni kullanıcı ekler.
    Kullanıcı adı benzersiz olmalı — çakışma varsa None döner.
    Şifre SHA-256 hash'lenmiş olarak gönderilmelidir.
    """
    conn = _get_conn()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, password, role)
        )
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        # Kullanıcı adı zaten mevcut
        conn.close()
        return None


def kullanici_bul(username):
    """Kullanıcı adına göre kullanıcı kaydını döner. Bulunamazsa None."""
    conn = _get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    return user


def kullanici_guncelle_rol(user_id, role):
    """Kullanıcının rolünü günceller. role: 'admin' veya 'readonly'"""
    conn = _get_conn()
    c = conn.cursor()
    c.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
    conn.commit()
    conn.close()


def tum_kullanicilar():
    """Tüm kullanıcıları (id, username, role) olarak döner. Admin paneli için."""
    conn = _get_conn()
    c = conn.cursor()
    c.execute("SELECT id, username, role FROM users")
    rows = c.fetchall()
    conn.close()
    return rows


# ============================================================
# CİHAZ İŞLEMLERİ
# ============================================================

def kullanici_cihaz_ekle(user_id, host, port, display_host):
    """
    Kullanıcıya yeni cihaz ekler.
    host: GNS3 VM IP adresi
    port: Telnet port numarası
    display_host: Arayüzde gösterilecek IP
    """
    conn = _get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO user_devices (user_id, host, port, display_host) VALUES (?, ?, ?, ?)",
        (user_id, host, port, display_host)
    )
    conn.commit()
    conn.close()


def kullanici_cihazlari(user_id):
    """Kullanıcıya ait tüm cihazları döner."""
    conn = _get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM user_devices WHERE user_id = ?", (user_id,))
    devices = c.fetchall()
    conn.close()
    return devices


# ============================================================
# CİHAZ DURUM GEÇMİŞİ
# ============================================================

def history_ekle(user_id, host, hostname, interface, status):
    """
    Interface durum değişikliğini geçmişe kaydeder.
    Monitor döngüsü tarafından interface down olduğunda çağrılır.
    """
    conn = _get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO device_history (tarih, user_id, host, hostname, interface, status) VALUES (?, ?, ?, ?, ?, ?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id, host, hostname, interface, status)
    )
    conn.commit()
    conn.close()


def history_listele(user_id, host=None):
    """
    Cihaz durum geçmişini döner. En fazla 100 kayıt.
    host verilirse sadece o cihazın geçmişi, verilmezse tüm cihazlar.
    """
    conn = _get_conn()
    c = conn.cursor()
    if host:
        c.execute(
            "SELECT * FROM device_history WHERE user_id = ? AND host = ? ORDER BY id DESC LIMIT 100",
            (user_id, host)
        )
    else:
        c.execute(
            "SELECT * FROM device_history WHERE user_id = ? ORDER BY id DESC LIMIT 100",
            (user_id,)
        )
    rows = c.fetchall()
    conn.close()
    return rows