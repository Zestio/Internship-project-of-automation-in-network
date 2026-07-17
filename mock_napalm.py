# ============================================================
# CONFIG YÖNETİM MODÜLÜ
# Cihaz konfigürasyonu: backup, diff karşılaştırma ve simülasyon
# ============================================================

import os
import re
from datetime import datetime

# Backup dosyalarının saklanacağı klasör
BACKUP_DIR = "backups"

# ============================================================
# GEÇERLİ IOS KOMUTLARI
# Simülasyon sırasında kabul edilecek komut listesi.
# Bu listede olmayan her komut hata olarak işaretlenir.
# ============================================================

VALID_COMMANDS = [
    "hostname",      # Cihaz adı
    "interface",     # Interface bloğu başlangıcı
    "ip address",    # IP adresi atama
    "no shutdown",   # Interface'i aktif et
    "shutdown",      # Interface'i kapat
    "no ip address", # IP adresini kaldır
    "description",   # Interface açıklaması
    "exit",          # Bloktan çıkış
    "no interface",  # Interface'i kaldır
    "ip route",      # Statik rota ekle
    "no ip route",   # Statik rotayı kaldır
]


# ============================================================
# CONFIG OKUMA
# ============================================================

def get_config(host):
    """
    Belirtilen cihazın çalışan konfigürasyonunu döner.
    Cache'den okur — get_cached_config() app.py'daki
    fetch_device() tarafından doldurulan cache'i kullanır.
    """
    from mock_device import get_cached_config
    return get_cached_config(host)


# ============================================================
# BACKUP İŞLEMLERİ
# ============================================================

def backup_config(host):
    """
    Cihazın mevcut config'ini tarih damgalı dosyaya kaydeder.
    Dosya adı formatı: backups/<host>_<YYYYMMDD_HHMMSS>.txt
    Backups klasörü yoksa otomatik oluşturulur.
    """
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    config = get_config(host)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{BACKUP_DIR}/{host}_{timestamp}.txt"

    with open(filename, "w") as f:
        f.write(config)

    return filename


# ============================================================
# CONFIG KARŞILAŞTIRMA (DIFF)
# ============================================================

def compare_config(host, new_config_lines):
    """
    Mevcut config ile yeni config arasındaki farkı hesaplar.
    
    Satır bazlı karşılaştırma:
    - '+' ile başlayan satırlar: yeni config'de var, eskide yok (eklenen)
    - '-' ile başlayan satırlar: eski config'de var, yenide yok (silinen)
    
    Fark yoksa 'Değişiklik yok' döner.
    """
    current = get_config(host).strip().splitlines()
    new = new_config_lines.strip().splitlines()

    diff = []

    # Yeni config'de olup eskide olmayan satırlar — eklenen
    for line in new:
        if line.strip() not in [l.strip() for l in current]:
            diff.append(f"+ {line}")

    # Eski config'de olup yenide olmayan satırlar — silinen
    for line in current:
        if line.strip() not in [l.strip() for l in new]:
            diff.append(f"- {line}")

    return "\n".join(diff) if diff else "Değişiklik yok"


# ============================================================
# DOĞRULAMA YARDIMCI FONKSİYONLARI
# ============================================================

def is_valid_ip(ip):
    """
    IPv4 adresini doğrular.
    Her oktet 0-255 arasında olmalı, toplam 4 oktet bulunmalı.
    """
    parts = ip.split(".")
    return (
        len(parts) == 4 and
        all(p.isdigit() and 0 <= int(p) <= 255 for p in parts)
    )


def is_valid_interface(ifname):
    """
    Cisco interface adını doğrular.
    
    Geçerli formatlar:
    - GigabitEthernet0/0, FastEthernet0/1
    - Serial0/0, Loopback0, Vlan10
    
    Port numarası 0-9 arasında olmalıdır.
    
    Başarılı: (True, "")
    Başarısız: (False, "hata mesajı")
    """
    pattern = r'^(GigabitEthernet|FastEthernet|Serial|Loopback|Vlan)(\d+)(\/(\d+))?$'
    match = re.match(pattern, ifname, re.IGNORECASE)

    if not match:
        return False, "Geçersiz interface adı (Örnek: GigabitEthernet0/0, Serial0/1, Loopback0)"

    # Port numarası varsa 0-9 arasında olmalı
    if match.group(4) is not None:
        port = int(match.group(4))
        if port > 9:
            return False, f"Geçersiz port numarası: {port} (Port 0-9 arasında olmalı)"

    return True, ""


