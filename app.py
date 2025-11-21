"""
Flask Backend Application
Gerçek zamanlı EEG veri akışı ve web arayüzü
"""

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import json
import threading
import time
from datetime import datetime
import os

# Kendi modüllerimizi import et
from modules.eeg_simulator import EEGSimulator, MentalStateMode
from modules.signal_processor import SignalProcessor
from modules.mental_state_classifier import MentalStateClassifier
from modules.recommendation_engine import RecommendationEngine

# Flask uygulaması oluştur
app = Flask(__name__)
app.config['SECRET_KEY'] = 'eeg-mental-tracker-secret-2024'
CORS(app)  # Cross-Origin isteklerine izin ver
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global nesneler (tüm modüller)
simulator = EEGSimulator(sampling_rate=256)
processor = SignalProcessor(sampling_rate=256, window_size_seconds=2.0)
classifier = MentalStateClassifier()
engine = RecommendationEngine()

# Global durum değişkenleri
eeg_buffer = []  # Ham EEG örnekleri burda toplanır
session_data = []  # Analiz sonuçları burda saklanır
current_mode = MentalStateMode.RELAXED  # Başlangıç modu
is_streaming = False  # Akış aktif mi?


def background_eeg_stream():
    """
    Arka planda sürekli çalışan EEG veri akışı.
    
    Bu fonksiyon ayrı bir thread'de çalışır ve:
    1. Her 250ms'de simülatörden veri alır
    2. Buffer dolduğunda analiz yapar
    3. Sonuçları WebSocket ile frontend'e gönderir
    """
    global eeg_buffer, session_data, current_mode, is_streaming
    
    print("🚀 EEG akışı başlatıldı...")
    
    while True:
        if not is_streaming:
            time.sleep(0.5)
            continue
        
        try:
            # 0.25 saniyelik veri üret (256 Hz * 0.25 = 64 örnek)
            samples = list(simulator.stream_samples(current_mode, duration_seconds=0.25))
            eeg_buffer.extend(samples)
            
            # 2 saniyelik pencere doldu mu kontrol et (256 Hz * 2 = 512 örnek)
            if len(eeg_buffer) >= 512:
                # === ANALİZ AŞAMASI ===
                
                # 1. Son 512 örneği al (2 saniye)
                window_samples = eeg_buffer[-512:]
                
                # 2. Sinyal işleme: Band güçlerini hesapla
                band_powers = processor.analyze_eeg_window(window_samples)
                
                # 3. Zihin durumu sınıflandır
                mental_state = classifier.classify(band_powers)
                
                # 4. Öneriler üret
                recommendations = engine.generate(mental_state)
                
                # === VERİ HAZIRLAMA ===
                data_packet = {
                    'timestamp': datetime.now().isoformat(),
                    'band_powers': band_powers,
                    'mental_state': {
                        'stress': mental_state.stress_level,
                        'focus': mental_state.focus_level,
                        'sleepiness': mental_state.sleepiness_level,
                        'confidence': mental_state.confidence
                    },
                    'recommendations': [
                        {
                            'type': rec.type.value,
                            'frequency_hz': rec.frequency_hz,
                            'duration_minutes': rec.duration_minutes,
                            'title': rec.title,
                            'description': rec.description,
                            'priority': rec.priority
                        } for rec in recommendations
                    ],
                    'current_mode': current_mode.value  # Debug için
                }
                
                # === WEBSOCKET İLE GÖNDER ===
                socketio.emit('eeg_update', data_packet)
                
                # Session'a kaydet
                session_data.append(data_packet)
                
                # Buffer'ı temizle (overlap için 256 örnek bırak)
                # Bu sayede pencereler kesintisiz devam eder
                eeg_buffer = eeg_buffer[-256:]
            
            # 250ms bekle (4 Hz güncelleme hızı)
            time.sleep(0.25)
            
        except Exception as e:
            print(f"❌ Akış hatası: {e}")
            time.sleep(1)


# === FLASK ROUTE'LAR (HTTP Endpointler) ===

@app.route('/')
def index():
    """Ana sayfa"""
    return render_template('index.html')


@app.route('/api/status')
def api_status():
    """Sistem durumu"""
    return jsonify({
        'status': 'online',
        'streaming': is_streaming,
        'current_mode': current_mode.value,
        'buffer_size': len(eeg_buffer),
        'session_data_count': len(session_data)
    })


