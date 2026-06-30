from mock_napalm import get_config, backup_config, compare_config

# Mevcut config'i göster
print("=== Mevcut Config ===")
print(get_config("192.168.100.10"))

# Backup al
backup_file = backup_config("192.168.100.10")
print(f"\nBackup alındı: {backup_file}")

# Yeni config ile karşılaştır
new_config = """
hostname Router1
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
interface GigabitEthernet0/1
 ip address 192.168.2.1 255.255.255.0
 no shutdown
"""

print("\n=== Config Diff ===")
print(compare_config("192.168.100.10", new_config))