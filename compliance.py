# ============================================================
# COMPLIANCE DENETİM MODÜLÜ
# Cisco cihazlarının güvenlik standartlarına uygunluğunu
# 10 kural üzerinden otomatik olarak denetler.
# ============================================================


# ============================================================
# KURAL SETİ
# Her kural şu alanları içerir:
# - id      : Kural numarası
# - kural   : Kısa kural açıklaması (tabloda gösterilir)
# - aciklama: Detaylı açıklama (neden bu kural var)
# - kontrol : Config metnini alan ve bool dönen lambda fonksiyon
#
# Tüm kontroller büyük/küçük harf duyarsızdır (config.lower()).
# ============================================================

RULES = [
    {
        "id": 1,
        "kural": "Telnet kapalı olmalı",
        "aciklama": "Güvenlik gereği Telnet kullanılmamalı, SSH tercih edilmeli",
        # 'transport input telnet' varsa kural ihlali
        "kontrol": lambda config: "transport input telnet" not in config.lower()
    },
    {
        "id": 2,
        "kural": "SSH aktif olmalı",
        "aciklama": "Uzak yönetim için SSH kullanılmalı",
        # 'ip ssh version' satırı varsa SSH aktif
        "kontrol": lambda config: "ip ssh version" in config.lower()
    },
    {
        "id": 3,
        "kural": "Hostname varsayılan olmamalı",
        "aciklama": "Cihaz hostname'i 'Router' veya 'Switch' olmamalı",
        # Cisco'nun varsayılan hostnameleri kabul edilmez
        "kontrol": lambda config: (
            "hostname router" not in config.lower() and
            "hostname switch" not in config.lower()
        )
    },
    {
        "id": 4,
        "kural": "Kullanıcı tanımlı olmalı",
        "aciklama": "En az bir lokal kullanıcı tanımlanmış olmalı",
        # 'username' satırı en az bir kullanıcının varlığını gösterir
        "kontrol": lambda config: "username" in config.lower()
    },
    {
        "id": 5,
        "kural": "HTTP server kapalı olmalı",
        "aciklama": "Güvenlik gereği HTTP server devre dışı bırakılmalı",
        # 'no ip http server' açıkça kapatılmış olmalı
        "kontrol": lambda config: "no ip http server" in config.lower()
    },
    {
        "id": 6,
        "kural": "CEF aktif olmalı",
        "aciklama": "Performans için Cisco Express Forwarding aktif olmalı",
        # 'ip cef' satırı CEF'in aktif olduğunu gösterir
        "kontrol": lambda config: "ip cef" in config.lower()
    },
    {
        "id": 7,
        "kural": "Domain adı tanımlı olmalı",
        "aciklama": "SSH için ip domain-name tanımlı olmalı",
        # IOS versiyonuna göre 'ip domain name' veya 'ip domain-name' olabilir
        "kontrol": lambda config: (
            "ip domain name" in config.lower() or
            "ip domain-name" in config.lower()
        )
    },
    {
        "id": 8,
        "kural": "VTY login local olmalı",
        "aciklama": "VTY hatlarında login local kullanılmalı",
        # 'login local' lokal kullanıcı veritabanını kullanır
        "kontrol": lambda config: "login local" in config.lower()
    },
    {
        "id": 9,
        "kural": "Service password-encryption aktif olmalı",
        "aciklama": "Şifrelerin şifreli saklanması için aktif olmalı",
        # 'no service password-encryption' varsa devre dışı — kural ihlali
        "kontrol": lambda config: "no service password-encryption" not in config.lower()
    },
    {
        "id": 10,
        "kural": "IP domain lookup kapalı olmalı",
        "aciklama": "Gereksiz DNS sorgularını önlemek için kapalı olmalı",
        # 'no ip domain lookup' varsa DNS sorguları engellenir
        "kontrol": lambda config: "no ip domain lookup" in config.lower()
    },
]


# ============================================================
# COMPLIANCE KONTROL FONKSİYONU
# ============================================================

def compliance_kontrol(config):
    """
    Verilen config metnini tüm kurallara karşı denetler.

    Her kural için kontrol lambda'sı config üzerinde çalıştırılır.
    Sonuç True ise kural geçilmiş, False ise ihlal edilmiş demektir.

    Parametreler:
        config (str): Cihazın running config metni

    Döner:
        sonuclar (list): Her kural için {id, kural, aciklama, durum} dict'i
        gecen (int)    : Geçilen kural sayısı
        toplam (int)   : Toplam kural sayısı (her zaman len(RULES))

    Kullanım:
        sonuclar, gecen, toplam = compliance_kontrol(config)
        skor = round((gecen / toplam) * 100)  # Yüzde skor
    """
    sonuclar = []
    gecen = 0

    for rule in RULES:
        durum = rule["kontrol"](config)
        if durum:
            gecen += 1
        sonuclar.append({
            "id"      : rule["id"],
            "kural"   : rule["kural"],
            "aciklama": rule["aciklama"],
            "durum"   : durum
        })

    return sonuclar, gecen, len(RULES)