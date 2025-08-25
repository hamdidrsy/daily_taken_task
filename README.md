# TaskTycoon – Şirket Simülasyon Oyunu

Flask tabanlı interaktif şirket simülasyon oyunu. Görevler yaparak şirketinizi büyütün, departmanlar kurun ve çalışanlar işe alın.

## 🚀 Hızlı Başlangıç

### Kurulum
```bash
# 1. Sanal ortam oluşturun ve aktif edin
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 2. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 3. Uygulamayı başlatın
python -m tasktycoon
```

### Erişim
- **Web Dashboard:** http://127.0.0.1:5000
- **API Base URL:** http://127.0.0.1:5000/api

---

## 📋 Hafta 1 - Tamamlanan Özellikler ✅

### 🏗️ Backend Sistemi (Day 1-6)
#### ✅ Modular Flask Mimarisi
- **Blueprint yapısı** ile organize edilmiş route'lar
- **Service katmanı** ile iş mantığı ayrımı  
- **Factory pattern** ile uygulama oluşturma

#### ✅ Oyun Mekaniği
- **Enerji sistemi** (0-100 arası)
- **Görev sistemi** (kodlama, pazarlama, satış, araştırma)
- **Gün/gece döngüsü**
- **XP ve seviye sistemi**

#### ✅ Departman Yönetimi
- Engineering, R&D, HR, Sales departmanları
- Departman seviyeleri ve yükseltme sistemi
- Departman bazlı çalışan yönetimi

#### ✅ Çalışan Sistemi
- Çalışan işe alma/işten çıkarma
- Maaş sistemi
- Departman atamaları

#### ✅ State Yönetimi
- **JSON tabanlı** kalıcı veri saklama (`data/state.json`)
- Otomatik kaydetme/yükleme
- State sıfırlama

### 🎨 Frontend Sistemi (Day 7)
#### ✅ Web Dashboard
- **Bootstrap 5** ile responsive tasarım
- **Jinja2 templates** ile dinamik içerik
- Modern ve kullanıcı dostu arayüz

#### ✅ JavaScript API Entegrasyonu  
- **Fetch API** ile backend iletişimi
- Real-time dashboard güncellemeleri
- Otomatik yenileme (30 saniye)
- Otomatik kaydetme (5 dakika)

---

## 🔧 API Endpointleri

### 📊 State Management
- `GET /api/state` - Oyun durumu
- `POST /api/state/save` - Oyunu kaydet
- `POST /api/state/load` - Oyunu yükle  
- `POST /api/state/reset` - Oyunu sıfırla

### 🎯 Görev Sistemi
- `POST /api/task` - Görev gerçekleştir
- `POST /api/day/end` - Günü bitir
- `POST /api/energy/restore` - Enerji yenile

### 🏢 Departman Yönetimi
- `POST /api/department/{type}/upgrade` - Departman yükselt

### 👥 Çalışan Yönetimi  
- `POST /api/employees/hire` - Çalışan işe al
- `POST /api/employees/{id}/fire` - Çalışan işten çıkar
- `GET /api/employees` - Çalışan listesi

---

## 📁 Proje Yapısı

```
TaskTycoon/
├── tasktycoon/                 # Ana uygulama paketi
│   ├── __init__.py            # Flask factory
│   ├── __main__.py            # Entry point
│   ├── config.py              # Konfigürasyon
│   ├── routes/                # Blueprint'ler
│   │   ├── home.py           # Ana sayfa
│   │   ├── state.py          # State API'leri
│   │   ├── task.py           # Görev API'leri
│   │   ├── department.py     # Departman API'leri
│   │   ├── employees.py      # Çalışan API'leri
│   │   ├── day.py            # Gün yönetimi
│   │   └── manage.py         # Yönetim API'leri
│   ├── services/              # İş mantığı
│   │   ├── state_service.py  # State yönetimi
│   │   └── employee_service.py # Çalışan yönetimi
│   ├── templates/             # Jinja2 şablonları
│   │   └── dashboard.html    # Ana dashboard
│   └── static/               # Statik dosyalar
│       ├── css/style.css     # Özel stiller
│       └── js/app.js         # Frontend JS
├── data/
│   └── state.json            # Oyun verisi
├── requirements.txt          # Python bağımlılıkları
└── README.md                # Bu dosya
```

---

## ⚠️ Şu An Aktif Olmayan Özellikler

### 🚧 Week 2'de Gelecek (Day 8-14)
- [ ] **Ekonomik Balans**: Gelir/gider dengeleme
- [ ] **Gelişmiş Görevler**: Kompleks görev zincirleri
- [ ] **Pazar Sistemi**: Ürün geliştirme ve satış
- [ ] **Rekabet Sistemi**: Diğer şirketlerle yarışma
- [ ] **Random Events**: Pazar değişimleri, krizler
- [ ] **Achievement System**: Başarım rozerleri
- [ ] **İstatistikler**: Detaylı performans takibi

### 🔧 Teknik İyileştirmeler (Gelecek)
- [ ] **Database Integration**: SQLite/PostgreSQL geçişi
- [ ] **User Authentication**: Kullanıcı sistemi
- [ ] **Real-time Updates**: WebSocket entegrasyonu
- [ ] **Mobile Responsive**: Mobil optimizasyonu
- [ ] **API Documentation**: Swagger/OpenAPI
- [ ] **Unit Tests**: Test coverage
- [ ] **Docker**: Containerization

---

## 🎮 Nasıl Oynanır?

1. **Oyunu Başlatın**: `python -m tasktycoon`
2. **Dashboard'a Gidin**: http://127.0.0.1:5000
3. **Görevleri Gerçekleştirin**: 
   - Kodlama (+10 XP, +100 TL, -10 Enerji)
   - Pazarlama (+5 XP, +50 TL, -5 Enerji)  
   - Satış (+15 XP, +200 TL, -15 Enerji)
   - Araştırma (+20 XP, +5 Research, -20 Enerji)
4. **Departman Kurun**: Yeterli para biriktirince
5. **Çalışan İşe Alın**: Departmanları büyütün
6. **Günü Bitirin**: Maaşlar ödenecek, yeni gün başlayacak

---

## 🔑 Klavye Kısayolları

- `Ctrl + S`: Oyunu kaydet
- `Ctrl + L`: Oyunu yükle  
- `Ctrl + E`: Günü bitir

---

## 🐛 Bilinen Sorunlar

- [ ] JavaScript dosyası bazen boş kalabiliyor (manuel yenileme gerekebilir)
- [ ] Energy restore endpoint'i eksik olabilir
- [ ] Department upgrade maliyetleri henüz balance edilmedi

---

## 📝 Gelişim Notları

### Day 1-3: Temel API'ler
- Flask setup, state management, basic endpoints

### Day 4-5: Departman & Çalışan Sistemi  
- Department operations, employee management

### Day 6: Modular Refactoring
- Blueprint migration, service layer separation

### Day 7: UI Implementation
- Dashboard, JavaScript integration, user experience

---

## 📞 İletişim

Bu proje 14 günlük bir sprint ile geliştirilmektedir. Her gün yeni özellikler eklenmekte ve GitHub'a commit edilmektedir.

**Geliştirici**: [GitHub](https://github.com/hamdidrsy)  
**Proje Repository**: [daily_taken_task](https://github.com/hamdidrsy/daily_taken_task)

---

## 📄 Lisans

MIT License - Detaylar için LICENSE dosyasına bakınız.
