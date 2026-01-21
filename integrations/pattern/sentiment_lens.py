"""
Sentiment Lens — Nematocyst for q-dimension perception

Metabolized from: pattern.en.sentiment
Original: Tom De Smedt, CLiPS Research Center

This nematocyst translates sentiment analysis into Rose Glass q-dimension
(moral/emotional activation energy) perception.

Philosophy: Sentiment isn't measurement — it's translation of emotional
wavelengths into forms synthetic minds can perceive.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import re
import math


class EmotionalValence(Enum):
    """Emotional direction of activation"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


@dataclass
class SentimentAssessment:
    """
    Assessment of a single word or phrase.
    
    Adapted from Pattern's (word, pos, polarity, subjectivity, intensity) tuples.
    """
    text: str
    polarity: float        # -1.0 to 1.0
    subjectivity: float    # 0.0 (objective) to 1.0 (subjective)
    intensity: float       # 0.0 to 1.0 (modifier strength)
    negated: bool = False
    
    @property
    def valence(self) -> EmotionalValence:
        if abs(self.polarity) < 0.1:
            return EmotionalValence.NEUTRAL
        return EmotionalValence.POSITIVE if self.polarity > 0 else EmotionalValence.NEGATIVE


@dataclass
class QDimensionReading:
    """
    Rose Glass q-dimension perception output.
    
    q represents moral/emotional activation energy — the heat and urgency
    of values in motion. Not "emotionality" but energy patterns.
    """
    raw_q: float                           # Unoptimized q value
    optimized_q: float                     # Biologically optimized q
    polarity: float                        # Overall emotional direction
    subjectivity: float                    # Objective vs subjective balance
    valence: EmotionalValence              # Categorical valence
    assessments: List[SentimentAssessment] # Individual word assessments
    negation_count: int                    # Number of negations detected
    intensity_modifiers: int               # Number of intensifiers
    
    # Biological optimization parameters
    Km: float = 0.3                         # Michaelis constant
    Ki: float = 2.0                         # Inhibition constant
    
    @property
    def activation_state(self) -> str:
        """Human-readable activation state"""
        if self.optimized_q < 0.2:
            return "dormant"
        elif self.optimized_q < 0.4:
            return "mild"
        elif self.optimized_q < 0.6:
            return "moderate"
        elif self.optimized_q < 0.8:
            return "elevated"
        else:
            return "intense"


