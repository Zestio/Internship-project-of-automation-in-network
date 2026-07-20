# ============================================================
# CİHAZ VERİ MODÜLÜ (mock_device.py)
# Ağ cihazlarından veri çekme ve cache yönetimi
# Not: Bu modül artık sadece get_cached_config() ile kullanılır.
# Asıl bağlantı app.py'daki fetch_device() (Netmiko) üzerinden yapılır.
# ============================================================

from napalm import get_network_driver
import threading
import time

# ============================================================
# CİHAZ LİSTESİ
# Her cihaz için GNS3 VM bağlantı bilgileri.
# host: GNS3 VM IP adresi
# port: Telnet konsol portu
# display_host: Arayüzde gösterilecek IP adresi
# ============================================================

DEVICES = [
    {"host": "192.168.56.101", "port": 5000, "display_host": "192.168.100.1"},
]

# ============================================================
# CACHE YÖNETİMİ
# Thread-safe cache sistemi.
# _cache: Cihaz verilerini tutan liste
# _cache_lock: Eşzamanlı erişimi önlemek için kilit
# _cache_ready: İlk yüklemenin tamamlandığını bildiren event
# ============================================================

_cache = []
_cache_lock = threading.Lock()
_cache_ready = threading.Event()


# ============================================================
# NAPALM BAĞLANTI FONKSİYONU
# ============================================================

def get_napalm_device(port):
    """
    NAPALM ile Cisco IOS cihazına Telnet bağlantısı kurar.
    GNS3 ortamının gecikmelerine karşı yüksek timeout değerleri kullanılır.
    global_cmd_verify=False: GNS3 buffer sorunlarını azaltır.
    """
    driver = get_network_driver('ios')
    return driver(
        hostname="192.168.56.101",
        username="admin",
        password="cisco123",
        optional_args={
            'port': port,
            'transport': 'telnet',
            'secret': "cisco123",
            'global_delay_factor': 25,
            'read_timeout_override': 600,
            'fast_cli': False,
            'session_timeout': 600,
            'conn_timeout': 120,
            'global_cmd_verify': False,
        }
    )


# ============================================================
# CİHAZ VERİSİ ÇEKME FONKSİYONLARI
# ============================================================

def fetch_one(d):
    """
    Tek bir cihazdan NAPALM ile tüm verileri çeker:
    - Genel bilgiler (hostname, model, uptime vb.)
    - Interface durumları ve IP adresleri
    - Çalışan konfigürasyon

    Başarısız olursa 'Ulaşılamıyor' durumunda boş nesne döner.
    """
    try:
        dev = get_napalm_device(d["port"])
        dev.open()

        facts = dev.get_facts()           # Hostname, model, uptime vb.
        interfaces = dev.get_interfaces() # Interface up/down durumları
        ip_data = dev.get_interfaces_ip() # Interface IP adresleri
        config = dev.get_config()["running"]  # Running config

        dev.close()

        # Interface bilgilerini standart formata dönüştür
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

        facts["host"] = d["display_host"]
        facts["interfaces"] = result_interfaces
        facts["config"] = config
        return facts

    except Exception as e:
        print(f"HATA ({d['port']}): {e}")
        return {
            "host": d["display_host"],
            "hostname": "Ulaşılamıyor",
            "model": "-",
            "uptime": "-",
            "vendor": "-",
            "os_version": "-",
            "interfaces": {},
            "config": ""
        }


def fetch_config(d):
    """
    Sadece running config'i çeker.
    fetch_one()'dan daha hafif — config güncelleme gerektiğinde kullanılır.
    """
    try:
        dev = get_napalm_device(d["port"])
        dev.open()
        config = dev.get_config()["running"]
        dev.close()
        return config
    except Exception as e:
        print(f"Config HATA ({d['port']}): {e}")
        return ""


# ============================================================
# CACHE YENİLEME DÖNGÜSÜ
# ============================================================

def _refresh_cache():
    """
    Arka planda sürekli çalışan cache yenileme döngüsü.
    Her 60 saniyede bir tüm cihazlardan veri çeker ve cache'i günceller.
    İlk çalışmada _cache_ready event'ini set ederek start_cache()'in
    bekleme döngüsünü serbest bırakır.
    """
    global _cache
    while True:
        new_data = [fetch_one(d) for d in DEVICES]
        with _cache_lock:
            _cache = new_data
        _cache_ready.set()   # İlk yükleme tamamlandı sinyali
        time.sleep(60)       # 60 saniye bekle, sonra yenile


def start_cache():
    """
    Cache sistemini başlatır.
    Arka planda _refresh_cache() thread'ini başlatır ve
    ilk veri yüklemesi tamamlanana kadar bekler.
    Flask uygulaması başlamadan önce çağrılmalıdır.
    """
    t = threading.Thread(target=_refresh_cache, daemon=True)
    t.start()
    print("Cache yükleniyor, lütfen bekleyin...")
    _cache_ready.wait()  # İlk yükleme tamamlanana kadar bekle
    print("Cache hazır, site açılıyor.")


# ============================================================
# CACHE'DEN VERİ OKUMA FONKSİYONLARI (Thread-Safe)
# ============================================================

def get_all_devices():
    """Cache'deki tüm cihazların listesini döner."""
    with _cache_lock:
        return list(_cache)


def get_facts(host):
    """
    Belirtilen display_host'a ait cihaz bilgilerini cache'den döner.
    Bulunamazsa boş dict döner.
    """
    with _cache_lock:
        for d in _cache:
            if d["host"] == host:
                return d
    return {}


def get_interfaces(host):
    """
    Belirtilen cihazın interface bilgilerini cache'den döner.
    Bulunamazsa boş dict döner.
    """
    with _cache_lock:
        for d in _cache:
            if d["host"] == host:
                return d.get("interfaces", {})
    return {}


def get_cached_config(host):
    """
    Belirtilen cihazın running config'ini cache'den döner.
    mock_napalm.py'daki get_config() tarafından çağrılır.
    Bulunamazsa boş string döner.
    """
    with _cache_lock:
        for d in _cache:
            if d["host"] == host:
                return d.get("config", "")
    return ""