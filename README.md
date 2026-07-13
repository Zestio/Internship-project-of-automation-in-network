# 🌐 NAPALM Tabanlı Multi-Vendor Ağ Yönetim Platformu

Dönem sonu staj projesi kapsamında geliştirilen bu platform, birden fazla Cisco ağ cihazını merkezi bir web arayüzü üzerinden yönetmeyi, konfigürasyon değişikliklerini güvenli şekilde önizlemeyi, güvenlik denetimi yapmayı ve gerçek zamanlı izleme sağlamayı hedeflemektedir.

---

## 🚀 Özellikler

- **Kullanıcı Yönetimi** — Kayıt/giriş sistemi, rol tabanlı yetkilendirme (Admin/Readonly), şifre değiştirme, hesap silme
- **Çok Cihaz Desteği** — Her kullanıcı kendi router'larını ekleyip yönetebilir, paralel bağlantı ile hızlı veri çekimi
- **Cihaz Envanteri** — Tüm ağ cihazlarının (hostname, model, uptime, interface durumu) tek panelden görüntülenmesi
- **Anlık Tarama** — "Şimdi Tara" butonu ile cihaz verilerinin canlı olarak güncellenmesi
- **Gerçek Zamanlı İzleme** — Arka planda otomatik cihaz kontrolü, interface down veya cihaza ulaşılamaz durumunda anında uyarı ve e-posta bildirimi
- **E-posta Bildirimi** — Interface down veya cihaza ulaşılamaz durumunda Gmail üzerinden otomatik alarm e-postası (5 dakikada bir)
- **Ağ Topoloji Haritası** — Cihazların birbirine bağlantısını görsel olarak gösteren interaktif harita (vis.js)
- **Config Yönetimi** — Mevcut konfigürasyonu görüntüleme, değişiklik önizleme (diff), simülasyon ve uygulama
- **Config Simülasyonu** — Yeni config uygulanmadan önce interface durumlarını simüle etme, hatalı komutları tespit etme (IP, interface, syntax validasyonu)
- **Config Versiyonlama** — Backup'lar arası diff karşılaştırması
- **Backup Sistemi** — Tarih damgalı otomatik yedekleme, yedek listeleme, indirme ve silme
- **Toplu İşlem** — Birden fazla cihazı seçip aynı anda backup alma veya compliance denetimi yapma
- **Compliance Denetimi** — Cihazların güvenlik standartlarına (SSH, NTP, logging, HTTP kapalı vb.) uygunluğunu otomatik kontrol etme (10 kural)
- **Audit Log** — Tüm işlemlerin (backup, config değişikliği) tarih/saat/host/kullanıcı bilgisiyle kayıt altına alınması
- **Cihaz Durum Geçmişi** — Interface down olaylarının tarihli kaydı
- **İstatistik/Grafik Sayfası** — Compliance skorları, backup sayıları, audit log dağılımı (Chart.js)
- **Export Özelliği** — Cihaz listesini Excel, compliance raporunu PDF olarak indirme
- **Ping & Port Tarama** — Cihaza ping atma ve Telnet portunun açık olup olmadığını kontrol etme
- **Profil Sayfası** — Kullanıcı bilgileri, rol, son giriş zamanı, istatistikler
- **Cache Sistemi** — Arka planda periyodik veri güncelleme, sayfa açılışlarında anlık yanıt
- **Multi-Vendor Mimari** — NAPALM kütüphanesi sayesinde Cisco IOS/IOS-XR/NX-OS, Juniper ve Arista cihazlarına aynı kod tabanından bağlanabilme

---

## 🛠️ Kullanılan Teknolojiler

| Teknoloji | Amaç |
|---|---|
| Python 3 | Ana programlama dili |
| Flask | Web framework (backend) |
| NAPALM | Multi-vendor ağ otomasyon kütüphanesi |
| Netmiko | SSH/Telnet tabanlı cihaz bağlantısı |
| SQLite | Kullanıcı, cihaz ve audit log veritabanı |
| Flask-Login | Kullanıcı oturum yönetimi |
| Bootstrap 5 | Frontend UI framework |
| Chart.js | İstatistik grafikleri |
| vis.js | Ağ topoloji görselleştirme |
| openpyxl | Excel export |
| ReportLab | PDF export |
| GNS3 | Ağ simülasyon ortamı (Cisco 3725) |

---

## 📁 Proje Yapısı

staj-projesi/
├── app.py                  # Flask backend, tüm route'lar
├── mock_napalm.py          # Config yönetimi fonksiyonları
├── compliance.py           # Güvenlik denetim kuralları (10 kural)
├── database.py             # SQLite veritabanı işlemleri
├── templates/
│   ├── index.html          # Ana sayfa - cihaz listesi + uyarılar
│   ├── detail.html         # Cihaz detay sayfası
│   ├── config.html         # Config yönetimi sayfası
│   ├── config_versions.html # Config versiyonlama
│   ├── backups.html        # Backup geçmişi sayfası
│   ├── compliance.html     # Compliance denetim sayfası
│   ├── audit.html          # Audit log sayfası
│   ├── topology.html       # Ağ topoloji haritası
│   ├── stats.html          # İstatistik/grafik sayfası
│   ├── device_history.html # Cihaz durum geçmişi
│   ├── profile.html        # Kullanıcı profil sayfası
│   ├── login.html          # Giriş sayfası
│   ├── register.html       # Kayıt sayfası
│   ├── add_device.html     # Cihaz ekleme sayfası
│   ├── admin_users.html    # Kullanıcı yönetimi (admin)
│   ├── email_settings.html # E-posta ayarları
│   ├── change_password.html # Şifre değiştirme
│   └── delete_account.html # Hesap silme
├── backups/                # Config yedek dosyaları
├── audit.db                # SQLite veritabanı
└── requirements.txt        # Python bağımlılıkları

---

## ⚙️ Kurulum

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

## 📋 Gereksinimler
flask
napalm
netmiko
flask-login
openpyxl
reportlab
pysnmp
---

## 🗺️ Yol Haritası

- [x] Gerçek Cisco 3725 cihaz entegrasyonu (NAPALM/Netmiko via GNS3)
- [x] Çok kullanıcılı sistem (kayıt, giriş, rol tabanlı yetkilendirme)
- [x] Çok cihazlı envanter dashboard
- [x] Config backup/diff/simülasyon/uygulama/versiyonlama
- [x] Config validasyonu (IP, interface, syntax kontrolü)
- [x] Compliance denetim modülü (10 güvenlik kuralı)
- [x] SQLite audit log sistemi (kullanıcıya özel)
- [x] Gerçek zamanlı izleme ve uyarı sistemi
- [x] E-posta bildirimi (Gmail SMTP)
- [x] Ağ topoloji haritası (vis.js)
- [x] Cache sistemi ile performans optimizasyonu
- [x] Toplu işlem (backup ve compliance)
- [x] Export özelliği (Excel + PDF)
- [x] Ping & Port tarama
- [x] Cihaz durum geçmişi
- [x] Profil sayfası (son giriş, rol, istatistikler)