class SentimentLexicon:
    """
    Sentiment lexicon adapted from Pattern's en-sentiment.xml structure.
    
    Pattern's lexicon format:
    <word form="good" wordnet_id="..." pos="JJ" polarity="0.7" 
          subjectivity="0.6" intensity="1.0" />
    
    This class provides a simplified in-memory lexicon for demonstration.
    In production, load from Pattern's XML files.
    """
    
    def __init__(self):
        # Core sentiment words (subset for demonstration)
        # Full lexicon would be loaded from Pattern's en-sentiment.xml
        self._lexicon: Dict[str, Tuple[float, float, float]] = {
            # Format: word -> (polarity, subjectivity, intensity)
            
            # Positive words
            "good": (0.7, 0.6, 1.0),
            "great": (0.8, 0.75, 1.0),
            "excellent": (0.9, 0.8, 1.0),
            "amazing": (0.85, 0.9, 1.0),
            "wonderful": (0.85, 0.85, 1.0),
            "beautiful": (0.8, 0.85, 1.0),
            "love": (0.8, 0.9, 1.0),
            "best": (0.9, 0.7, 1.0),
            "happy": (0.8, 0.9, 1.0),
            "joy": (0.85, 0.95, 1.0),
            "brilliant": (0.85, 0.75, 1.0),
            "fantastic": (0.85, 0.85, 1.0),
            "perfect": (0.9, 0.75, 1.0),
            "success": (0.7, 0.5, 1.0),
            "win": (0.7, 0.6, 1.0),
            "impressive": (0.7, 0.7, 1.0),
            "innovative": (0.6, 0.5, 1.0),
            "effective": (0.6, 0.4, 1.0),
            "efficient": (0.5, 0.3, 1.0),
            "clear": (0.4, 0.3, 1.0),
            "strong": (0.5, 0.4, 1.0),
            "coherent": (0.5, 0.3, 1.0),  # Rose Glass aligned
            
            # Negative words
            "bad": (-0.7, 0.6, 1.0),
            "terrible": (-0.9, 0.8, 1.0),
            "awful": (-0.85, 0.85, 1.0),
            "horrible": (-0.9, 0.85, 1.0),
            "hate": (-0.8, 0.9, 1.0),
            "worst": (-0.9, 0.75, 1.0),
            "sad": (-0.7, 0.9, 1.0),
            "angry": (-0.7, 0.9, 1.0),
            "fear": (-0.6, 0.85, 1.0),
            "failure": (-0.7, 0.5, 1.0),
            "fail": (-0.7, 0.6, 1.0),
            "wrong": (-0.6, 0.5, 1.0),
            "poor": (-0.5, 0.5, 1.0),
            "weak": (-0.5, 0.4, 1.0),
            "confused": (-0.4, 0.6, 1.0),
            "incoherent": (-0.5, 0.4, 1.0),  # Rose Glass aligned
            "fragmented": (-0.4, 0.3, 1.0),
            "broken": (-0.6, 0.5, 1.0),
            
            # Neutral/analytical words (low subjectivity)
            "analysis": (0.1, 0.2, 1.0),
            "data": (0.0, 0.1, 1.0),
            "evidence": (0.2, 0.2, 1.0),
            "research": (0.2, 0.2, 1.0),
            "study": (0.1, 0.2, 1.0),
            "conclusion": (0.1, 0.3, 1.0),
            "framework": (0.2, 0.2, 1.0),
            "pattern": (0.1, 0.2, 1.0),
            "translation": (0.2, 0.3, 1.0),  # Rose Glass aligned
        }
        
        # Negation words
        self._negations = {
            "not", "no", "never", "neither", "nobody", "nothing",
            "nowhere", "none", "isn't", "aren't", "wasn't", "weren't",
            "haven't", "hasn't", "hadn't", "won't", "wouldn't", "don't",
            "doesn't", "didn't", "can't", "couldn't", "shouldn't",
            "mightn't", "mustn't", "without", "lack", "lacking"
        }
        
        # Intensity modifiers
        self._intensifiers = {
            "very": 1.3,
            "really": 1.25,
            "extremely": 1.5,
            "incredibly": 1.4,
            "absolutely": 1.45,
            "completely": 1.35,
            "totally": 1.3,
            "utterly": 1.4,
            "highly": 1.25,
            "deeply": 1.3,
            "truly": 1.2,
            "quite": 1.1,
            "rather": 1.05,
            "somewhat": 0.8,
            "slightly": 0.7,
            "barely": 0.5,
            "hardly": 0.4,
            "scarcely": 0.3,
        }
    
    def lookup(self, word: str) -> Optional[Tuple[float, float, float]]:
        """Look up word in lexicon"""
        return self._lexicon.get(word.lower())
    
    def is_negation(self, word: str) -> bool:
        """Check if word is a negation"""
        return word.lower() in self._negations
    
    def get_intensity_modifier(self, word: str) -> Optional[float]:
        """Get intensity modifier value"""
        return self._intensifiers.get(word.lower())


