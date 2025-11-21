"""
Signal Processor Module
EEG sinyallerini işler ve frekans analizi yapar.
"""

import numpy as np
from typing import List, Dict
from modules.eeg_simulator import EEGSample


class SignalProcessor:
    """
    EEG sinyallerini analiz eder.
    
    Temel görevler:
    1. Pencere içindeki örnekleri toplar
    2. Her dalga bandının ortalama gücünü hesaplar
    3. Temiz veri çıktısı sağlar
    
    İleri seviye: FFT (Fast Fourier Transform) ile frekans analizi yapılabilir.
    """
    
    def __init__(self, sampling_rate: int = 256, window_size_seconds: float = 2.0):
        """
        Args:
            sampling_rate: Örnekleme frekansı (Hz)
            window_size_seconds: Analiz penceresi süresi (saniye)
        """
        self.sampling_rate = sampling_rate
        self.window_size = int(sampling_rate * window_size_seconds)
        
    def analyze_eeg_window(self, samples: List[EEGSample]) -> Dict[str, float]:
        """
        Bir pencere dolusu EEG verisini analiz et.
        
        Args:
            samples: EEGSample listesi
            
        Returns:
            Her dalga bandının güç değeri ve zaman damgası
            
        Not:
            Bu basitleştirilmiş versiyonda sadece ortalama alıyoruz.
            İleri seviyede FFT ile gerçek frekans analizi yapılabilir.
        """
        if not samples:
            return self._empty_result()
        
        # Her kanal için veriyi ayır
        delta_samples = [s.delta for s in samples]
        theta_samples = [s.theta for s in samples]
        alpha_samples = [s.alpha for s in samples]
        beta_samples = [s.beta for s in samples]
        gamma_samples = [s.gamma for s in samples]
        
        # Basit ortalama güç hesabı
        return {
            'delta_power': float(np.mean(delta_samples)),
            'theta_power': float(np.mean(theta_samples)),
            'alpha_power': float(np.mean(alpha_samples)),
            'beta_power': float(np.mean(beta_samples)),
            'gamma_power': float(np.mean(gamma_samples)),
            'timestamp': samples[-1].timestamp
        }
    
    def _empty_result(self) -> Dict[str, float]:
        """Boş sonuç döndür."""
        return {
            'delta_power': 0.0,
            'theta_power': 0.0,
            'alpha_power': 0.0,
            'beta_power': 0.0,
            'gamma_power': 0.0,
            'timestamp': 0.0
        }
    
    def calculate_ratios(self, band_powers: Dict[str, float]) -> Dict[str, float]:
        """
        Dalga güçlerinden oranlar hesapla.
        Bu oranlar zihin durumu tespitinde kullanılır.
        
        Örnek:
            - Beta/Alpha oranı yüksekse → Stres
            - Theta/Beta oranı yüksekse → Uykusuzluk
        """
        total_power = sum([
            band_powers['delta_power'],
            band_powers['theta_power'],
            band_powers['alpha_power'],
            band_powers['beta_power'],
            band_powers['gamma_power']
        ])
        
        if total_power == 0:
            return {'beta_alpha_ratio': 0, 'theta_beta_ratio': 0}
        
        # Güvenli bölme
        alpha = max(band_powers['alpha_power'], 0.1)
        beta = max(band_powers['beta_power'], 0.1)
        
        return {
            'beta_alpha_ratio': beta / alpha,
            'theta_beta_ratio': band_powers['theta_power'] / beta,
            'total_power': total_power
        }


# Test kodu
if __name__ == "__main__":
    from modules.eeg_simulator import EEGSimulator, MentalStateMode
    
    print("🔬 Signal Processor Test\n")
    print("=" * 50)
    
    simulator = EEGSimulator()
    processor = SignalProcessor()
    
    # 2 saniyelik veri üret
    samples = list(simulator.stream_samples(MentalStateMode.STRESSED, duration_seconds=2.0))
    
    # Analiz yap
    result = processor.analyze_eeg_window(samples)
    
    print("\n📊 Band Powers:")
    for band, power in result.items():
        if band != 'timestamp':
            print(f"  {band:15s}: {power:6.2f} µV")
    
    # Oranları hesapla
    ratios = processor.calculate_ratios(result)
    print(f"\n📈 Ratios:")
    print(f"  Beta/Alpha: {ratios['beta_alpha_ratio']:.2f} (>2 = Stres işareti)")
    print(f"  Theta/Beta: {ratios['theta_beta_ratio']:.2f} (>1 = Uykusuzluk)")