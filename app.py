import os
import threading
import time
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, send_file, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime
from database import init_db, log_ekle, log_listele, log_temizle, kullanici_ekle, kullanici_bul, kullanici_cihaz_ekle, kullanici_cihazlari
from mock_napalm import get_config, backup_config, compare_config, simulate_config
from compliance import compliance_kontrol

app = Flask(__name__)
app.secret_key = "napalm-staj-projesi-2026"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    import sqlite3
    conn = sqlite3.connect("audit.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    if user:
        return User(user[0], user[1])
    return None

init_db()

alerts = []
alerts_lock = threading.Lock()
user_caches = {}
user_caches_lock = threading.Lock()

def sifre_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_napalm_device(host, port):
    from napalm import get_network_driver
    driver = get_network_driver('ios')
    return driver(
        hostname=host,
        username="admin",
        password="cisco123",
        optional_args={
            'port': port,
            'transport': 'telnet',
            'secret': "cisco123",
            'global_delay_factor': 20,
            'read_timeout_override': 600,
            'fast_cli': False,
            'session_timeout': 600,
            'conn_timeout': 120,
        }
    )

def fetch_device(host, port, display_host):
    try:
        dev = get_napalm_device(host, port)
        dev.open()
        facts = dev.get_facts()
        interfaces = dev.get_interfaces()
        ip_data = dev.get_interfaces_ip()
        config = dev.get_config()["running"]
        dev.close()

        result_interfaces = {}
        for name, info in interfaces.items():
            ip = None
            if name in ip_data:
                ips = list(ip_data[name].get("ipv4", {}).keys())
                ip = ips[0] if ips else None
            result_interfaces[name] = {
                "status": "up" if info["is_up"] else "down",
                "ip": ip
            }

        facts["host"] = display_host
        facts["interfaces"] = result_interfaces
        facts["config"] = config
        return facts

    except Exception as e:
        print(f"HATA ({port}): {e}")
        return {
            "host": display_host,
            "hostname": "Ulaşılamıyor",
            "model": "-",
            "uptime": "-",
            "vendor": "-",
            "os_version": "-",
            "interfaces": {},
            "config": ""
        }

def load_user_cache(user_id):
    devices_db = kullanici_cihazlari(user_id)
    print(f"Cihaz sayisi: {len(devices_db)}")

    if not devices_db:
        print("Kayitli cihaz yok!")
        return

    # Tüm cihazlara paralel bağlan
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    result = [None] * len(devices_db)
    
    def fetch_with_index(idx, d):
        print(f"Cihaz cekiliyor: {d}")
        data = fetch_device(d[2], d[3], d[4])
        return idx, data
    
    with ThreadPoolExecutor(max_workers=len(devices_db)) as executor:
        futures = {executor.submit(fetch_with_index, i, d): i for i, d in enumerate(devices_db)}
        for future in as_completed(futures):
            idx, data = future.result()
            result[idx] = data

    with user_caches_lock:
        user_caches[user_id] = result
    print(f"Cache tamamlandi: {user_id}")

def get_user_devices(user_id):
    with user_caches_lock:
        return list(user_caches.get(user_id, []))

def monitor_loop():
    while True:
        time.sleep(30)
        try:
            new_alerts = []
            with user_caches_lock:
                all_devices = []
                for devices in user_caches.values():
                    all_devices.extend(devices)
            for d in all_devices:
                if d["hostname"] == "Ulaşılamıyor":
                    new_alerts.append({
                        "host": d["host"],
                        "mesaj": f"{d['host']} cihazına ulaşılamıyor!",
                        "tip": "danger"
                    })
                for iface, info in d.get("interfaces", {}).items():
                    if info["status"] == "down":
                        new_alerts.append({
                            "host": d["host"],
                            "mesaj": f"{d['hostname']} - {iface} DOWN!",
                            "tip": "warning"
                        })
            with alerts_lock:
                alerts.clear()
                alerts.extend(new_alerts)
        except Exception as e:
            print(f"Monitor HATA: {e}")

threading.Thread(target=monitor_loop, daemon=True).start()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = sifre_hash(request.form.get('password'))
        user = kullanici_bul(username)
        if user and user[2] == password:
            u = User(user[0], user[1])
            login_user(u)
            threading.Thread(target=load_user_cache, args=(u.id,), daemon=True).start()
            return redirect('/')
        flash('Kullanıcı adı veya şifre hatalı.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if len(username) < 3:
            flash('Kullanıcı adı en az 3 karakter olmalı.', 'danger')
            return render_template('register.html')

        if len(password) < 8 or not any(c.isupper() for c in password) or not any(c.isdigit() for c in password):
            flash('Şifre en az 8 karakter, 1 büyük harf ve 1 rakam içermeli.', 'danger')
            return render_template('register.html')

        password_hashed = sifre_hash(password)
        host = request.form.get('host')
        port = int(request.form.get('port'))
        display_host = request.form.get('display_host')
        user_id = kullanici_ekle(username, password_hashed)
        if not user_id:
            flash('Bu kullanıcı adı zaten alınmış.', 'danger')
            return render_template('register.html')
        kullanici_cihaz_ekle(user_id, host, port, display_host)
        flash('Kayıt başarılı, giriş yapabilirsiniz.', 'success')
        return redirect('/login')
    return render_template('register.html')

@app.route('/add_device', methods=['GET', 'POST'])
@login_required
def add_device():
    if request.method == 'POST':
        host = request.form.get('host')
        port = int(request.form.get('port'))
        display_host = request.form.get('display_host')
        kullanici_cihaz_ekle(current_user.id, host, port, display_host)
        # Cache'i yenile
        threading.Thread(target=load_user_cache, args=(current_user.id,), daemon=True).start()
        flash('Cihaz başarıyla eklendi.', 'success')
        return redirect('/')
    return render_template('add_device.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/')
@login_required
def home():
    devices = get_user_devices(current_user.id)
    last_scan = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template('index.html', devices=devices, last_scan=last_scan, username=current_user.username)

@app.route('/api/devices')
@login_required
def api_devices():
    devices = get_user_devices(current_user.id)
    last_scan = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return jsonify({"devices": devices, "last_scan": last_scan})

@app.route('/api/alerts')
@login_required
def get_alerts():
    with alerts_lock:
        return jsonify(list(alerts))

@app.route('/device/<host>')
@login_required
def device_detail(host):
    devices = get_user_devices(current_user.id)
    device = next((d for d in devices if d["host"] == host), None)
    if not device:
        return "Cihaz bulunamadı", 404
    return render_template('detail.html', facts=device, interfaces=device["interfaces"], host=host)

@app.route('/config/<host>')
@login_required
def config_page(host):
    devices = get_user_devices(current_user.id)
    device = next((d for d in devices if d["host"] == host), None)
    current_config = device.get("config", "") if device else ""
    return render_template('config.html', host=host, current_config=current_config, diff=None, new_config=None)

@app.route('/config/<host>/preview', methods=['POST'])
@login_required
def config_preview(host):
    new_config = request.form.get('new_config')
    devices = get_user_devices(current_user.id)
    device = next((d for d in devices if d["host"] == host), None)
    current_config = device.get("config", "") if device else ""
    diff = compare_config(host, new_config)
    log_ekle(host, "CONFIG DIFF", "Diff önizlemesi yapıldı", user_id=current_user.id)
    return render_template('config.html', host=host, current_config=current_config, diff=diff, new_config=new_config)

@app.route('/config/<host>/simulate', methods=['POST'])
@login_required
def config_simulate(host):
    new_config = request.form.get('new_config')
    interfaces, errors = simulate_config(new_config)
    devices = get_user_devices(current_user.id)
    device = next((d for d in devices if d["host"] == host), None)
    current_config = device.get("config", "") if device else ""
    diff = compare_config(host, new_config)
    return render_template('config.html',
        host=host,
        current_config=current_config,
        diff=diff,
        new_config=new_config,
        sim_interfaces=interfaces,
        sim_errors=errors
    )

@app.route('/config/<host>/backup', methods=['POST'])
@login_required
def config_backup(host):
    devices = get_user_devices(current_user.id)
    device = next((d for d in devices if d["host"] == host), None)
    config = device.get("config", "") if device else ""
    if not os.path.exists("backups"):
        os.makedirs("backups")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backups/{host}_{timestamp}.txt"
    with open(filename, "w") as f:
        f.write(config)
    log_ekle(host, "BACKUP", "Config yedeklendi", user_id=current_user.id)
    return redirect(f'/config/{host}?backup=success')

@app.route('/config/<host>/apply', methods=['POST'])
@login_required
def config_apply(host):
    new_config = request.form.get('new_config')
    log_ekle(host, "CONFIG APPLY", "Config değişikliği uygulandı", user_id=current_user.id)
    return redirect(f'/config/{host}?backup=success')

@app.route('/config/<host>/backups')
@login_required
def list_backups(host):
    backup_dir = "backups"
    files = []
    if os.path.exists(backup_dir):
        for f in sorted(os.listdir(backup_dir), reverse=True):
            if f.startswith(host):
                full_path = os.path.join(backup_dir, f)
                size = os.path.getsize(full_path)
                files.append({"name": f, "size": size})
    return render_template('backups.html', host=host, files=files)

@app.route('/config/<host>/backups/download/<filename>')
@login_required
def download_backup(host, filename):
    return send_file(os.path.join("backups", filename), as_attachment=True)

@app.route('/config/<host>/backups/delete/<filename>', methods=['POST'])
@login_required
def delete_backup(host, filename):
    filepath = os.path.join("backups", filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    return redirect(f'/config/{host}/backups')

@app.route('/compliance/<host>')
@login_required
def compliance(host):
    devices = get_user_devices(current_user.id)
    device = next((d for d in devices if d["host"] == host), None)
    config = device.get("config", "") if device else ""
    sonuclar, gecen, toplam = compliance_kontrol(config)
    return render_template('compliance.html', host=host, sonuclar=sonuclar, gecen=gecen, toplam=toplam)

@app.route('/api/bulk_backup', methods=['POST'])
@login_required
def bulk_backup():
    from flask import request as req
    hosts = req.json.get('hosts', [])
    devices = get_user_devices(current_user.id)
    count = 0
    for host in hosts:
        device = next((d for d in devices if d["host"] == host), None)
        if device:
            config = device.get("config", "")
            if not os.path.exists("backups"):
                os.makedirs("backups")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backups/{host}_{timestamp}.txt"
            with open(filename, "w") as f:
                f.write(config)
            log_ekle(host, "BACKUP", "Toplu backup alındı", user_id=current_user.id)
            count += 1
    return jsonify({"message": f"{count} cihazdan backup alındı."})

@app.route('/api/bulk_compliance', methods=['POST'])
@login_required
def bulk_compliance():
    from flask import request as req
    hosts = req.json.get('hosts', [])
    devices = get_user_devices(current_user.id)
    results = []
    for host in hosts:
        device = next((d for d in devices if d["host"] == host), None)
        if device:
            config = device.get("config", "")
            _, gecen, toplam = compliance_kontrol(config)
            results.append({
                "host": host,
                "hostname": device.get("hostname", "-"),
                "skor": round((gecen / toplam) * 100)
            })
    return jsonify({"results": results})

@app.route('/audit')
@login_required
def audit():
    logs = log_listele(current_user.id)
    return render_template('audit.html', logs=logs)

@app.route('/audit/temizle', methods=['POST'])
@login_required
def audit_temizle():
    log_temizle()
    return redirect('/audit')

@app.route('/topology')
@login_required
def topology():
    devices = get_user_devices(current_user.id)
    simple_devices = [{
        "host": d["host"],
        "hostname": d["hostname"],
        "model": d["model"],
        "uptime": d["uptime"],
        "vendor": d.get("vendor", ""),
    } for d in devices]
    return render_template('topology.html', devices=simple_devices)

@app.route('/stats')
@login_required
def stats():
    devices = get_user_devices(current_user.id)
    logs = log_listele(current_user.id)

    compliance_data = []
    for d in devices:
        if d["hostname"] != "Ulaşılamıyor":
            config = d.get("config", "")
            _, gecen, toplam = compliance_kontrol(config)
            compliance_data.append({
                "hostname": d["hostname"],
                "skor": round((gecen / toplam) * 100),
            })

    backup_count = sum(1 for l in logs if l[3] == "BACKUP")
    diff_count = sum(1 for l in logs if l[3] == "CONFIG DIFF")
    apply_count = sum(1 for l in logs if l[3] == "CONFIG APPLY")

    return render_template('stats.html',
        compliance_data=compliance_data,
        backup_count=backup_count,
        diff_count=diff_count,
        apply_count=apply_count,
        total_devices=len(devices)
    )

if __name__ == '__main__':
    app.run(debug=False)