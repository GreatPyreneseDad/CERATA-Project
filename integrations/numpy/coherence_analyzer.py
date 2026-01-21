"""
Coherence Analyzer - Pattern Decomposition via FFT
===================================================

Nematocyst extracted from NumPy's FFT capabilities.
Transforms frequency analysis into Rose Glass coherence perception.

Pattern decomposition reveals underlying rhythms and cycles
in communication, behavior, and data - the "music" beneath the surface.
"""

from typing import Dict, List, Optional, Tuple, Any, Union, Sequence
from dataclasses import dataclass, field
from enum import Enum
import math

# NumPy import with graceful fallback
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None


@dataclass
class FrequencyPattern:
    """A dominant pattern found in the data."""
    frequency: float          # Cycles per unit
    amplitude: float          # Strength of pattern (0.0-1.0)
    phase: float              # Phase offset (radians)
    interpretation: str       # Human-readable meaning
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'frequency': self.frequency,
            'amplitude': self.amplitude,
            'phase': self.phase,
            'interpretation': self.interpretation
        }


@dataclass
class PatternDecomposition:
    """Result of decomposing data into frequency patterns."""
    dominant_patterns: List[FrequencyPattern]
    noise_level: float        # Background noise (0.0-1.0)
    periodicity: float        # Overall periodic strength (0.0-1.0)
    coherence: float          # Pattern coherence score (0.0-1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'dominant_patterns': [p.to_dict() for p in self.dominant_patterns],
            'noise_level': self.noise_level,
            'periodicity': self.periodicity,
            'coherence': self.coherence
        }


@dataclass
class CoherenceResult:
    """Cross-coherence between two signals."""
    coherence: float          # Overall coherence (0.0-1.0)
    phase_alignment: float    # How aligned the phases are (0.0-1.0)
    frequency_overlap: float  # Shared frequency content (0.0-1.0)
    dominant_shared_freq: Optional[float]  # Strongest shared frequency
    notes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'coherence': self.coherence,
            'phase_alignment': self.phase_alignment,
            'frequency_overlap': self.frequency_overlap,
            'dominant_shared_freq': self.dominant_shared_freq
        }


