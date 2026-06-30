import os
from datetime import datetime

# Sahte "running config" - gerçek cihazda bu device.get_config() ile gelir
FAKE_RUNNING_CONFIG = """
hostname Router1
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
interface GigabitEthernet0/1
 ip address 192.168.2.1 255.255.255.0
 shutdown
"""

BACKUP_DIR = "backups"

def get_config(host):
    """Gerçekte: device.get_config()['running']"""
    return FAKE_RUNNING_CONFIG

def backup_config(host):
    """Mevcut config'i tarih damgalı dosyaya kaydeder"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    config = get_config(host)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{BACKUP_DIR}/{host}_{timestamp}.txt"

    with open(filename, "w") as f:
        f.write(config)

    return filename

def compare_config(host, new_config_lines):
    """Gerçekte: device.load_merge_candidate() + device.compare_config()
    Burada basitçe satır satır farkı simüle ediyoruz"""
    current = get_config(host).strip().splitlines()
    new = new_config_lines.strip().splitlines()

    diff = []
    for line in new:
        if line.strip() not in [l.strip() for l in current]:
            diff.append(f"+ {line}")
    for line in current:
        if line.strip() not in [l.strip() for l in new]:
            diff.append(f"- {line}")

    return "\n".join(diff) if diff else "Değişiklik yok"