# ============================================================
# CONFIG SİMÜLASYONU
# ============================================================

def simulate_config(new_config):
    """
    Verilen config metnini satır satır parse eder ve simüle eder.
    
    Gerçek cihaza göndermeden önce:
    - Tanımsız komutları tespit eder
    - IP ve subnet maskesi formatlarını doğrular
    - Interface adlarını doğrular
    - Interface durumlarını (up/down) hesaplar
    - Static route formatlarını kontrol eder
    
    Döner:
    - interfaces: {interface_adı: {status, ip, description}}
    - errors: [hata mesajları listesi]
    
    Hata olsa bile simülasyon devam eder — tüm hatalar toplanır.
    """
    errors = []
    interfaces = {}
    current_interface = None  # Şu an işlenen interface bloğu

    lines = new_config.strip().splitlines()

    for i, line in enumerate(lines, start=1):
        stripped = line.strip()

        # Boş satırları atla
        if not stripped:
            continue

        # Komutun geçerli listede olup olmadığını kontrol et
        valid = any(
            stripped == cmd or stripped.startswith(cmd + " ")
            for cmd in VALID_COMMANDS
        )

        if not valid:
            errors.append(f"Satır {i}: Tanımlanamayan komut → <code>{stripped}</code>")
            continue

        # ── Interface bloğu başlangıcı ──────────────────────
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

            # Yeni interface başlat
            current_interface = ifname
            if current_interface not in interfaces:
                interfaces[current_interface] = {
                    "status": "down",
                    "ip": None,
                    "description": ""
                }

        # ── Global komutlar (interface bloğu dışında) ────────
        elif stripped.startswith("hostname "):
            value = stripped.replace("hostname ", "").strip()
            if not value:
                errors.append(f"Satır {i}: Hostname boş olamaz")

        # ── Interface bloğu içi komutlar ─────────────────────
        elif current_interface:

            if stripped == "no shutdown":
                # Interface'i aktif et
                interfaces[current_interface]["status"] = "up"

            elif stripped == "shutdown":
                # Interface'i kapat
                interfaces[current_interface]["status"] = "down"

            elif stripped.startswith("ip address "):
                # IP ve subnet maskesi doğrula
                parts = stripped.split()
                if len(parts) != 4:
                    errors.append(
                        f"Satır {i}: Hatalı format → <code>{stripped}</code> "
                        f"(Doğru: ip address X.X.X.X X.X.X.X)"
                    )
                else:
                    ip, subnet = parts[2], parts[3]
                    if not is_valid_ip(ip):
                        errors.append(
                            f"Satır {i}: Geçersiz IP → <code>{ip}</code> "
                            f"(Her oktet 0-255 arasında olmalı)"
                        )
                    elif not is_valid_ip(subnet):
                        errors.append(f"Satır {i}: Geçersiz subnet → <code>{subnet}</code>")
                    else:
                        interfaces[current_interface]["ip"] = ip

            elif stripped == "no ip address":
                # IP adresini kaldır
                interfaces[current_interface]["ip"] = None

            elif stripped.startswith("description "):
                # Interface açıklaması
                interfaces[current_interface]["description"] = stripped.replace("description ", "")

            elif stripped == "exit":
                # Interface bloğundan çık
                current_interface = None

            elif stripped.startswith("ip route "):
                # Static route doğrula: ip route <ağ> <mask> <next-hop>
                parts = stripped.split()
                if len(parts) != 4:
                    errors.append(
                        f"Satır {i}: Hatalı route formatı → <code>{stripped}</code> "
                        f"(Doğru: ip route X.X.X.X X.X.X.X X.X.X.X)"
                    )
                else:
                    if not is_valid_ip(parts[2]):
                        errors.append(f"Satır {i}: Geçersiz route ağı → <code>{parts[2]}</code>")
                    elif not is_valid_ip(parts[3]):
                        errors.append(f"Satır {i}: Geçersiz next-hop → <code>{parts[3]}</code>")

        # ── Interface bloğu dışında kullanılamaz komutlar ────
        else:
            if stripped != "exit":
                errors.append(
                    f"Satır {i}: Bu komut interface bloğu dışında kullanılamaz → <code>{stripped}</code>"
                )

    return interfaces, errors