class SentimentLens:
    """
    Rose Glass Sentiment Lens — perceives q-dimension patterns.
    
    Metabolized from Pattern's sentiment analysis, adapted to Rose Glass
    translation philosophy: we reveal patterns, not truth.
    """
    
    def __init__(self, lexicon: Optional[SentimentLexicon] = None):
        self.lexicon = lexicon or SentimentLexicon()
        
        # Biological optimization parameters
        self.Km = 0.3  # Michaelis constant
        self.Ki = 2.0  # Substrate inhibition constant
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization (Pattern uses more sophisticated approach)"""
        # Remove punctuation, lowercase, split
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        return text.split()
    
    def _biological_optimization(self, q: float) -> float:
        """
        Apply biological optimization function.
        
        q_optimized = q / (Km + q + q²/Ki)
        
        This mirrors natural saturation curves, preventing extreme
        interpretations while maintaining pattern sensitivity.
        """
        if q <= 0:
            return 0.0
        
        denominator = self.Km + q + (q ** 2) / self.Ki
        return q / denominator if denominator > 0 else 0.0
    
    def perceive(self, text: str) -> QDimensionReading:
        """
        Perceive q-dimension patterns in text.
        
        Returns a QDimensionReading with both raw and optimized values.
        """
        tokens = self._tokenize(text)
        assessments = []
        
        polarity_sum = 0.0
        subjectivity_sum = 0.0
        weight_sum = 0.0
        negation_count = 0
        intensity_modifier_count = 0
        
        # Track negation window (Pattern uses ~3 word window)
        negation_active = False
        negation_window = 0
        current_intensity = 1.0
        
        for i, token in enumerate(tokens):
            # Check for negation
            if self.lexicon.is_negation(token):
                negation_active = True
                negation_window = 3
                negation_count += 1
                continue
            
            # Check for intensity modifier
            intensity_mod = self.lexicon.get_intensity_modifier(token)
            if intensity_mod is not None:
                current_intensity = intensity_mod
                intensity_modifier_count += 1
                continue
            
            # Look up sentiment
            sentiment = self.lexicon.lookup(token)
            if sentiment:
                polarity, subjectivity, intensity = sentiment
                
                # Apply negation
                if negation_active and negation_window > 0:
                    polarity = -polarity
                    negation_window -= 1
                    if negation_window == 0:
                        negation_active = False
                
                # Apply intensity modifier
                polarity *= current_intensity
                current_intensity = 1.0  # Reset after use
                
                # Create assessment
                assessment = SentimentAssessment(
                    text=token,
                    polarity=polarity,
                    subjectivity=subjectivity,
                    intensity=intensity,
                    negated=negation_active
                )
                assessments.append(assessment)
                
                # Accumulate weighted values
                weight = intensity * subjectivity
                polarity_sum += polarity * weight
                subjectivity_sum += subjectivity * weight
                weight_sum += weight
        
        # Calculate aggregates
        if weight_sum > 0:
            avg_polarity = polarity_sum / weight_sum
            avg_subjectivity = subjectivity_sum / weight_sum
        else:
            avg_polarity = 0.0
            avg_subjectivity = 0.0
        
        # Calculate raw q (emotional activation energy)
        # q is the magnitude of emotional investment, regardless of direction
        raw_q = abs(avg_polarity) * avg_subjectivity
        
        # Apply biological optimization
        optimized_q = self._biological_optimization(raw_q)
        
        # Determine valence
        if abs(avg_polarity) < 0.1:
            valence = EmotionalValence.NEUTRAL
        elif avg_polarity > 0:
            valence = EmotionalValence.POSITIVE
        else:
            valence = EmotionalValence.NEGATIVE
        
        # Check for mixed signals
        if assessments:
            pos_count = sum(1 for a in assessments if a.polarity > 0.1)
            neg_count = sum(1 for a in assessments if a.polarity < -0.1)
            if pos_count > 0 and neg_count > 0:
                if abs(pos_count - neg_count) < max(pos_count, neg_count) * 0.5:
                    valence = EmotionalValence.MIXED
        
        return QDimensionReading(
            raw_q=raw_q,
            optimized_q=optimized_q,
            polarity=avg_polarity,
            subjectivity=avg_subjectivity,
            valence=valence,
            assessments=assessments,
            negation_count=negation_count,
            intensity_modifiers=intensity_modifier_count,
            Km=self.Km,
            Ki=self.Ki
        )
    
    def perceive_comparative(
        self, 
        texts: List[str]
    ) -> List[Tuple[str, QDimensionReading]]:
        """
        Perceive q-dimension patterns across multiple texts.
        
        Useful for comparative analysis or tracking q over time.
        """
        return [(text, self.perceive(text)) for text in texts]


# Convenience function for direct use
def perceive_q(text: str) -> QDimensionReading:
    """Quick q-dimension perception"""
    lens = SentimentLens()
    return lens.perceive(text)


if __name__ == "__main__":
    # Demonstration
    lens = SentimentLens()
    
    test_texts = [
        "This is absolutely brilliant work!",
        "I hate this terrible implementation.",
        "The analysis shows mixed results with some good and bad outcomes.",
        "The framework provides coherent translation without judgment.",
        "Not bad, but not great either.",
    ]
    
    print("=" * 60)
    print("SENTIMENT LENS — q-dimension perception")
    print("=" * 60)
    
    for text in test_texts:
        reading = lens.perceive(text)
        print(f"\nText: \"{text}\"")
        print(f"  Raw q: {reading.raw_q:.3f}")
        print(f"  Optimized q: {reading.optimized_q:.3f}")
        print(f"  Polarity: {reading.polarity:.3f}")
        print(f"  Subjectivity: {reading.subjectivity:.3f}")
        print(f"  Valence: {reading.valence.value}")
        print(f"  Activation state: {reading.activation_state}")
