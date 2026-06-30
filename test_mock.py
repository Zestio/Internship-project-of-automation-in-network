from mock_device import get_facts, get_interfaces

facts = get_facts("192.168.100.10")
print("Facts:", facts)

interfaces = get_interfaces("192.168.100.10")
print("Interfaces:", interfaces)