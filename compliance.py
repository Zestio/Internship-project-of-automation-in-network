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
        "kontrol": lambda config: "transport input ssh" in config.lower() or "ip ssh version" in config.lower()
    },
    {
        "id": 3,
        "kural": "Hostname varsayılan olmamalı",
        "aciklama": "Cihaz hostname'i 'Router' veya 'Switch' olmamalı",
        "kontrol": lambda config: not any(
            f"hostname {h}" in config.lower()
            for h in ["router", "switch"]
        )
    },
    {
        "id": 4,
        "kural": "Enable secret tanımlı olmalı",
        "aciklama": "Cihazda şifreli enable password bulunmalı",
        "kontrol": lambda config: "enable secret" in config.lower()
    },
    {
        "id": 5,
        "kural": "NTP sunucusu tanımlı olmalı",
        "aciklama": "Zaman senkronizasyonu için NTP ayarlanmalı",
        "kontrol": lambda config: "ntp server" in config.lower()
    },
    {
        "id": 6,
        "kural": "Şifreler şifreli tutulmalı",
        "aciklama": "service password-encryption aktif olmalı",
        "kontrol": lambda config: "service password-encryption" in config.lower()
    },
    {
        "id": 7,
        "kural": "Logging aktif olmalı",
        "aciklama": "Cihaz logları bir sunucuya gönderilmeli",
        "kontrol": lambda config: "logging" in config.lower()
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