@app.route('/api/session/save', methods=['POST'])
def save_session():
    """
    Aktif session verisini JSON dosyasına kaydet.
    
    Dosya formatı: data/session_YYYYMMDD_HHMMSS.json
    """
    try:
        # data klasörünü kontrol et
        os.makedirs('data', exist_ok=True)
        
        # Dosya adı oluştur
        filename = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join('data', filename)
        
        # JSON'a yaz
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'status': 'success',
            'filename': filename,
            'data_points': len(session_data)
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/session/clear', methods=['POST'])
def clear_session():
    """Session verisini temizle"""
    global session_data
    session_data = []
    return jsonify({'status': 'success', 'message': 'Session temizlendi'})


@app.route('/api/session/stats')
def session_stats():
    """Session istatistikleri"""
    if not session_data:
        return jsonify({'status': 'empty'})
    
    # Ortalama değerleri hesapla
    avg_stress = sum(d['mental_state']['stress'] for d in session_data) / len(session_data)
    avg_focus = sum(d['mental_state']['focus'] for d in session_data) / len(session_data)
    avg_sleepiness = sum(d['mental_state']['sleepiness'] for d in session_data) / len(session_data)
    
    return jsonify({
        'total_data_points': len(session_data),
        'duration_seconds': len(session_data) * 2,  # Her nokta 2 saniye
        'averages': {
            'stress': round(avg_stress, 1),
            'focus': round(avg_focus, 1),
            'sleepiness': round(avg_sleepiness, 1)
        }
    })


# === WEBSOCKET OLAYLARI (SocketIO Events) ===

@socketio.on('connect')
def handle_connect():
    """İstemci bağlandığında"""
    print('✅ Client bağlandı')
    emit('connected', {
        'status': 'ready',
        'message': 'EEG Tracker hazır',
        'current_mode': current_mode.value
    })


@socketio.on('disconnect')
def handle_disconnect():
    """İstemci bağlantıyı kestiğinde"""
    print('❌ Client bağlantıyı kesti')


@socketio.on('start_streaming')
def handle_start_streaming():
    """Akışı başlat"""
    global is_streaming
    is_streaming = True
    print('▶️  Akış başlatıldı')
    emit('streaming_started', {'status': 'streaming'})


@socketio.on('stop_streaming')
def handle_stop_streaming():
    """Akışı durdur"""
    global is_streaming
    is_streaming = False
    print('⏸️  Akış durduruldu')
    emit('streaming_stopped', {'status': 'stopped'})


@socketio.on('change_mode')
def handle_mode_change(data):
    """
    Simülatör modunu değiştir.
    
    Frontend'den gelen komut:
    { "mode": "stressed" }
    """
    global current_mode
    
    mode_str = data.get('mode', 'relaxed')
    
    # String'i enum'a çevir
    mode_map = {
        'relaxed': MentalStateMode.RELAXED,
        'focused': MentalStateMode.FOCUSED,
        'stressed': MentalStateMode.STRESSED,
        'sleepy': MentalStateMode.SLEEPY
    }
    
    if mode_str in mode_map:
        current_mode = mode_map[mode_str]
        print(f'🔄 Mode değiştirildi: {current_mode.value}')
        
        emit('mode_changed', {
            'mode': current_mode.value,
            'message': f'Mod {current_mode.value} olarak değiştirildi'
        }, broadcast=True)
    else:
        emit('error', {'message': 'Geçersiz mod'})


# === UYGULAMA BAŞLATMA ===

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🧠 EEG Mental State Tracker")
    print("="*60)
    print("📡 Server: http://localhost:5000")
    print("📊 Örnekleme hızı: 256 Hz")
    print("⏱️  Pencere boyutu: 2 saniye")
    print("🔄 Güncelleme hızı: 4 Hz (0.25s)")
    print("="*60 + "\n")
    
    # Arka plan thread'i başlat
    stream_thread = threading.Thread(target=background_eeg_stream, daemon=True)
    stream_thread.start()
    
    # Flask sunucusunu başlat
    socketio.run(
        app,
        debug=True,
        host='0.0.0.0',
        port=5000,
        allow_unsafe_werkzeug=True  # Geliştirme için
    )