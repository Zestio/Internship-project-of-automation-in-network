from napalm import get_network_driver
import threading
import time

DEVICES = [
    {"host": "192.168.56.101", "port": 5000, "display_host": "192.168.100.1"},
]

_cache = []
_cache_lock = threading.Lock()
_cache_ready = threading.Event()

def get_napalm_device(port):
    driver = get_network_driver('ios')
    return driver(
        hostname="192.168.56.101",
        username="admin",
        password="cisco123",
        optional_args={
            'port': port,
            'transport': 'telnet',
            'secret': "cisco123",
            'global_delay_factor': 8,
            'read_timeout_override': 180,
            'fast_cli': False,
            'session_timeout': 180,
            'conn_timeout': 60,
        }
    )

def fetch_one(d):
    try:
        dev = get_napalm_device(d["port"])
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
    try:
        dev = get_napalm_device(d["port"])
        dev.open()
        config = dev.get_config()["running"]
        dev.close()
        return config
    except Exception as e:
        print(f"Config HATA ({d['port']}): {e}")
        return ""

def _refresh_cache():
    global _cache
    while True:
        new_data = [fetch_one(d) for d in DEVICES]
        with _cache_lock:
            _cache = new_data
        _cache_ready.set()
        time.sleep(60)

def start_cache():
    t = threading.Thread(target=_refresh_cache, daemon=True)
    t.start()
    print("Cache yükleniyor, lütfen bekleyin...")
    _cache_ready.wait()
    print("Cache hazır, site açılıyor.")

def get_all_devices():
    with _cache_lock:
        return list(_cache)

def get_facts(host):
    with _cache_lock:
        for d in _cache:
            if d["host"] == host:
                return d
    return {}

def get_interfaces(host):
    with _cache_lock:
        for d in _cache:
            if d["host"] == host:
                return d.get("interfaces", {})
    return {}

def get_cached_config(host):
    with _cache_lock:
        for d in _cache:
            if d["host"] == host:
                return d.get("config", "")
    return ""