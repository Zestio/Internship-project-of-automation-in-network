RULES = [
    {
        "id": 1,
        "kural": "Telnet kapalı olmalı",
        "aciklama": "Güvenlik gereği Telnet kullanılmamalı, SSH tercih edilmeli",
        "kontrol": lambda config: "transport input telnet" not in config.lower()
    },
    {
        "id": 2,
        "kural": "SSH aktif olmalı",
        "aciklama": "Uzak yönetim için SSH kullanılmalı",
        "kontrol": lambda config: "ip ssh version" in config.lower()
    },
    {
        "id": 3,
        "kural": "Hostname varsayılan olmamalı",
        "aciklama": "Cihaz hostname'i 'Router' veya 'Switch' olmamalı",
        "kontrol": lambda config: (
            "hostname router" not in config.lower() and
            "hostname switch" not in config.lower()
        )
    },
    {
        "id": 4,
        "kural": "Kullanıcı tanımlı olmalı",
        "aciklama": "En az bir lokal kullanıcı tanımlanmış olmalı",
        "kontrol": lambda config: "username" in config.lower()
    },
    {
        "id": 5,
        "kural": "HTTP server kapalı olmalı",
        "aciklama": "Güvenlik gereği HTTP server devre dışı bırakılmalı",
        "kontrol": lambda config: "no ip http server" in config.lower()
    },
    {
        "id": 6,
        "kural": "CEF aktif olmalı",
        "aciklama": "Performans için Cisco Express Forwarding aktif olmalı",
        "kontrol": lambda config: "ip cef" in config.lower()
    },
    {
        "id": 7,
        "kural": "Domain adı tanımlı olmalı",
        "aciklama": "SSH için ip domain-name tanımlı olmalı",
        "kontrol": lambda config: "ip domain name" in config.lower() or "ip domain-name" in config.lower()
    },
    {
        "id": 8,
        "kural": "VTY login local olmalı",
        "aciklama": "VTY hatlarında login local kullanılmalı",
        "kontrol": lambda config: "login local" in config.lower()
    },
    {
        "id": 9,
        "kural": "Service password-encryption aktif olmalı",
        "aciklama": "Şifrelerin şifreli saklanması için aktif olmalı",
        "kontrol": lambda config: "no service password-encryption" not in config.lower()
    },
    {
        "id": 10,
        "kural": "IP domain lookup kapalı olmalı",
        "aciklama": "Gereksiz DNS sorgularını önlemek için kapalı olmalı",
        "kontrol": lambda config: "no ip domain lookup" in config.lower()
    },
]

def compliance_kontrol(config):
    sonuclar = []
    gecen = 0
    for rule in RULES:
        durum = rule["kontrol"](config)
        if durum:
            gecen += 1
        sonuclar.append({
            "id": rule["id"],
            "kural": rule["kural"],
            "aciklama": rule["aciklama"],
            "durum": durum
        })
    return sonuclar, gecen, len(RULES)