import os
from flask import Flask, render_template, jsonify, request, redirect, send_file
from datetime import datetime
from mock_device import get_all_devices, get_facts, get_interfaces
from mock_napalm import get_config, backup_config, compare_config

app = Flask(__name__)

current_devices = get_all_devices()
last_scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@app.route('/')
def home():
    return render_template('index.html', devices=current_devices, last_scan=last_scan_time)

@app.route('/api/devices')
def api_devices():
    global current_devices, last_scan_time
    current_devices = get_all_devices()
    last_scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return jsonify({"devices": current_devices, "last_scan": last_scan_time})

@app.route('/device/<host>')
def device_detail(host):
    facts = get_facts(host)
    interfaces = get_interfaces(host)
    return render_template('detail.html', facts=facts, interfaces=interfaces, host=host)

@app.route('/config/<host>')
def config_page(host):
    current_config = get_config(host)
    return render_template('config.html', host=host, current_config=current_config, diff=None, new_config=None)

@app.route('/config/<host>/preview', methods=['POST'])
def config_preview(host):
    new_config = request.form.get('new_config')
    diff = compare_config(host, new_config)
    current_config = get_config(host)
    return render_template('config.html', host=host, current_config=current_config, diff=diff, new_config=new_config)

@app.route('/config/<host>/backup', methods=['POST'])
def config_backup(host):
    backup_config(host)
    return redirect(f'/config/{host}?backup=success')

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

if __name__ == '__main__':
    app.run(debug=True)