class CoherenceAnalyzer:
    """
    Rose Glass analyzer for pattern coherence via FFT.
    
    Transforms NumPy's frequency analysis into Rose Glass perception.
    Patterns in data become visible structure - the underlying rhythms.
    
    Philosophy:
        "Every signal has a song. We perceive the melody."
        
        FFT reveals not just frequencies, but the coherence of 
        underlying patterns - how consistently something oscillates.
    """
    
    def __init__(self, sample_rate: float = 1.0):
        """
        Initialize coherence analyzer.
        
        Args:
            sample_rate: Samples per unit time (affects frequency interpretation)
        """
        if not NUMPY_AVAILABLE:
            raise ImportError(
                "NumPy not available. Install with: pip install numpy"
            )
        
        self.sample_rate = sample_rate
    
    def decompose_patterns(self,
                           data: Union[Sequence[float], 'np.ndarray'],
                           n_patterns: int = 5
                           ) -> PatternDecomposition:
        """
        Decompose data into dominant frequency patterns.
        
        Args:
            data: Time series or sequential data
            n_patterns: Number of dominant patterns to identify
            
        Returns:
            PatternDecomposition with frequency analysis
        """
        arr = np.asarray(data, dtype=np.float64)
        
        if arr.size < 4:
            return PatternDecomposition(
                dominant_patterns=[],
                noise_level=1.0,
                periodicity=0.0,
                coherence=0.0
            )
        
        # Remove DC component (mean)
        arr_centered = arr - np.mean(arr)
        
        # FFT
        fft_result = np.fft.rfft(arr_centered)
        frequencies = np.fft.rfftfreq(len(arr_centered), d=1.0/self.sample_rate)
        
        # Power spectrum (normalized)
        power = np.abs(fft_result) ** 2
        if power.sum() > 0:
            power_norm = power / power.sum()
        else:
            power_norm = power
        
        # Find dominant frequencies (excluding DC at index 0)
        if len(power_norm) > 1:
            top_indices = np.argsort(power_norm[1:])[-n_patterns:][::-1] + 1
        else:
            top_indices = []
        
        # Extract patterns
        patterns = []
        total_power = power.sum() if power.sum() > 0 else 1.0
        
        for idx in top_indices:
            if idx < len(frequencies) and power[idx] > 0:
                amp = np.sqrt(power[idx]) / np.sqrt(total_power)
                phase = np.angle(fft_result[idx])
                freq = frequencies[idx]
                
                # Interpret frequency
                interpretation = self._interpret_frequency(freq)
                
                patterns.append(FrequencyPattern(
                    frequency=float(freq),
                    amplitude=float(np.clip(amp, 0.0, 1.0)),
                    phase=float(phase),
                    interpretation=interpretation
                ))
        
        # Calculate overall metrics
        noise_level = self._calculate_noise_level(power_norm)
        periodicity = self._calculate_periodicity(power_norm)
        coherence = self._calculate_pattern_coherence(patterns, periodicity)
        
        return PatternDecomposition(
            dominant_patterns=patterns,
            noise_level=float(noise_level),
            periodicity=float(periodicity),
            coherence=float(coherence)
        )

    def cross_coherence(self,
                        data1: Union[Sequence[float], 'np.ndarray'],
                        data2: Union[Sequence[float], 'np.ndarray']
                        ) -> CoherenceResult:
        """
        Calculate cross-coherence between two signals.
        
        Measures how coherently two data streams relate to each other
        in the frequency domain.
        
        Args:
            data1: First time series
            data2: Second time series
            
        Returns:
            CoherenceResult with cross-coherence metrics
        """
        arr1 = np.asarray(data1, dtype=np.float64)
        arr2 = np.asarray(data2, dtype=np.float64)
        
        # Pad to same length
        max_len = max(len(arr1), len(arr2))
        arr1 = np.pad(arr1, (0, max_len - len(arr1)), mode='constant')
        arr2 = np.pad(arr2, (0, max_len - len(arr2)), mode='constant')
        
        # FFT of both
        fft1 = np.fft.rfft(arr1 - np.mean(arr1))
        fft2 = np.fft.rfft(arr2 - np.mean(arr2))
        frequencies = np.fft.rfftfreq(max_len, d=1.0/self.sample_rate)
        
        # Cross-spectral density
        cross_spectrum = fft1 * np.conj(fft2)
        
        # Power spectra
        power1 = np.abs(fft1) ** 2
        power2 = np.abs(fft2) ** 2
        
        # Coherence at each frequency
        denominator = np.sqrt(power1 * power2)
        denominator[denominator < 1e-10] = 1e-10
        coherence_spectrum = np.abs(cross_spectrum) / denominator
        
        # Phase difference
        phase_diff = np.angle(cross_spectrum)
        
        # Overall metrics
        # Frequency overlap: how much power is in the same frequencies
        norm1 = power1 / (power1.sum() + 1e-10)
        norm2 = power2 / (power2.sum() + 1e-10)
        overlap = np.sum(np.minimum(norm1, norm2))
        
        # Phase alignment: how consistent is the phase relationship
        phase_variance = np.var(phase_diff[power1 > 0.01 * power1.max()])
        phase_alignment = 1.0 / (1.0 + phase_variance)
        
        # Dominant shared frequency
        shared_power = np.minimum(power1, power2)
        if shared_power.sum() > 0:
            dominant_idx = np.argmax(shared_power[1:]) + 1
            dominant_shared_freq = float(frequencies[dominant_idx])
        else:
            dominant_shared_freq = None
        
        # Overall coherence
        coherence = overlap * 0.5 + phase_alignment * 0.3 + np.mean(coherence_spectrum) * 0.2
        
        notes = []
        if coherence > 0.7:
            notes.append("Strong coherence: signals share significant structure")
        elif coherence < 0.3:
            notes.append("Weak coherence: signals largely independent")
        
        return CoherenceResult(
            coherence=float(np.clip(coherence, 0.0, 1.0)),
            phase_alignment=float(np.clip(phase_alignment, 0.0, 1.0)),
            frequency_overlap=float(np.clip(overlap, 0.0, 1.0)),
            dominant_shared_freq=dominant_shared_freq,
            notes=notes
        )
    
    def _interpret_frequency(self, freq: float) -> str:
        """Generate human-readable interpretation of frequency."""
        if freq < 0.1:
            return "Very slow cycle (long-term trend)"
        elif freq < 0.25:
            return "Slow cycle (gradual rhythm)"
        elif freq < 0.5:
            return "Medium cycle (regular pattern)"
        elif freq < 1.0:
            return "Fast cycle (rapid oscillation)"
        else:
            return "Very fast cycle (high-frequency activity)"
    
    def _calculate_noise_level(self, power_norm: 'np.ndarray') -> float:
        """Estimate noise level from power spectrum."""
        if len(power_norm) < 3:
            return 0.5
        
        # Noise is estimated by the "flatness" of the spectrum
        # Pure noise = flat spectrum; strong signal = peaked spectrum
        spectral_flatness = np.exp(np.mean(np.log(power_norm + 1e-10))) / (np.mean(power_norm) + 1e-10)
        
        # Flatness near 1 = pure noise; near 0 = strong signal
        return float(np.clip(spectral_flatness, 0.0, 1.0))
    
    def _calculate_periodicity(self, power_norm: 'np.ndarray') -> float:
        """Calculate overall periodic strength."""
        if len(power_norm) < 2:
            return 0.0
        
        # Periodicity: how much power is concentrated in a few frequencies
        # High periodicity = few strong peaks
        # Low periodicity = spread across all frequencies
        
        # Use entropy as measure
        power_norm_safe = power_norm[power_norm > 1e-10]
        if len(power_norm_safe) == 0:
            return 0.0
        
        entropy = -np.sum(power_norm_safe * np.log(power_norm_safe))
        max_entropy = np.log(len(power_norm))
        
        # Low entropy = high periodicity
        if max_entropy > 0:
            periodicity = 1.0 - (entropy / max_entropy)
        else:
            periodicity = 0.5
        
        return float(np.clip(periodicity, 0.0, 1.0))
    
    def _calculate_pattern_coherence(self, 
                                      patterns: List[FrequencyPattern],
                                      periodicity: float) -> float:
        """Calculate overall pattern coherence from extracted patterns."""
        if not patterns:
            return periodicity * 0.5
        
        # Coherence based on:
        # 1. Periodicity (already calculated)
        # 2. Amplitude concentration (few strong patterns vs many weak)
        # 3. Phase consistency (not random phases)
        
        amplitudes = [p.amplitude for p in patterns]
        phases = [p.phase for p in patterns]
        
        # Amplitude concentration
        amp_sum = sum(amplitudes)
        if amp_sum > 0:
            amp_concentration = max(amplitudes) / amp_sum
        else:
            amp_concentration = 0.0
        
        # Phase consistency (low variance = consistent)
        phase_variance = np.var(phases) if len(phases) > 1 else 0.0
        phase_consistency = 1.0 / (1.0 + phase_variance)
        
        coherence = periodicity * 0.4 + amp_concentration * 0.35 + phase_consistency * 0.25
        
        return float(np.clip(coherence, 0.0, 1.0))


# Export main components
__all__ = [
    'CoherenceAnalyzer',
    'PatternDecomposition',
    'FrequencyPattern',
    'CoherenceResult'
]
