from netmiko import ConnectHandler

device = {
    'device_type': 'cisco_xr',
    'host': '10.21.25.15',
    'username': 'admin',
    'password': 'QAWSedrf1234!',
}

connection = ConnectHandler(**device)
output = connection.send_command('show version')
print(output)
connection.disconnect()