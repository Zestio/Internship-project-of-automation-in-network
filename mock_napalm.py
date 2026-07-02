import os
import re
from datetime import datetime

BACKUP_DIR = "backups"

FAKE_RUNNING_CONFIG = """
hostname Router1
service password-encryption
line vty 0 4
logging 192.168.1.200
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
interface GigabitEthernet0/1
 ip address 192.168.2.1 255.255.255.0
 shutdown
"""

VALID_COMMANDS = [
    "hostname",
    "interface",
    "ip address",
    "no shutdown",
    "shutdown",
    "no ip address",
    "description",
    "exit",
    "no interface",
    "ip route",
    "no ip route",
]

FAKE_CONFIGS = {
    "192.168.100.10": """
hostname Router-10
enable secret 5 $1$mERr$hx5rVt7rPNoS4wqbXKX7m0
service password-encryption
ip ssh version 2
line vty 0 4
 transport input ssh
ntp server 192.168.1.100
logging 192.168.1.200
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
interface GigabitEthernet0/1
 ip address 192.168.2.1 255.255.255.0
 shutdown
""",
    "192.168.100.11": """
hostname Router-11
interface GigabitEthernet0/0
 ip address 192.168.3.1 255.255.255.0
 no shutdown
interface GigabitEthernet0/1
 ip address 192.168.4.1 255.255.255.0
 shutdown
""",
    "192.168.100.12": """
hostname Router-12
enable secret 5 $1$mERr$hx5rVt7rPNoS4wqbXKX7m0
ip ssh version 2
line vty 0 4
 transport input ssh
interface GigabitEthernet0/0
 ip address 192.168.5.1 255.255.255.0
 no shutdown
""",
}

def get_config(host):
    from mock_device import get_napalm_device, DEVICES
    d = next((d for d in DEVICES if d["display_host"] == host), None)
    if not d:
        return ""
    try:
        dev = get_napalm_device(d["port"])
        dev.open()
        config = dev.get_config()["running"]
        dev.close()
        return config
    except Exception as e:
        print(f"Config HATA: {e}")
        return ""

def backup_config(host):
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    config = get_config(host)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{BACKUP_DIR}/{host}_{timestamp}.txt"
    with open(filename, "w") as f:
        f.write(config)
    return filename

def compare_config(host, new_config_lines):
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

def is_valid_ip(ip):
    parts = ip.split(".")
    return (
        len(parts) == 4 and
        all(p.isdigit() and 0 <= int(p) <= 255 for p in parts)
    )

def is_valid_interface(ifname):
    # Geçerli interface tipleri
    pattern = r'^(GigabitEthernet|FastEthernet|Serial|Loopback|Vlan)(\d+)(\/(\d+))?$'
    match = re.match(pattern, ifname, re.IGNORECASE)
    if not match:
        return False, "Geçersiz interface adı (Örnek: GigabitEthernet0/0, Serial0/1, Loopback0)"
    
    # Port numarası kontrolü
    if match.group(4) is not None:
        port = int(match.group(4))
        if port > 9:
            return False, f"Geçersiz port numarası: {port} (Port 0-9 arasında olmalı)"
    
    return True, ""

def simulate_config(new_config):
    errors = []
    interfaces = {}
    current_interface = None

    lines = new_config.strip().splitlines()

    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped:
            continue

        # Geçerli komut kontrolü
        valid = any(
            stripped == cmd or stripped.startswith(cmd + " ")
            for cmd in VALID_COMMANDS
        )

        if not valid:
            errors.append(f"Satır {i}: Tanımlanamayan komut → <code>{stripped}</code>")
            continue

        if stripped.startswith("interface "):
            ifname = stripped.replace("interface ", "").strip()
            if not ifname:
                errors.append(f"Satır {i}: Interface adı boş olamaz")
                current_interface = None
                continue

            gecerli, hata_mesaji = is_valid_interface(ifname)
            if not gecerli:
                errors.append(f"Satır {i}: {hata_mesaji} → <code>{ifname}</code>")
                current_interface = None
                continue

            current_interface = ifname
            if current_interface not in interfaces:
                interfaces[current_interface] = {
                    "status": "down",
                    "ip": None,
                    "description": ""
                }

        elif stripped.startswith("hostname "):
            value = stripped.replace("hostname ", "").strip()
            if not value:
                errors.append(f"Satır {i}: Hostname boş olamaz")

        elif current_interface:
            if stripped == "no shutdown":
                interfaces[current_interface]["status"] = "up"

            elif stripped == "shutdown":
                interfaces[current_interface]["status"] = "down"

            elif stripped.startswith("ip address "):
                parts = stripped.split()
                if len(parts) != 4:
                    errors.append(f"Satır {i}: Hatalı format → <code>{stripped}</code> (Doğru: ip address X.X.X.X X.X.X.X)")
                else:
                    ip, subnet = parts[2], parts[3]
                    if not is_valid_ip(ip):
                        errors.append(f"Satır {i}: Geçersiz IP → <code>{ip}</code> (Her oktet 0-255 arasında olmalı)")
                    elif not is_valid_ip(subnet):
                        errors.append(f"Satır {i}: Geçersiz subnet → <code>{subnet}</code>")
                    else:
                        interfaces[current_interface]["ip"] = ip

            elif stripped == "no ip address":
                interfaces[current_interface]["ip"] = None

            elif stripped.startswith("description "):
                value = stripped.replace("description ", "").strip()
                interfaces[current_interface]["description"] = value

            elif stripped == "exit":
                current_interface = None

            elif stripped.startswith("ip route "):
                parts = stripped.split()
                if len(parts) != 4:
                    errors.append(f"Satır {i}: Hatalı route formatı → <code>{stripped}</code> (Doğru: ip route X.X.X.X X.X.X.X X.X.X.X)")
                else:
                    if not is_valid_ip(parts[2]):
                        errors.append(f"Satır {i}: Geçersiz route ağı → <code>{parts[2]}</code>")
                    elif not is_valid_ip(parts[3]):
                        errors.append(f"Satır {i}: Geçersiz next-hop → <code>{parts[3]}</code>")

        else:
            if stripped != "exit":
                errors.append(f"Satır {i}: Bu komut interface bloğu dışında kullanılamaz → <code>{stripped}</code>")

    return interfaces, errors