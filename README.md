# 🧠 EEG Zihin Durumu Takip Sistemi

Gerçek zamanlı EEG beyin dalgası analizi ve kişiselleştirilmiş öneri sistemi. Yüksek lisans tez projesi.

## 📋 Proje Özeti

Bu sistem, EEG (Elektroensefalografi) sinyallerini analiz ederek kullanıcının zihin durumunu tespit eder ve buna göre öneriler sunar.

### Temel Özellikler

- 🌊 **Gerçek Zamanlı EEG Simülasyonu**: 5 dalga bandı (Delta, Theta, Alpha, Beta, Gamma)
- 🧠 **Zihin Durumu Analizi**: Stres, Odak, Uykusuzluk tespiti
- 💡 **Akıllı Öneriler**: Frekans bazlı müzik, meditasyon, mola önerileri
- 📊 **Canlı Görselleştirme**: Chart.js ile interaktif grafikler
- 💾 **Veri Kayıt**: JSON formatında session kayıtları

## 🏗️ Mimari
```
┌─────────────────────────────────────┐
│   Web Frontend (HTML/JS/Chart.js)  │
└──────────────┬──────────────────────┘
               │ WebSocket
┌──────────────┴──────────────────────┐
│      Flask Backend (Python)         │
│  ┌────────────────────────────────┐ │
│  │  EEG Simulator                 │ │
│  │  Signal Processor              │ │
│  │  Mental State Classifier       │ │
│  │  Recommendation Engine         │ │
│  └────────────────────────────────┘ │
└─────────────────────────────────────┘
```

## 🚀 Kurulum

### 1. Proje İndir ve Kur
```bash
# Dizini oluştur
git clone <repo> # veya ZIP indir
cd eeg_mental_tracker

# Virtual environment
python -m venv venv

# Aktif et
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Bağımlılıkları kur
pip install -r requirements.txt
```

### 2. Uygulamayı Başlat
```bash
python app.py
```

### 3. Tarayıcıda Aç
```
http://localhost:5000
```

## 📁 Dizin Yapısı
```
eeg_mental_tracker/
├── modules/                  # Core modüller
│   ├── eeg_simulator.py
│   ├── signal_processor.py
│   ├── mental_state_classifier.py
│   └── recommendation_engine.py
├── templates/
│   └── index.html           # Frontend
├── data/                    # JSON kayıtları
├── app.py                   # Ana uygulama
└── requirements.txt
```

## 🔬 Modüller

### 1. EEG Simulator
- Gerçekçi EEG sinyali simüle eder
- 4 mod: Relaxed, Focused, Stressed, Sleepy
- 256 Hz örnekleme hızı

### 2. Signal Processor
- 2 saniyelik pencere analizi
- Band güç hesaplama
- İleri seviye: FFT entegrasyonu

### 3. Mental State Classifier
- Kural tabanlı sınıflandırma
- 3 metrik: Stres, Odak, Uykusuzluk
- 0-100 skala

### 4. Recommendation Engine
- Frekans bazlı müzik (Binaural Beats)
- Meditasyon egzersizleri
- Mola ve nefes önerileri

## 🎯 Kullanım

1. **Başlat**: ▶️ butonuna tıklayın
2. **Mod Seç**: 😌 😰 🎯 😴 butonlarından birini seçin
3. **İzle**: Grafiklerde gerçek zamanlı veri akışını görün
4. **Kaydet**: 💾 ile session'u JSON'a kaydedin

## 📊 Veri Formatı

Kaydedilen JSON yapısı:
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "band_powers": {
    "delta_power": 5.2,
    "theta_power": 8.1,
    "alpha_power": 15.3,
    "beta_power": 12.7,
    "gamma_power": 3.4
  },
  "mental_state": {
    "stress": 45,
    "focus": 72,
    "sleepiness": 20,
    "confidence": 0.85
  },
  "recommendations": [...]
}
```

## 🔧 Geliştirme

### Modül Test

Her modül bağımsız test edilebilir:
```bash
python modules/eeg_simulator.py
python modules/signal_processor.py
python modules/mental_state_classifier.py
python modules/recommendation_engine.py
```

### API Endpoints

- `GET /`: Ana sayfa
- `GET /api/status`: Sistem durumu
- `POST /api/session/save`: Session kaydet
- `POST /api/session/clear`: Session temizle
- `GET /api/session/stats`: Session istatistikleri

### WebSocket Events

**Client → Server:**
- `start_streaming`: Akışı başlat
- `stop_streaming`: Akışı durdur
- `change_mode`: Simülatör modunu değiştir

**Server → Client:**
- `connected`: Bağlantı başarılı
- `eeg_update`: Yeni veri paketi
- `mode_changed`: Mod değişti

## 📚 Bilimsel Temeller

### EEG Dalga Bantları

| Band | Frekans | Durum |
|------|---------|-------|
| Delta | 0.5-4 Hz | Derin uyku |
| Theta | 4-8 Hz | Meditasyon, rüya |
| Alpha | 8-13 Hz | Rahat, dingin |
| Beta | 13-30 Hz | Aktif düşünme |
| Gamma | 30-100 Hz | Yoğun konsantrasyon |

### Zihin Durumu Kuralları

- **Stres**: Yüksek Beta + Düşük Alpha + Yüksek Gamma
- **Odak**: Orta-Yüksek Beta + Gamma
- **Uykusuzluk**: Yüksek Delta + Theta + Düşük Beta

## 🎓 Öğrenme Kaynakları

1. [Beyin Dalgaları ve EEG](https://en.wikipedia.org/wiki/Electroencephalography)
2. [Binaural Beats Araştırması](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4428073/)
3. [FFT ve Sinyal İşleme](https://en.wikipedia.org/wiki/Fast_Fourier_transform)
4. [WebSocket ile Gerçek Zamanlı Veri](https://flask-socketio.readthedocs.io/)

## 🚀 Gelecek Geliştirmeler

- [ ] Machine Learning modeli entegrasyonu
- [ ] Gerçek EEG cihazı (Muse/OpenBCI) desteği
- [ ] PostgreSQL veritabanı
- [ ] Gerçek Binaural Beats ses üretimi
- [ ] Kullanıcı hesapları ve oturum yönetimi
- [ ] Mobil uygulama (React Native)

## 📄 Lisans

Bu proje eğitim amaçlıdır.

## 👥 Katkıda Bulunanlar

- Yüksek Lisans Öğrencisi: Ezgi Nur İşbilen
- Danışman: Fatih Şahinbaş

## 📧 İletişim

Sorular için: [email]