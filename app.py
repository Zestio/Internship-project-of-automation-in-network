import os
from flask import Flask, render_template, jsonify, request, redirect, send_file
from datetime import datetime
from database import init_db, log_ekle, log_listele, log_temizle
from mock_device import get_all_devices, get_facts, get_interfaces
from mock_napalm import get_config, backup_config, compare_config
from mock_napalm import get_config, backup_config, compare_config, simulate_config
from compliance import compliance_kontrol
import threading
import time
from mock_device import get_all_devices, get_facts, get_interfaces, start_cache


app = Flask(__name__)
init_db()
start_cache()
# Monitoring state
alerts = []
alerts_lock = threading.Lock()

def monitor_devices():
    while True:
        time.sleep(30)
        try:
            devices = get_all_devices()
            new_alerts = []
            for d in devices:
                if d["hostname"] == "Ulaşılamıyor":
                    new_alerts.append({
                        "host": d["host"],
                        "mesaj": f"{d['host']} cihazına ulaşılamıyor!",
                        "tip": "danger"
                    })
                    continue
                for iface, info in d.get("interfaces", {}).items():
                    if info["status"] == "down":
                        new_alerts.append({
                            "host": d["host"],
                            "mesaj": f"{d['hostname']} - {iface} interface DOWN!",
                            "tip": "warning"
                        })
            with alerts_lock:
                alerts.clear()
                alerts.extend(new_alerts)
        except Exception as e:
            print(f"Monitor HATA: {e}")

monitor_thread = threading.Thread(target=monitor_devices, daemon=True)
monitor_thread.start()
current_devices = get_all_devices()
last_scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@app.route('/')
def home():
    return render_template('index.html', devices=current_devices, last_scan=last_scan_time)

@app.route('/config/<host>/apply', methods=['POST'])
def config_apply(host):
    from mock_napalm import FAKE_RUNNING_CONFIG
    import mock_napalm
    new_config = request.form.get('new_config')
    mock_napalm.FAKE_RUNNING_CONFIG = new_config
    log_ekle(host, "CONFIG APPLY", "Config değişikliği uygulandı")
    return redirect(f'/config/{host}?backup=success')

@app.route('/api/alerts')
def get_alerts():
    with alerts_lock:
        return jsonify(list(alerts))

@app.route('/topology')
def topology():
    devices = get_all_devices()
    # Config'i topoloji sayfasına gönderme
    simple_devices = [{
        "host": d["host"],
        "hostname": d["hostname"],
        "model": d["model"],
        "uptime": d["uptime"],
        "vendor": d.get("vendor", ""),
    } for d in devices]
    return render_template('topology.html', devices=simple_devices)

@app.route('/compliance/<host>')
def compliance(host):
    from mock_napalm import get_config
    config = get_config(host)
    sonuclar, gecen, toplam = compliance_kontrol(config)
    return render_template('compliance.html',
        host=host,
        sonuclar=sonuclar,
        gecen=gecen,
        toplam=toplam
    )

@app.route('/config/<host>/simulate', methods=['POST'])
def config_simulate(host):
    new_config = request.form.get('new_config')
    interfaces, errors = simulate_config(new_config)
    current_config = get_config(host)
    diff = compare_config(host, new_config)
    return render_template('config.html',
        host=host,
        current_config=current_config,
        diff=diff,
        new_config=new_config,
        sim_interfaces=interfaces,
        sim_errors=errors
    )

@app.route('/api/devices')
def api_devices():
    global current_devices, last_scan_time
    current_devices = get_all_devices()
    last_scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return jsonify({"devices": current_devices, "last_scan": last_scan_time})

@app.route('/device/<host>')
def device_detail(host):
    device = next((d for d in current_devices if d["host"] == host), None)
    if not device:
        return "Cihaz bulunamadı", 404
    return render_template('detail.html', facts=device, interfaces=device["interfaces"], host=host)

@app.route('/config/<host>')
def config_page(host):
    current_config = get_config(host)
    return render_template('config.html', host=host, current_config=current_config, diff=None, new_config=None)

@app.route('/config/<host>/backup', methods=['POST'])
def config_backup(host):
    backup_config(host)
    log_ekle(host, "BACKUP", "Config yedeklendi")
    return redirect(f'/config/{host}?backup=success')

@app.route('/config/<host>/preview', methods=['POST'])
def config_preview(host):
    new_config = request.form.get('new_config')
    diff = compare_config(host, new_config)
    current_config = get_config(host)
    log_ekle(host, "CONFIG DIFF", f"Diff önizlemesi yapıldı")
    return render_template('config.html', host=host, current_config=current_config, diff=diff, new_config=new_config)

@app.route('/config/<host>/backups')
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
def download_backup(host, filename):
    return send_file(os.path.join("backups", filename), as_attachment=True)

@app.route('/audit')
def audit():
    logs = log_listele()
    return render_template('audit.html', logs=logs)

@app.route('/audit/temizle', methods=['POST'])
def audit_temizle():
    log_temizle()
    return redirect('/audit')

@app.route('/config/<host>/backups/delete/<filename>', methods=['POST'])
def delete_backup(host, filename):
    filepath = os.path.join("backups", filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    return redirect(f'/config/{host}/backups')

if __name__ == '__main__':
    app.run(debug=True)