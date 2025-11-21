"""
Mental State Classifier Module
EEG güç değerlerinden zihin durumu tespit eder.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class MentalState:
    """
    Zihin durumu sonuçları.
    Her değer 0-100 arası skala.
    """
    stress_level: int      # 0=Rahat, 100=Çok stresli
    focus_level: int       # 0=Dağınık, 100=Çok odaklı
    sleepiness_level: int  # 0=Uyanık, 100=Çok uykulu
    confidence: float      # 0-1 arası, tahmin güvenilirliği


class MentalStateClassifier:
    """
    Kural tabanlı zihin durumu sınıflandırıcı.
    
    Araştırmalara dayalı kurallar:
    - Stres: Düşük Alpha + Yüksek Beta
    - Odak: Orta-Yüksek Beta + Gamma
    - Uykusuzluk: Yüksek Delta + Theta
    
    İleride Machine Learning modeli ile değiştirilebilir.
    """
    
    def __init__(self):
        # Eşik değerleri (threshold)
        self.stress_beta_threshold = 15.0
        self.stress_alpha_threshold = 8.0
        self.focus_beta_min = 12.0
        self.sleepy_delta_threshold = 10.0
        
    def classify(self, band_powers: Dict[str, float]) -> MentalState:
        """
        Band güçlerinden zihin durumu çıkar.
        
        Args:
            band_powers: Signal processor'dan gelen güç değerleri
            
        Returns:
            MentalState: Stres, odak, uykusuzluk seviyeleri
        """
        delta = band_powers['delta_power']
        theta = band_powers['theta_power']
        alpha = band_powers['alpha_power']
        beta = band_powers['beta_power']
        gamma = band_powers['gamma_power']
        
        # Toplam güç
        total_power = delta + theta + alpha + beta + gamma
        
        if total_power < 1.0:
            # Çok düşük sinyal
            return MentalState(
                stress_level=0,
                focus_level=0,
                sleepiness_level=0,
                confidence=0.0
            )
        
        # Her bandın yüzdesi
        delta_pct = (delta / total_power) * 100
        theta_pct = (theta / total_power) * 100
        alpha_pct = (alpha / total_power) * 100
        beta_pct = (beta / total_power) * 100
        gamma_pct = (gamma / total_power) * 100
        
        # === STRES HESAPLAMA ===
        # Yüksek beta + düşük alpha = stres
        stress = self._calculate_stress(beta_pct, alpha_pct, gamma_pct)
        
        # === ODAK HESAPLAMA ===
        # Orta-yüksek beta + gamma
        focus = self._calculate_focus(beta_pct, gamma_pct, alpha_pct)
        
        # === UYKUSUZLUK HESAPLAMA ===
        # Yüksek delta + theta
        sleepiness = self._calculate_sleepiness(delta_pct, theta_pct, beta_pct)
        
        # Güven skoru
        confidence = self._calculate_confidence(total_power)
        
        return MentalState(
            stress_level=stress,
            focus_level=focus,
            sleepiness_level=sleepiness,
            confidence=confidence
        )
    
    def _calculate_stress(self, beta_pct: float, alpha_pct: float, 
                         gamma_pct: float) -> int:
        """
        Stres seviyesi hesapla.
        
        Formül: Yüksek Beta - Düşük Alpha + Yüksek Gamma
        """
        # Beta çok yüksekse stres artar
        stress_from_beta = min(100, beta_pct * 3)
        
        # Alpha düşükse stres artar
        stress_from_alpha = max(0, 50 - alpha_pct * 2)
        
        # Gamma çok yüksekse stres işareti
        stress_from_gamma = min(30, gamma_pct * 2)
        
        total_stress = (stress_from_beta + stress_from_alpha + stress_from_gamma) / 2.5
        
        return int(min(100, max(0, total_stress)))
    
    def _calculate_focus(self, beta_pct: float, gamma_pct: float,
                        alpha_pct: float) -> int:
        """
        Odak seviyesi hesapla.
        
        Formül: Orta Beta + Gamma + Biraz Alpha
        """
        # Beta 20-35% arasında optimum odak
        if 20 <= beta_pct <= 35:
            focus_from_beta = 60
        elif beta_pct > 35:
            focus_from_beta = min(100, beta_pct * 2)
        else:
            focus_from_beta = beta_pct * 2
        
        # Gamma katkısı
        focus_from_gamma = min(40, gamma_pct * 3)
        
        # Çok fazla alpha odağı bozabilir
        alpha_penalty = max(0, (alpha_pct - 30) * 0.5)
        
        total_focus = focus_from_beta + focus_from_gamma - alpha_penalty
        
        return int(min(100, max(0, total_focus)))
    
    def _calculate_sleepiness(self, delta_pct: float, theta_pct: float,
                             beta_pct: float) -> int:
        """
        Uykusuzluk seviyesi hesapla.
        
        Formül: Yüksek Delta + Theta - Beta
        """
        # Delta ve Theta yüksekse uykusuzluk
        sleepy_from_slow = (delta_pct * 2 + theta_pct * 1.5) / 2
        
        # Beta düşükse uykusuzluk artar
        beta_penalty = max(0, 30 - beta_pct)
        
        total_sleepiness = sleepy_from_slow + beta_penalty
        
        return int(min(100, max(0, total_sleepiness)))
    
    def _calculate_confidence(self, total_power: float) -> float:
        """
        Tahmin güvenilirliği hesapla.
        
        Yüksek toplam güç = yüksek güven
        """
        if total_power > 30:
            return 0.9
        elif total_power > 20:
            return 0.7
        elif total_power > 10:
            return 0.5
        else:
            return 0.3


# Test kodu
if __name__ == "__main__":
    from modules.eeg_simulator import EEGSimulator, MentalStateMode
    from modules.signal_processor import SignalProcessor
    
    print("🧠 Mental State Classifier Test\n")
    print("=" * 60)
    
    simulator = EEGSimulator()
    processor = SignalProcessor()
    classifier = MentalStateClassifier()
    
    for mode in MentalStateMode:
        print(f"\n📊 {mode.value.upper()} Durumu:")
        print("-" * 60)
        
        # 2 saniye veri üret
        samples = list(simulator.stream_samples(mode, duration_seconds=2.0))
        
        # İşle
        band_powers = processor.analyze_eeg_window(samples)
        mental_state = classifier.classify(band_powers)
        
        # Sonuçları göster
        print(f"  Stres:       {mental_state.stress_level:3d}/100  {'🔴' if mental_state.stress_level > 60 else '🟢'}")
        print(f"  Odak:        {mental_state.focus_level:3d}/100  {'🟢' if mental_state.focus_level > 60 else '🔴'}")
        print(f"  Uykusuzluk:  {mental_state.sleepiness_level:3d}/100  {'🔴' if mental_state.sleepiness_level > 60 else '🟢'}")
        print(f"  Güven:       {mental_state.confidence:.2f}")