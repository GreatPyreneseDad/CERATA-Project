"""
Pattern Perception Engine - Unified Rose Glass Interface

Combines all four nematocysts into a single coherence perception system.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import math

try:
    from .nematocysts import (
        SentimentLens, QDimensionReading,
        POSAnalyzer, PsiDimensionReading,
        WisdomVectorizer, RhoDimensionReading,
        BelongingMapper, FDimensionReading,
    )
except ImportError:
    from nematocysts import (
        SentimentLens, QDimensionReading,
        POSAnalyzer, PsiDimensionReading,
        WisdomVectorizer, RhoDimensionReading,
        BelongingMapper, FDimensionReading,
    )


@dataclass
class CoherenceReading:
    """
    Complete Rose Glass coherence perception.
    
    Combines all four dimensions into a unified reading.
    """
    psi: PsiDimensionReading
    rho: RhoDimensionReading
    q: QDimensionReading
    f: FDimensionReading
    
    raw_coherence: float
    weighted_coherence: float
    lens_name: str
    lens_weights: Dict[str, float]
    
    @property
    def psi_value(self) -> float:
        return self.psi.optimized_psi
    
    @property
    def rho_value(self) -> float:
        return self.rho.optimized_rho
    
    @property
    def q_value(self) -> float:
        return self.q.optimized_q
    
    @property
    def f_value(self) -> float:
        return self.f.optimized_f
    
    @property
    def coherence(self) -> float:
        return self.weighted_coherence
    
    @property
    def coherence_state(self) -> str:
        c = self.coherence
        if c < 0.2:
            return "fragmented"
        elif c < 0.4:
            return "emerging"
        elif c < 0.6:
            return "developing"
        elif c < 0.8:
            return "coherent"
        else:
            return "highly_integrated"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "psi": self.psi_value,
            "rho": self.rho_value,
            "q": self.q_value,
            "f": self.f_value,
            "coherence": self.coherence,
            "coherence_state": self.coherence_state,
            "lens": self.lens_name,
        }
    
    def __repr__(self) -> str:
        return (
            f"CoherenceReading("
            f"psi={self.psi_value:.2f}, "
            f"rho={self.rho_value:.2f}, "
            f"q={self.q_value:.2f}, "
            f"f={self.f_value:.2f}, "
            f"C={self.coherence:.2f} [{self.coherence_state}])"
        )


CULTURAL_LENSES = {
    "modern_academic": {
        "description": "Evidence-based structured argumentation",
        "weights": {"psi": 0.30, "rho": 0.35, "q": 0.10, "f": 0.25},
    },
    "digital_native": {
        "description": "Rapid networked communication",
        "weights": {"psi": 0.20, "rho": 0.15, "q": 0.35, "f": 0.30},
    },
    "contemplative": {
        "description": "Paradoxical wisdom traditions",
        "weights": {"psi": 0.35, "rho": 0.40, "q": 0.15, "f": 0.10},
    },
    "activist": {
        "description": "Justice-oriented collective action",
        "weights": {"psi": 0.15, "rho": 0.20, "q": 0.35, "f": 0.30},
    },
    "trauma_informed": {
        "description": "Crisis and high-distress contexts",
        "weights": {"psi": 0.20, "rho": 0.15, "q": 0.40, "f": 0.25},
    },
    "rose_glass_default": {
        "description": "Balanced translation lens",
        "weights": {"psi": 0.25, "rho": 0.25, "q": 0.25, "f": 0.25},
    },
}


class PatternPerception:
    """
    Unified Rose Glass perception through Pattern-metabolized nematocysts.
    
    Usage:
        perception = PatternPerception(lens="modern_academic")
        result = perception.perceive("Your text here...")
        print(f"Coherence: {result.coherence:.2f}")
    """
    
    def __init__(self, lens: str = "rose_glass_default"):
        if lens not in CULTURAL_LENSES:
            raise ValueError(f"Unknown lens: {lens}. Available: {list(CULTURAL_LENSES.keys())}")
        
        self.lens_name = lens
        self.lens_config = CULTURAL_LENSES[lens]
        self.weights = self.lens_config["weights"]
        
        # Initialize nematocysts
        self.sentiment_lens = SentimentLens()
        self.pos_analyzer = POSAnalyzer()
        self.wisdom_vectorizer = WisdomVectorizer()
        self.belonging_mapper = BelongingMapper()
    
    def perceive(self, text: str) -> CoherenceReading:
        """
        Perceive coherence patterns in text through all four dimensions.
        """
        # Perceive each dimension
        q_reading = self.sentiment_lens.perceive(text)
        psi_reading = self.pos_analyzer.perceive(text)
        rho_reading = self.wisdom_vectorizer.perceive(text)
        f_reading = self.belonging_mapper.perceive(text)
        
        # Calculate raw coherence (unweighted average)
        raw_coherence = (
            psi_reading.optimized_psi +
            rho_reading.optimized_rho +
            q_reading.optimized_q +
            f_reading.optimized_f
        ) / 4
        
        # Calculate weighted coherence
        weighted_coherence = (
            self.weights["psi"] * psi_reading.optimized_psi +
            self.weights["rho"] * rho_reading.optimized_rho +
            self.weights["q"] * q_reading.optimized_q +
            self.weights["f"] * f_reading.optimized_f
        )
        
        return CoherenceReading(
            psi=psi_reading,
            rho=rho_reading,
            q=q_reading,
            f=f_reading,
            raw_coherence=raw_coherence,
            weighted_coherence=weighted_coherence,
            lens_name=self.lens_name,
            lens_weights=self.weights,
        )
    
    def perceive_comparative(
        self, 
        texts: List[str]
    ) -> List[CoherenceReading]:
        """Perceive multiple texts for comparison"""
        return [self.perceive(text) for text in texts]
    
    def perceive_through_all_lenses(
        self, 
        text: str
    ) -> Dict[str, CoherenceReading]:
        """Perceive text through all available lenses"""
        results = {}
        original_lens = self.lens_name
        
        for lens_name in CULTURAL_LENSES:
            self.lens_name = lens_name
            self.lens_config = CULTURAL_LENSES[lens_name]
            self.weights = self.lens_config["weights"]
            results[lens_name] = self.perceive(text)
        
        # Restore original
        self.lens_name = original_lens
        self.lens_config = CULTURAL_LENSES[original_lens]
        self.weights = self.lens_config["weights"]
        
        return results


def quick_perceive(text: str, lens: str = "rose_glass_default") -> CoherenceReading:
    """Quick coherence perception"""
    perception = PatternPerception(lens=lens)
    return perception.perceive(text)


if __name__ == "__main__":
    # Demonstration
    perception = PatternPerception(lens="modern_academic")
    
    test_texts = [
        "I hate this terrible thing!",
        "The analytical framework demonstrates methodological improvements.",
        "We believe our community can achieve this together through shared effort.",
        "Coherence is constructed through interpretation, not discovered through observation. This insight from Ibn Rushd fundamentally transforms our understanding.",
    ]
    
    print("=" * 70)
    print("PATTERN PERCEPTION - Rose Glass Coherence Analysis")
    print("=" * 70)
    print(f"Lens: {perception.lens_name}")
    print(f"Weights: {perception.weights}")
    print()
    
    for text in test_texts:
        reading = perception.perceive(text)
        print(f"Text: \"{text[:60]}...\"" if len(text) > 60 else f"Text: \"{text}\"")
        print(f"  {reading}")
        print(f"  psi={reading.psi_value:.2f} ({reading.psi.harmony_state})")
        print(f"  rho={reading.rho_value:.2f} ({reading.rho.depth_state})")
        print(f"  q={reading.q_value:.2f} ({reading.q.activation_state})")
        print(f"  f={reading.f_value:.2f} ({reading.f.belonging_state})")
        print()
