#  NAPALM Tabanlı Multi-Vendor Ağ Yönetim Platformu

Dönem sonu staj projesi kapsamında geliştirilen bu platform, birden fazla Cisco ağ cihazını merkezi bir web arayüzü üzerinden yönetmeyi, konfigürasyon değişikliklerini güvenli şekilde önizlemeyi ve güvenlik denetimi yapmayı sağlar.

---

##  Özellikler

- **Cihaz Envanteri** — Tüm ağ cihazlarının (hostname, model, uptime, interface durumu) tek panelden görüntülenmesi
- **Anlık Tarama** — "Şimdi Tara" butonu ile cihaz verilerinin canlı olarak güncellenmesi
- **Config Yönetimi** — Mevcut konfigürasyonu görüntüleme, değişiklik önizleme (diff), simülasyon ve uygulama
- **Config Simülasyonu** — Yeni config uygulanmadan önce interface durumlarını simüle etme, hatalı komutları tespit etme
- **Backup Sistemi** — Tarih damgalı otomatik yedekleme, yedek listeleme, indirme ve silme
- **Compliance Denetimi** — Cihazların güvenlik standartlarına (SSH, NTP, logging vb.) uygunluğunu otomatik kontrol etme
- **Audit Log** — Tüm işlemlerin (backup, config değişikliği) tarih/saat/host bilgisiyle kayıt altına alınması
- **Multi-Vendor Mimari** — NAPALM kütüphanesi sayesinde Cisco IOS/IOS-XR/NX-OS, Juniper ve Arista cihazlarına aynı kod tabanından bağlanabilme

---

##  Kullanılan Teknolojiler

| Teknoloji | Amaç |
|---|---|
| Python 3 | Ana programlama dili |
| Flask | Web framework (backend) |
| NAPALM | Multi-vendor ağ otomasyon kütüphanesi |
| Netmiko | SSH tabanlı cihaz bağlantısı |
| SQLite | Audit log veritabanı |
| Bootstrap 5 | Frontend UI framework |
| GNS3 | Ağ simülasyon ortamı |

---

##  Proje Yapısı
staj-projesi/
├── app.py              # Flask backend, route'lar
├── mock_device.py      # Cihaz envanter fonksiyonları (mock/gerçek)
├── mock_napalm.py      # Config yönetimi fonksiyonları (mock/gerçek)
├── compliance.py       # Güvenlik denetim kuralları
├── database.py         # SQLite audit log işlemleri
├── templates/
│   ├── index.html      # Ana sayfa - cihaz listesi
│   ├── detail.html     # Cihaz detay sayfası
│   ├── config.html     # Config yönetimi sayfası
│   ├── backups.html    # Backup geçmişi sayfası
│   ├── compliance.html # Compliance denetim sayfası
│   └── audit.html      # Audit log sayfası
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

**4. Uygulamayı başlat:**
```bash
python app.py
```

**5. Tarayıcıda aç:**
http://127.0.0.1:5000
---

##  Gereksinimler (requirements.txt)

flask
napalm
netmiko
---

##  Yol Haritası

- [x] Mock veri ile çalışan dashboard
- [x] Config backup/diff/simülasyon
- [x] Compliance denetim modülü
- [x] Audit log sistemi
- [ ] Gerçek Cisco cihaz entegrasyonu (GNS3 IOS image bekleniyor)
- [ ] Multi-vendor test (Juniper/Arista)

---

##  Not

Proje şu an **mock veri** ile çalışmaktadır. GNS3 ortamında Cisco IOS image temin edildikten sonra `mock_device.py` ve `mock_napalm.py` dosyalarındaki fonksiyonlar gerçek NAPALM/Netmiko bağlantılarıyla değiştirilecektir. Mimari bu geçişe hazır olacak şekilde tasarlanmıştır.
