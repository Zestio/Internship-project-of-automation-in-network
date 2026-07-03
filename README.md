#  NAPALM Tabanlı Multi-Vendor Ağ Yönetim Platformu

Dönem sonu staj projesi kapsamında geliştirilen bu platform, birden fazla Cisco ağ cihazını merkezi bir web arayüzü üzerinden yönetmeyi, konfigürasyon değişikliklerini güvenli şekilde önizlemeyi, güvenlik denetimi yapmayı ve gerçek zamanlı izleme sağlamayı hedeflemektedir.

---

##  Özellikler

- **Cihaz Envanteri** — Tüm ağ cihazlarının (hostname, model, uptime, interface durumu) tek panelden görüntülenmesi
- **Anlık Tarama** — "Şimdi Tara" butonu ile cihaz verilerinin canlı olarak güncellenmesi
- **Gerçek Zamanlı İzleme** — Arka planda otomatik cihaz kontrolü, interface down veya cihaza ulaşılamaz durumunda anında uyarı
- **Ağ Topoloji Haritası** — Cihazların birbirine bağlantısını görsel olarak gösteren interaktif harita
- **Config Yönetimi** — Mevcut konfigürasyonu görüntüleme, değişiklik önizleme (diff), simülasyon ve uygulama
- **Config Simülasyonu** — Yeni config uygulanmadan önce interface durumlarını simüle etme, hatalı komutları tespit etme (IP, interface, syntax validasyonu)
- **Backup Sistemi** — Tarih damgalı otomatik yedekleme, yedek listeleme, indirme ve silme
- **Compliance Denetimi** — Cihazların güvenlik standartlarına (SSH, NTP, logging, HTTP kapalı vb.) uygunluğunu otomatik kontrol etme
- **Audit Log** — Tüm işlemlerin (backup, config değişikliği) tarih/saat/host bilgisiyle kayıt altına alınması
- **Cache Sistemi** — Arka planda periyodik veri güncelleme, sayfa açılışlarında anlık yanıt
- **Multi-Vendor Mimari** — NAPALM kütüphanesi sayesinde Cisco IOS/IOS-XR/NX-OS, Juniper ve Arista cihazlarına aynı kod tabanından bağlanabilme

---

##  Kullanılan Teknolojiler

| Teknoloji | Amaç |
|---|---|
| Python 3 | Ana programlama dili |
| Flask | Web framework (backend) |
| NAPALM | Multi-vendor ağ otomasyon kütüphanesi |
| Netmiko | SSH/Telnet tabanlı cihaz bağlantısı |
| SQLite | Audit log veritabanı |
| Bootstrap 5 | Frontend UI framework |
| vis.js | Ağ topoloji görselleştirme |
| GNS3 | Ağ simülasyon ortamı (Cisco 3725) |

---

##  Proje Yapısı
staj-projesi/
├── app.py              # Flask backend, route'lar
├── mock_device.py      # Cihaz envanter fonksiyonları (NAPALM/cache)
├── mock_napalm.py      # Config yönetimi fonksiyonları
├── compliance.py       # Güvenlik denetim kuralları
├── database.py         # SQLite audit log işlemleri
├── templates/
│   ├── index.html      # Ana sayfa - cihaz listesi + uyarılar
│   ├── detail.html     # Cihaz detay sayfası
│   ├── config.html     # Config yönetimi sayfası
│   ├── backups.html    # Backup geçmişi sayfası
│   ├── compliance.html # Compliance denetim sayfası
│   ├── audit.html      # Audit log sayfası
│   └── topology.html   # Ağ topoloji haritası
├── backups/            # Config yedek dosyaları
├── audit.db            # SQLite veritabanı
└── requirements.txt    # Python bağımlılıkları
---

##  Kurulum

**1. Repoyu klonla:**
```bash
git clone https://github.com/Zestio/Internship-project-of-automation-in-network.git
cd Internship-project-of-automation-in-network
```

**2. Virtual environment oluştur ve aktif et:**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

**3. Bağımlılıkları kur:**
```bash
pip install -r requirements.txt
```

**4. GNS3 ortamını hazırla:**
- GNS3 ve VirtualBox kurulu olmalı
- Cisco 3725 IOS image GNS3'e eklenmiş olmalı
- En az 1 router çalışıyor olmalı (SSH/Telnet aktif)

**5. Uygulamayı başlat:**
```bash
python app.py
```

**6. Tarayıcıda aç:**
http://127.0.0.1:5000
---

##  Gereksinimler (requirements.txt)
flask
napalm
netmiko
---

##  Yol Haritası

- [x] Gerçek Cisco 3725 cihaz entegrasyonu (NAPALM/Netmiko via GNS3)
- [x] Çok cihazlı envanter dashboard
- [x] Config backup/diff/simülasyon/uygulama
- [x] Config validasyonu (IP, interface, syntax kontrolü)
- [x] Compliance denetim modülü (10 güvenlik kuralı)
- [x] SQLite audit log sistemi
- [x] Gerçek zamanlı izleme ve uyarı sistemi
- [x] Ağ topoloji haritası (vis.js)
- [x] Cache sistemi ile performans optimizasyonu
- [x] Grafik/istatistik sayfası
- [ ] Toplu işlem (birden fazla cihaza aynı anda işlem)
- [ ] Kullanıcı girişi (login sistemi)
