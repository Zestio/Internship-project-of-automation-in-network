from napalm import get_network_driver

driver = get_network_driver('ios')
device = driver(
    hostname='192.168.56.101',
    username='admin',
    password='cisco123',
    optional_args={
        'port': 5000,
        'transport': 'telnet',
        'secret': 'cisco123',
    }
)

device.open()
facts = device.get_facts()
print(facts)
device.close()