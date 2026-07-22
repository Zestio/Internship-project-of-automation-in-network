# NAPALM Tabanlı Multi-Vendor Ağ Yönetim Platformu

Dönem sonu staj projesi kapsamında geliştirilen bu platform, birden fazla Cisco ağ cihazını (router ve switch) merkezi bir web arayüzü üzerinden yönetmeyi, konfigürasyon değişikliklerini güvenli şekilde önizlemeyi, güvenlik denetimi yapmayı ve gerçek zamanlı izleme sağlamayı hedeflemektedir.

Proje, GNS3 simülasyon ortamında Cisco 3725 router ve NM-16ESW switch modülü üzerinde geliştirilmiş ve test edilmiştir.

---

## Özellikler

**Kullanıcı ve Erişim Yönetimi**
- Kayıt ve giriş sistemi, SHA-256 ile şifrelenmiş parola saklama
- Rol tabanlı yetkilendirme: Admin (tam yetki) ve Readonly (sadece görüntüleme)
- Şifre değiştirme, hesap silme, son giriş zamanı takibi
- Admin paneli üzerinden kullanıcı rol yönetimi

**Cihaz Yönetimi**
- Her kullanıcı kendi router/switch cihazlarını sisteme ekleyip yönetebilir
- Paralel bağlantı ile hızlı çok cihaz veri çekimi (ThreadPoolExecutor)
- Cihaz silme, ping atma, Telnet port tarama
- Ağ topoloji haritası (vis.js ile interaktif görselleştirme)

**Konfigürasyon Yönetimi**
- Mevcut running config görüntüleme
- Yeni config ile diff karşılaştırması (önizleme)
- Config simülasyonu: IP, interface, syntax validasyonu ile hata tespiti
- Config uygulama ve versiyonlama (backup'lar arası diff)
- Tarih damgalı backup alma, listeleme, indirme ve silme
- Toplu işlem: Birden fazla cihaza aynı anda backup alma

**Güvenlik ve Denetim**
- 10 kurallı compliance denetimi (SSH, HTTP, CEF, domain, VTY vb.)
- Toplu compliance denetimi ve yüzde skor hesaplama
- Tüm işlemlerin kullanıcıya özel audit log'a kaydedilmesi
- Audit log temizleme

**İzleme ve Bildirim**
- Arka planda 5 dakikada bir otomatik cihaz kontrolü
- Interface down veya cihaza ulaşılamaz durumunda anlık uyarı (ana sayfa)
- Gmail SMTP üzerinden otomatik e-posta alarm bildirimi
- Interface down olaylarının tarihli geçmişi

**Raporlama ve Export**
- Cihaz listesini Excel (.xlsx) olarak dışa aktarma
- Compliance raporunu PDF olarak dışa aktarma
- Compliance skorları, backup ve audit log istatistikleri (Chart.js grafikleri)

**Performans**
- Thread-safe cache sistemi: Sayfa açılışlarında anlık yanıt
- 60 saniyede bir arka planda otomatik cache yenileme

---

## Kullanılan Teknolojiler

| Teknoloji    | Amaç                                      |
|--------------|-------------------------------------------|
| Python 3     | Ana programlama dili                      |
| Flask        | Web framework (backend)                   |
| NAPALM       | Multi-vendor ağ otomasyon kütüphanesi     |
| Netmiko      | SSH/Telnet tabanlı cihaz bağlantısı       |
| SQLite       | Kullanıcı, cihaz ve audit log veritabanı  |
| Flask-Login  | Kullanıcı oturum yönetimi                 |
| Bootstrap 5  | Frontend UI framework                     |
| Chart.js     | İstatistik grafikleri                     |
| vis.js       | Ağ topoloji görselleştirme                |
| openpyxl     | Excel export                              |
| ReportLab    | PDF export                                |
| GNS3         | Ağ simülasyon ortamı (Cisco 3725)         |

---

## Proje Yapısı
staj-projesi/
├── app.py # Flask backend, tüm route'lar ve iş mantığı
├── mock_napalm.py # Config yönetimi: backup, diff, simülasyon
├── mock_device.py # Cihaz veri çekimi ve cache yönetimi
├── compliance.py # Güvenlik denetim kuralları (10 kural)
├── database.py # SQLite veritabanı işlemleri
├── templates/
│ ├── index.html # Ana sayfa — cihaz listesi ve uyarılar
│ ├── detail.html # Cihaz detay sayfası
│ ├── config.html # Config yönetimi sayfası
│ ├── config_versions.html # Config versiyonlama ve diff
│ ├── backups.html # Backup geçmişi sayfası
│ ├── compliance.html # Compliance denetim sayfası
│ ├── audit.html # Audit log sayfası
│ ├── topology.html # Ağ topoloji haritası
│ ├── stats.html # İstatistik ve grafik sayfası
│ ├── device_history.html # Cihaz durum geçmişi
│ ├── profile.html # Kullanıcı profil sayfası
│ ├── login.html # Giriş sayfası
│ ├── register.html # Kayıt sayfası
│ ├── add_device.html # Cihaz ekleme sayfası
│ ├── admin_users.html # Kullanıcı yönetimi (admin)
│ ├── email_settings.html # E-posta ayarları
│ ├── change_password.html # Şifre değiştirme
│ └── delete_account.html # Hesap silme
├── backups/ # Config yedek dosyaları
├── audit.db # SQLite veritabanı
└── requirements.txt # Python bağımlılıkları
---

## Kurulum

**1. Repoyu klonla:**
```bash
git clone https://github.com/Zestio/Internship-project-of-automation-in-network.git
cd Internship-project-of-automation-in-network
```

**2. Virtual environment oluştur ve aktif et:**
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
```

**3. Bağımlılıkları kur:**
```bash
pip install -r requirements.txt
```

**4. GNS3 ortamını hazırla:**
- GNS3 ve VirtualBox kurulu olmalı
- Cisco 3725 IOS image GNS3'e eklenmiş olmalı
- En az 1 router veya switch çalışıyor olmalı (Telnet/SSH aktif)
- Switch için: c3725 üzerine NM-16ESW modülü eklenebilir

**5. Uygulamayı başlat:**
```bash
python app.py
```

**6. Tarayıcıda aç:**
http://127.0.0.1:5000
---

## Gereksinimler
flask
napalm
netmiko
flask-login
openpyxl
reportlab
---

## Yol Haritası

- [x] Gerçek Cisco 3725 router ve NM-16ESW switch entegrasyonu (GNS3/Netmiko)
- [x] Çok kullanıcılı sistem (kayıt, giriş, rol tabanlı yetkilendirme)
- [x] Çok cihazlı envanter dashboard (router ve switch karışık topoloji)
- [x] Config backup, diff, simülasyon, uygulama ve versiyonlama
- [x] Config validasyonu (IP, interface, syntax kontrolü)
- [x] Compliance denetim modülü (10 güvenlik kuralı)
- [x] SQLite audit log sistemi (kullanıcıya özel)
- [x] Gerçek zamanlı izleme ve uyarı sistemi
- [x] E-posta bildirimi (Gmail SMTP)
- [x] Ağ topoloji haritası (vis.js)
- [x] Cache sistemi ile performans optimizasyonu
- [x] Toplu işlem (backup ve compliance)
- [x] Export özelliği (Excel ve PDF)
- [x] Ping ve port tarama
- [x] Cihaz durum geçmişi
- [x] Profil sayfası (son giriş, rol, istatistikler)
- [x] Tüm Python modülleri dokümante edildi (yorum satırları)