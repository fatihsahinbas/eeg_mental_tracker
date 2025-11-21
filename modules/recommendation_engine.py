"""
Recommendation Engine Module
Zihin durumuna göre kişiselleştirilmiş öneriler üretir.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List
from modules.mental_state_classifier import MentalState


class RecommendationType(Enum):
    """Öneri türleri"""
    BINAURAL_BEATS = "binaural_beats"  # Frekans bazlı müzik
    MEDITATION = "meditation"           # Meditasyon egzersizi
    BREAK = "break"                     # Mola önerisi
    BREATHING = "breathing"             # Nefes egzersizi


@dataclass
class Recommendation:
    """
    Tek bir öneri.
    """
    type: RecommendationType
    frequency_hz: float = None  # Müzik için hedef frekans
    duration_minutes: int = 5   # Önerilen süre
    title: str = ""
    description: str = ""
    priority: int = 1           # 1=yüksek, 3=düşük


class RecommendationEngine:
    """
    Zihin durumuna göre akıllı öneriler üretir.
    
    Frekans Terapisi (Binaural Beats):
    - İki kulağa hafif farklı frekanslar gönderilir
    - Beyin farkı algılar ve o frekansta uyarılır
    - Örnek: Sol 200Hz + Sağ 210Hz = 10Hz Alpha dalgası
    
    Bilimsel Temeller:
    - Alpha (8-13 Hz): Rahatlatıcı, stres azaltıcı
    - Beta (13-30 Hz): Konsantrasyon artırıcı
    - Theta (4-8 Hz): Meditasyon derinleştirici
    - Delta (0.5-4 Hz): Uyku kalitesi artırıcı
    """
    
    def __init__(self):
        # Eşik değerleri
        self.high_stress_threshold = 60
        self.low_focus_threshold = 40
        self.high_sleepiness_threshold = 70
        
    def generate(self, mental_state: MentalState) -> List[Recommendation]:
        """
        Zihin durumuna göre öneri listesi oluştur.
        
        Args:
            mental_state: Mevcut zihin durumu
            
        Returns:
            List[Recommendation]: Öncelik sırasına göre öneriler
        """
        recommendations = []
        
        # STRES YÜKSEK
        if mental_state.stress_level > self.high_stress_threshold:
            recommendations.extend(self._stress_recommendations())
        
        # ODAK DÜŞÜK
        if mental_state.focus_level < self.low_focus_threshold:
            recommendations.extend(self._focus_recommendations())
        
        # UYKUSUZLUK YÜKSEK
        if mental_state.sleepiness_level > self.high_sleepiness_threshold:
            recommendations.extend(self._sleepiness_recommendations())
        
        # ORTA SEVİYE (her şey normal)
        if (self.low_focus_threshold <= mental_state.focus_level <= 70 and
            mental_state.stress_level < self.high_stress_threshold and
            mental_state.sleepiness_level < self.high_sleepiness_threshold):
            recommendations.extend(self._maintenance_recommendations())
        
        # Önceliğe göre sırala
        recommendations.sort(key=lambda x: x.priority)
        
        return recommendations
    
    def _stress_recommendations(self) -> List[Recommendation]:
        """Stres için öneriler."""
        return [
            Recommendation(
                type=RecommendationType.BINAURAL_BEATS,
                frequency_hz=10.0,  # Alpha band ortası
                duration_minutes=10,
                title="🎵 Alpha Dalgası - Stres Azaltıcı",
                description="10 Hz Alpha dalgası ile derin rahatlamayı destekler. "
                           "Kulaklıkla dinlemeniz önerilir.",
                priority=1
            ),
            Recommendation(
                type=RecommendationType.BREATHING,
                duration_minutes=5,
                title="🫁 4-7-8 Nefes Tekniği",
                description="4 saniye burnunuzdan nefes alın, 7 saniye tutun, "
                           "8 saniye ağzınızdan verin. 4 kez tekrarlayın.",
                priority=1
            ),
            Recommendation(
                type=RecommendationType.MEDITATION,
                duration_minutes=10,
                title="🧘 Beden Tarama Meditasyonu",
                description="Vücudunuzdaki her bölgeyi sırayla tarayın ve gevşetin.",
                priority=2
            )
        ]
    
    def _focus_recommendations(self) -> List[Recommendation]:
        """Odak için öneriler."""
        return [
            Recommendation(
                type=RecommendationType.BINAURAL_BEATS,
                frequency_hz=20.0,  # Beta band
                duration_minutes=15,
                title="🎵 Beta Dalgası - Konsantrasyon Artırıcı",
                description="20 Hz Beta dalgası ile odaklanmayı destekler. "
                           "Çalışma sırasında arka planda çalabilir.",
                priority=1
            ),
            Recommendation(
                type=RecommendationType.BREAK,
                duration_minutes=5,
                title="☕ Kısa Mola",
                description="5 dakika ayağa kalkın, gerinin, su için. "
                           "Pomodoro tekniği: 25 dk çalış, 5 dk mola.",
                priority=2
            )
        ]
    
    def _sleepiness_recommendations(self) -> List[Recommendation]:
        """Uykusuzluk için öneriler."""
        return [
            Recommendation(
                type=RecommendationType.BREAK,
                duration_minutes=10,
                title="🚶 Enerji Molası",
                description="Kısa yürüyüş veya hafif germe hareketleri. "
                           "Dışarı çıkıp güneş ışığı almanız faydalı olacaktır.",
                priority=1
            ),
            Recommendation(
                type=RecommendationType.BINAURAL_BEATS,
                frequency_hz=15.0,  # Düşük Beta
                duration_minutes=10,
                title="🎵 Uyanıklık Artırıcı",
                description="15 Hz ile uyanıklığı destekler.",
                priority=2
            ),
            Recommendation(
                type=RecommendationType.BREATHING,
                duration_minutes=3,
                title="🫁 Hızlı Enerji Nefesi",
                description="Hızlı ve derin nefes alıp verme (Bellows Breath). "
                           "30 saniye hızlı nefes, 30 saniye normal nefes.",
                priority=2
            )
        ]
    
    def _maintenance_recommendations(self) -> List[Recommendation]:
        """Normal durum için önleyici öneriler."""
        return [
            Recommendation(
                type=RecommendationType.MEDITATION,
                duration_minutes=5,
                title="🧘 Mindfulness Anı",
                description="Kısa bir farkındalık egzersizi ile zihninizi tazeleyin.",
                priority=3
            )
        ]


# Test kodu
if __name__ == "__main__":
    from modules.mental_state_classifier import MentalState
    
    print("💡 Recommendation Engine Test\n")
    print("=" * 60)
    
    engine = RecommendationEngine()
    
    # Test senaryoları
    scenarios = [
        ("Yüksek Stres", MentalState(85, 50, 30, 0.8)),
        ("Düşük Odak", MentalState(30, 25, 20, 0.7)),
        ("Yüksek Uykusuzluk", MentalState(20, 40, 85, 0.9)),
        ("Normal Durum", MentalState(35, 60, 30, 0.8))
    ]
    
    for scenario_name, state in scenarios:
        print(f"\n📋 Senaryo: {scenario_name}")
        print(f"   Stres: {state.stress_level}, Odak: {state.focus_level}, "
              f"Uykusuzluk: {state.sleepiness_level}")
        print("-" * 60)
        
        recommendations = engine.generate(state)
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"\n  {i}. {rec.title}")
                print(f"     {rec.description}")
                if rec.frequency_hz:
                    print(f"     🎵 Frekans: {rec.frequency_hz} Hz")
                print(f"     ⏱️  Süre: {rec.duration_minutes} dakika")
        else:
            print("  ✅ Her şey yolunda! Öneri yok.")