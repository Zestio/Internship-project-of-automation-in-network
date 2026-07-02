from napalm import get_network_driver

DEVICES = [
    {"host": "192.168.56.101", "port": 5000, "display_host": "192.168.100.1"},
   
]

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
            'global_delay_factor': 2,
            'fast_cli': False,
        }
    )

def fetch_one(d):
    try:
        dev = get_napalm_device(d["port"])
        dev.open()
        facts = dev.get_facts()
        interfaces = dev.get_interfaces()
        ip_data = dev.get_interfaces_ip()
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
            "interfaces": {}
        }

def get_all_devices():
    return [fetch_one(d) for d in DEVICES]

def get_facts(host):
    for d in DEVICES:
        if d["display_host"] == host:
            return fetch_one(d)
    return {}

def get_interfaces(host):
    facts = get_facts(host)
    return facts.get("interfaces", {})