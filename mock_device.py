import random

DEVICES = ["192.168.100.10", "192.168.100.11", "192.168.100.12"]

def get_facts(host):
    return {
        "hostname": f"Router-{host.split('.')[-1]}",
        "vendor": "Cisco",
        "model": "3725",
        "os_version": "12.4(15)T14",
        "uptime": f"{random.randint(1,30)} days",
        "host": host
    }

def get_interfaces(host):
    statuses = ["up", "down"]
    return {
        "Gi0/0": {"status": random.choice(statuses), "ip": "192.168.1.1"},
        "Gi0/1": {"status": random.choice(statuses), "ip": "192.168.1.2"},
    }

def get_all_devices():
    result = []
    for host in DEVICES:
        facts = get_facts(host)
        facts["interfaces"] = get_interfaces(host)
        result.append(facts)
    return result