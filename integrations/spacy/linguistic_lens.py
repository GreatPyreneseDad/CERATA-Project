"""
Linguistic Lens - Ψ/q/ρ Perception via spaCy
=============================================

Nematocyst extracted from explosion/spaCy NLP library.
Transforms linguistic analysis into Rose Glass dimensional readings.

- Ψ (Psi): Internal consistency via syntactic coherence
- q: Emotional activation via entity/sentiment patterns  
- ρ: Accumulated wisdom via vocabulary sophistication
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import Counter
import math

try:
    import spacy
    from spacy.tokens import Doc, Token, Span
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    spacy = None


class POSPattern(Enum):
    """Part-of-speech patterns indicating communication style."""
    NOUN_HEAVY = "noun_heavy"       # Concrete, object-focused
    VERB_HEAVY = "verb_heavy"       # Action-oriented
    ADJECTIVE_HEAVY = "adj_heavy"   # Descriptive, evaluative
    BALANCED = "balanced"           # Even distribution
    PRONOUN_HEAVY = "pronoun_heavy" # Personal, relational


@dataclass
class LinguisticCoherence:
    """Syntactic coherence metrics."""
    sentence_consistency: float   # Consistency of sentence structure
    dependency_depth: float       # Average parse tree depth (normalized)
    pos_entropy: float            # POS distribution entropy
    lexical_density: float        # Content words / total words
    
    def to_dict(self) -> Dict[str, float]:
        return {
            'sentence_consistency': self.sentence_consistency,
            'dependency_depth': self.dependency_depth,
            'pos_entropy': self.pos_entropy,
            'lexical_density': self.lexical_density
        }


@dataclass 
class PsiReading:
    """Rose Glass Ψ-dimension reading from linguistic analysis."""
    psi: float                    # Overall Ψ-dimension (0.0-1.0)
    rho: float                    # ρ-dimension from vocabulary
    q: float                      # q-dimension from entities/sentiment
    coherence: LinguisticCoherence
    pos_pattern: POSPattern
    entity_count: int
    confidence: float = 0.8
    notes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'psi': self.psi,
            'rho': self.rho,
            'q': self.q,
            'coherence': self.coherence.to_dict(),
            'pos_pattern': self.pos_pattern.value,
            'entity_count': self.entity_count,
            'confidence': self.confidence
        }


# Content POS tags (for lexical density)
CONTENT_POS = {'NOUN', 'VERB', 'ADJ', 'ADV', 'PROPN'}
FUNCTION_POS = {'DET', 'ADP', 'CCONJ', 'SCONJ', 'AUX', 'PART', 'PRON'}


class LinguisticLens:
    """
    Rose Glass lens for perceiving Ψ/q/ρ through linguistic analysis.
    
    Transforms spaCy NLP operations into Rose Glass readings.
    Syntax becomes consistency. Vocabulary becomes wisdom. Entities become activation.
    
    Philosophy:
        "We don't parse grammar - we perceive coherent expression."
    """
    
    def __init__(self, model: str = "en_core_web_sm"):
        """
        Initialize linguistic lens.
        
        Args:
            model: spaCy model to use (default: en_core_web_sm)
        """
        if not SPACY_AVAILABLE:
            raise ImportError(
                "spaCy not available. Install with: pip install spacy && "
                "python -m spacy download en_core_web_sm"
            )
        
        try:
            self.nlp = spacy.load(model)
        except OSError:
            raise ImportError(
                f"spaCy model '{model}' not found. Install with: "
                f"python -m spacy download {model}"
            )
        
        self.model_name = model
    
    def perceive(self, text: str) -> PsiReading:
        """
        Perceive the linguistic dimensions of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            PsiReading with Ψ, q, ρ dimensions
        """
        if not text or not text.strip():
            return PsiReading(
                psi=0.0, rho=0.0, q=0.0,
                coherence=LinguisticCoherence(0.0, 0.0, 0.0, 0.0),
                pos_pattern=POSPattern.BALANCED,
                entity_count=0,
                confidence=0.0,
                notes=["Empty text"]
            )
        
        doc = self.nlp(text)
        
        # Calculate components
        coherence = self._analyze_coherence(doc)
        pos_pattern = self._analyze_pos_pattern(doc)
        entity_count = len(doc.ents)
        
        # Ψ from syntactic coherence
        psi = self._calculate_psi(coherence)
        
        # ρ from vocabulary sophistication
        rho = self._calculate_rho(doc)
        
        # q from entities and sentiment indicators
        q = self._calculate_q(doc, entity_count)
        
        # Confidence based on text length
        confidence = min(0.95, 0.5 + len(doc) * 0.01)
        
        notes = self._generate_notes(psi, rho, q, pos_pattern)
        
        return PsiReading(
            psi=float(psi),
            rho=float(rho),
            q=float(q),
            coherence=coherence,
            pos_pattern=pos_pattern,
            entity_count=entity_count,
            confidence=float(confidence),
            notes=notes
        )
    
    def _analyze_coherence(self, doc: 'Doc') -> LinguisticCoherence:
        """Analyze syntactic coherence of document."""
        if len(doc) == 0:
            return LinguisticCoherence(0.0, 0.0, 0.0, 0.0)
        
        # Sentence structure consistency
        sent_lengths = [len(sent) for sent in doc.sents]
        if len(sent_lengths) > 1:
            mean_len = sum(sent_lengths) / len(sent_lengths)
            variance = sum((l - mean_len)**2 for l in sent_lengths) / len(sent_lengths)
            cv = math.sqrt(variance) / (mean_len + 0.01)
            sentence_consistency = 1.0 / (1.0 + cv)
        else:
            sentence_consistency = 0.7  # Neutral for single sentence
        
        # Dependency tree depth
        depths = []
        for token in doc:
            depth = 0
            current = token
            while current.head != current:
                depth += 1
                current = current.head
                if depth > 20:  # Safety limit
                    break
            depths.append(depth)
        avg_depth = sum(depths) / len(depths) if depths else 0
        # Normalize: depth 3-5 is typical, map to 0-1
        dependency_depth = min(1.0, avg_depth / 8.0)
        
        # POS distribution entropy
        pos_counts = Counter(token.pos_ for token in doc)
        total = sum(pos_counts.values())
        if total > 0:
            probs = [c / total for c in pos_counts.values()]
            entropy = -sum(p * math.log(p + 1e-10) for p in probs)
            max_entropy = math.log(len(pos_counts) + 1)
            pos_entropy = entropy / max_entropy if max_entropy > 0 else 0
        else:
            pos_entropy = 0.0
        
        # Lexical density
        content_count = sum(1 for t in doc if t.pos_ in CONTENT_POS)
        lexical_density = content_count / len(doc) if len(doc) > 0 else 0
        
        return LinguisticCoherence(
            sentence_consistency=float(sentence_consistency),
            dependency_depth=float(dependency_depth),
            pos_entropy=float(pos_entropy),
            lexical_density=float(lexical_density)
        )
    
    def _analyze_pos_pattern(self, doc: 'Doc') -> POSPattern:
        """Determine dominant POS pattern."""
        pos_counts = Counter(token.pos_ for token in doc)
        total = sum(pos_counts.values())
        
        if total == 0:
            return POSPattern.BALANCED
        
        noun_ratio = (pos_counts.get('NOUN', 0) + pos_counts.get('PROPN', 0)) / total
        verb_ratio = (pos_counts.get('VERB', 0) + pos_counts.get('AUX', 0)) / total
        adj_ratio = pos_counts.get('ADJ', 0) / total
        pron_ratio = pos_counts.get('PRON', 0) / total
        
        # Determine dominant pattern
        if noun_ratio > 0.35:
            return POSPattern.NOUN_HEAVY
        elif verb_ratio > 0.30:
            return POSPattern.VERB_HEAVY
        elif adj_ratio > 0.15:
            return POSPattern.ADJECTIVE_HEAVY
        elif pron_ratio > 0.15:
            return POSPattern.PRONOUN_HEAVY
        else:
            return POSPattern.BALANCED
    
    def _calculate_psi(self, coherence: LinguisticCoherence) -> float:
        """Calculate Ψ-dimension from coherence metrics."""
        # Weighted combination
        psi = (
            coherence.sentence_consistency * 0.30 +
            coherence.dependency_depth * 0.20 +
            coherence.pos_entropy * 0.25 +
            coherence.lexical_density * 0.25
        )
        return max(0.0, min(1.0, psi))
    
    def _calculate_rho(self, doc: 'Doc') -> float:
        """Calculate ρ-dimension from vocabulary sophistication."""
        if len(doc) == 0:
            return 0.0
        
        # Type-token ratio (vocabulary diversity)
        lemmas = [token.lemma_.lower() for token in doc if token.is_alpha]
        if len(lemmas) == 0:
            return 0.0
        ttr = len(set(lemmas)) / len(lemmas)
        
        # Average word length (proxy for sophistication)
        word_lengths = [len(token.text) for token in doc if token.is_alpha]
        avg_length = sum(word_lengths) / len(word_lengths) if word_lengths else 0
        length_score = min(1.0, avg_length / 8.0)  # 8+ char avg is sophisticated
        
        # Rare word ratio (not in most common)
        # Using word frequency if available
        rare_count = sum(1 for t in doc if t.is_alpha and t.is_oov)
        rare_ratio = rare_count / len([t for t in doc if t.is_alpha]) if len(doc) > 0 else 0
        
        rho = ttr * 0.4 + length_score * 0.3 + rare_ratio * 0.3
        return max(0.0, min(1.0, rho))
    
    def _calculate_q(self, doc: 'Doc', entity_count: int) -> float:
        """Calculate q-dimension from emotional activation indicators."""
        if len(doc) == 0:
            return 0.0
        
        # Entity density (named entities suggest engagement)
        entity_density = min(1.0, entity_count / (len(doc) / 10 + 1))
        
        # Exclamation/question marks (activation markers)
        punct_activation = sum(1 for t in doc if t.text in '!?') / (len(doc) + 1)
        punct_score = min(1.0, punct_activation * 10)
        
        # First person pronouns (personal engagement)
        first_person = sum(1 for t in doc if t.lower_ in {'i', 'me', 'my', 'we', 'us', 'our'})
        personal_ratio = first_person / len(doc)
        personal_score = min(1.0, personal_ratio * 5)
        
        # Intensifiers
        intensifiers = {'very', 'really', 'extremely', 'absolutely', 'totally', 'completely'}
        intensifier_count = sum(1 for t in doc if t.lower_ in intensifiers)
        intensifier_score = min(1.0, intensifier_count / (len(doc) / 20 + 1))
        
        q = (
            entity_density * 0.25 +
            punct_score * 0.25 +
            personal_score * 0.25 +
            intensifier_score * 0.25
        )
        return max(0.0, min(1.0, q))
    
    def _generate_notes(self, psi: float, rho: float, q: float, 
                        pos_pattern: POSPattern) -> List[str]:
        """Generate interpretive notes."""
        notes = []
        
        if psi > 0.7:
            notes.append("High Ψ: syntactically coherent expression")
        elif psi < 0.3:
            notes.append("Low Ψ: fragmented or inconsistent syntax")
        
        if rho > 0.7:
            notes.append("High ρ: sophisticated vocabulary")
        elif rho < 0.3:
            notes.append("Low ρ: simple or repetitive vocabulary")
        
        if q > 0.7:
            notes.append("High q: emotionally activated")
        elif q < 0.3:
            notes.append("Low q: emotionally neutral")
        
        pattern_notes = {
            POSPattern.NOUN_HEAVY: "Noun-heavy: concrete, object-focused",
            POSPattern.VERB_HEAVY: "Verb-heavy: action-oriented",
            POSPattern.ADJECTIVE_HEAVY: "Adjective-heavy: descriptive, evaluative",
            POSPattern.PRONOUN_HEAVY: "Pronoun-heavy: personal, relational",
            POSPattern.BALANCED: "Balanced POS distribution"
        }
        notes.append(pattern_notes.get(pos_pattern, ""))
        
        return [n for n in notes if n]


__all__ = [
    'LinguisticLens',
    'PsiReading', 
    'LinguisticCoherence',
    'POSPattern'
]
