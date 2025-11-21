"""
EEG Simulator Module
Gerçekçi EEG sinyalleri simüle eder.
"""

import numpy as np
from dataclasses import dataclass
from enum import Enum
from typing import Generator


class MentalStateMode(Enum):
    """
    Simüle edilebilecek zihin durumu modları.
    Her mod farklı EEG dalga profiline sahiptir.
    """
    RELAXED = "relaxed"      # Yüksek Alpha (dingin)
    FOCUSED = "focused"      # Yüksek Beta (konsantre)
    STRESSED = "stressed"    # Düşük Alpha, çok yüksek Beta (stresli)
    SLEEPY = "sleepy"        # Yüksek Theta/Delta (uykulu)


@dataclass
class EEGSample:
    """
    Tek bir zaman noktasındaki EEG ölçümü.
    Her dalga bandının güç değerini içerir (µV - mikrovolt).
    """
    timestamp: float  # Saniye cinsinden zaman
    delta: float      # 0.5-4 Hz (derin uyku)
    theta: float      # 4-8 Hz (meditasyon, rüya)
    alpha: float      # 8-13 Hz (rahat, dingin)
    beta: float       # 13-30 Hz (aktif düşünme)
    gamma: float      # 30-100 Hz (yoğun konsantrasyon)


class EEGSimulator:
    """
    Gerçekçi EEG verisi üreten simülatör.
    
    Kullanım:
        simulator = EEGSimulator(sampling_rate=256)
        sample = simulator.generate_sample(MentalStateMode.RELAXED)
    """
    
    def __init__(self, sampling_rate: int = 256):
        """
        Args:
            sampling_rate: Saniyedeki örnek sayısı (Hz). 
                          Genelde 256 Hz kullanılır.
        """
        self.sampling_rate = sampling_rate
        self.time = 0.0
        self.current_mode = MentalStateMode.RELAXED
        
    def generate_sample(self, mode: MentalStateMode) -> EEGSample:
        """
        Belirli bir zihin durumu için tek bir EEG örneği üret.
        
        Args:
            mode: Simüle edilecek zihin durumu
            
        Returns:
            EEGSample: Tüm dalga bantlarının güç değerleri
            
        Not:
            Her dalga bandı için temel değer + rastgele gürültü eklenir.
            Bu gerçek EEG'nin doğal varyasyonunu simüle eder.
        """
        # Gerçekçi gürültü ekle (Gaussian noise)
        noise = np.random.randn() * 0.5
        
        if mode == MentalStateMode.RELAXED:
            # Rahat durum: Alpha dominant
            delta = 5 + noise
            theta = 8 + noise
            alpha = 15 + noise  # EN YÜKSEK
            beta = 5 + noise
            gamma = 2 + noise
            
        elif mode == MentalStateMode.FOCUSED:
            # Odaklı durum: Beta ve Gamma yüksek
            delta = 3 + noise
            theta = 5 + noise
            alpha = 7 + noise
            beta = 18 + noise   # EN YÜKSEK
            gamma = 8 + noise
            
        elif mode == MentalStateMode.STRESSED:
            # Stresli durum: Alpha düşük, Beta çok yüksek
            delta = 4 + noise
            theta = 6 + noise
            alpha = 4 + noise   # DÜŞÜK!
            beta = 20 + noise   # ÇOK YÜKSEK
            gamma = 12 + noise
            
        elif mode == MentalStateMode.SLEEPY:
            # Uykulu durum: Delta ve Theta dominant
            delta = 12 + noise  # EN YÜKSEK
            theta = 10 + noise  # YÜKSEK
            alpha = 6 + noise
            beta = 3 + noise
            gamma = 1 + noise
            
        else:
            # Default: orta değerler
            delta = theta = alpha = beta = gamma = 5 + noise
        
        # Negatif değerleri engelle (güç negatif olamaz)
        return EEGSample(
            timestamp=self.time,
            delta=max(0.1, delta),
            theta=max(0.1, theta),
            alpha=max(0.1, alpha),
            beta=max(0.1, beta),
            gamma=max(0.1, gamma)
        )
    
    def stream_samples(self, mode: MentalStateMode, 
                      duration_seconds: float = 1.0) -> Generator[EEGSample, None, None]:
        """
        Belirli bir süre boyunca EEG verisi akışı simüle et.
        
        Args:
            mode: Simüle edilecek zihin durumu
            duration_seconds: Akış süresi (saniye)
            
        Yields:
            EEGSample: Her örnekte bir tane
            
        Kullanım:
            for sample in simulator.stream_samples(MentalStateMode.FOCUSED, 2.0):
                print(sample)
        """
        samples_count = int(self.sampling_rate * duration_seconds)
        
        for _ in range(samples_count):
            yield self.generate_sample(mode)
            self.time += 1.0 / self.sampling_rate
    
    def set_mode(self, mode: MentalStateMode):
        """Simülatörün aktif modunu değiştir."""
        self.current_mode = mode
    
    def reset_time(self):
        """Zaman sayacını sıfırla."""
        self.time = 0.0


# Test kodu (bu dosya direkt çalıştırılırsa)
if __name__ == "__main__":
    print("🧠 EEG Simülatör Test\n")
    print("=" * 50)
    
    simulator = EEGSimulator()
    
    for mode in MentalStateMode:
        print(f"\n📊 {mode.value.upper()} Durumu:")
        print("-" * 50)
        
        # 5 örnek al
        for i, sample in enumerate(simulator.stream_samples(mode, duration_seconds=0.01)):
            if i == 0:  # Sadece ilk örneği göster
                print(f"  Delta:  {sample.delta:6.2f} µV")
                print(f"  Theta:  {sample.theta:6.2f} µV")
                print(f"  Alpha:  {sample.alpha:6.2f} µV  {'← DOMINANT' if sample.alpha > 10 else ''}")
                print(f"  Beta:   {sample.beta:6.2f} µV  {'← DOMINANT' if sample.beta > 15 else ''}")
                print(f"  Gamma:  {sample.gamma:6.2f} µV")