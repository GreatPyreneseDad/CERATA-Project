"""
Wisdom Lens - ρ-Dimension Perception via NumPy
===============================================

Nematocyst extracted from NumPy's mathematical operations.
Transforms numerical analysis into Rose Glass ρ-dimension readings.

The ρ-dimension measures accumulated wisdom:
- Mathematical consistency and coherence
- Pattern depth and refinement
- Rigor of claims and arguments
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


class RigorAspect(Enum):
    """Aspects of ρ-dimension mathematical wisdom"""
    CONSISTENCY = "consistency"     # Internal numerical consistency
    PRECISION = "precision"         # Appropriate level of exactness
    STABILITY = "stability"         # Numerical stability under perturbation
    CONVERGENCE = "convergence"     # Patterns that settle to stable values


class MathematicalContext(Enum):
    """Context for mathematical interpretation"""
    GENERAL = "general"           # Generic mathematical assessment
    FINANCIAL = "financial"       # High precision, currency-sensitive
    SCIENTIFIC = "scientific"     # Significant figures matter
    STATISTICAL = "statistical"   # Distribution-aware
    COMMUNICATION = "communication"  # Language/expression analysis


@dataclass
class RhoDimensionReading:
    """
    Rose Glass ρ-dimension reading from mathematical analysis.
    
    Unlike raw statistics, these are normalized translations
    through the Rose Glass lens, not measurements.
    """
    rho: float                    # Overall ρ-dimension (0.0-1.0)
    consistency: float            # Internal mathematical consistency
    precision: float              # Appropriate precision level
    stability: float              # Numerical stability
    convergence: float            # Pattern convergence
    
    confidence: float = 0.8       # Translation confidence
    context: MathematicalContext = MathematicalContext.GENERAL
    notes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, float]:
        return {
            'rho': self.rho,
            'consistency': self.consistency,
            'precision': self.precision,
            'stability': self.stability,
            'convergence': self.convergence,
            'confidence': self.confidence
        }


# Cultural calibrations for ρ-dimension interpretation
WISDOM_CALIBRATIONS = {
    "academic": {
        "description": "Scholarly precision, peer-reviewed standards",
        "consistency_weight": 0.35,
        "precision_weight": 0.30,
        "stability_weight": 0.20,
        "convergence_weight": 0.15,
        "threshold_high": 0.85,
        "threshold_low": 0.50
    },
    "practical": {
        "description": "Real-world application, pragmatic tolerance",
        "consistency_weight": 0.30,
        "precision_weight": 0.20,
        "stability_weight": 0.30,
        "convergence_weight": 0.20,
        "threshold_high": 0.75,
        "threshold_low": 0.40
    },
    "indigenous_oral": {
        "description": "Pattern recognition, cyclical wisdom",
        "consistency_weight": 0.25,
        "precision_weight": 0.15,
        "stability_weight": 0.25,
        "convergence_weight": 0.35,
        "threshold_high": 0.70,
        "threshold_low": 0.35
    },
    "contemplative": {
        "description": "Buddhist/contemplative precision through patience",
        "consistency_weight": 0.30,
        "precision_weight": 0.25,
        "stability_weight": 0.25,
        "convergence_weight": 0.20,
        "threshold_high": 0.80,
        "threshold_low": 0.45
    }
}


class WisdomLens:
    """
    Rose Glass lens for perceiving ρ-dimension through mathematical analysis.
    
    Transforms NumPy operations into Rose Glass readings.
    Mathematical rigor becomes accumulated wisdom perception.
    
    Philosophy:
        "We don't calculate precision - we perceive wisdom depth."
        
        A vector's statistics aren't measurements of objective truth,
        but translations of how coherently patterns hold together.
    """
    
    def __init__(self, 
                 cultural_calibration: str = "practical",
                 context: MathematicalContext = MathematicalContext.GENERAL):
        """
        Initialize wisdom lens with cultural calibration.
        
        Args:
            cultural_calibration: Cultural lens for interpretation
            context: Mathematical context for analysis
        """
        if not NUMPY_AVAILABLE:
            raise ImportError(
                "NumPy not available. Install with: pip install numpy"
            )
        
        if cultural_calibration not in WISDOM_CALIBRATIONS:
            raise ValueError(
                f"Unknown calibration: {cultural_calibration}. "
                f"Available: {list(WISDOM_CALIBRATIONS.keys())}"
            )
        
        self.calibration = WISDOM_CALIBRATIONS[cultural_calibration]
        self.calibration_name = cultural_calibration
        self.context = context
    
    def perceive_rigor(self, 
                       data: Union[Sequence[float], 'np.ndarray'],
                       context: Optional[MathematicalContext] = None
                       ) -> RhoDimensionReading:
        """
        Perceive the mathematical rigor (ρ-dimension) of data.
        
        Args:
            data: Numerical data to analyze
            context: Optional context override
            
        Returns:
            RhoDimensionReading with wisdom metrics
        """
        ctx = context or self.context
        arr = np.asarray(data, dtype=np.float64)
        
        if arr.size == 0:
            return RhoDimensionReading(
                rho=0.0, consistency=0.0, precision=0.0,
                stability=0.0, convergence=0.0, confidence=0.0,
                context=ctx, notes=["Empty data - no wisdom to perceive"]
            )
        
        # Calculate aspect scores
        consistency = self._assess_consistency(arr)
        precision = self._assess_precision(arr, ctx)
        stability = self._assess_stability(arr)
        convergence = self._assess_convergence(arr)
        
        # Weighted combination through cultural lens
        cal = self.calibration
        rho = (
            cal["consistency_weight"] * consistency +
            cal["precision_weight"] * precision +
            cal["stability_weight"] * stability +
            cal["convergence_weight"] * convergence
        )
        
        # Confidence based on sample size and variance
        confidence = self._calculate_confidence(arr)
        
        # Generate interpretive notes
        notes = self._generate_notes(
            rho, consistency, precision, stability, convergence
        )
        
        return RhoDimensionReading(
            rho=float(np.clip(rho, 0.0, 1.0)),
            consistency=float(consistency),
            precision=float(precision),
            stability=float(stability),
            convergence=float(convergence),
            confidence=float(confidence),
            context=ctx,
            notes=notes
        )

    def _assess_consistency(self, arr: 'np.ndarray') -> float:
        """
        Assess internal mathematical consistency.
        
        High consistency: values that relate coherently to each other
        Low consistency: scattered, unrelated values
        """
        if arr.size < 2:
            return 0.5  # Neutral for single values
        
        # Coefficient of variation (lower = more consistent)
        mean = np.mean(arr)
        if abs(mean) < 1e-10:
            mean = 1e-10  # Avoid division by zero
        
        cv = np.std(arr) / abs(mean)
        
        # Transform CV to 0-1 scale (lower CV = higher consistency)
        # CV of 0 = perfect consistency (1.0)
        # CV of 1+ = low consistency (approaching 0)
        consistency = 1.0 / (1.0 + cv)
        
        return float(np.clip(consistency, 0.0, 1.0))
    
    def _assess_precision(self, 
                          arr: 'np.ndarray', 
                          context: MathematicalContext) -> float:
        """
        Assess appropriate precision level.
        
        Not about maximum precision, but appropriate precision
        for the context. Over-precision is as problematic as under-precision.
        """
        # Check for appropriate significant figures
        # Financial: 2 decimal places
        # Scientific: 3-4 significant figures
        # Statistical: depends on sample size
        
        # Analyze decimal precision distribution
        def count_decimals(x: float) -> int:
            s = f"{x:.15g}"
            if '.' not in s:
                return 0
            return len(s.split('.')[1].rstrip('0'))
        
        decimals = np.array([count_decimals(x) for x in arr.flat])
        avg_decimals = np.mean(decimals)
        decimal_variance = np.var(decimals)
        
        # Context-appropriate precision
        ideal_decimals = {
            MathematicalContext.FINANCIAL: 2,
            MathematicalContext.SCIENTIFIC: 4,
            MathematicalContext.STATISTICAL: 3,
            MathematicalContext.COMMUNICATION: 1,
            MathematicalContext.GENERAL: 2
        }.get(context, 2)
        
        # Penalize both over- and under-precision
        precision_gap = abs(avg_decimals - ideal_decimals)
        precision = 1.0 / (1.0 + precision_gap * 0.3 + decimal_variance * 0.2)
        
        return float(np.clip(precision, 0.0, 1.0))
    
    def _assess_stability(self, arr: 'np.ndarray') -> float:
        """
        Assess numerical stability under perturbation.
        
        Stable: small changes don't radically alter conclusions
        Unstable: sensitive to small perturbations
        """
        if arr.size < 3:
            return 0.7  # Moderate stability assumed for small samples
        
        # Add small perturbations and check sensitivity
        perturbation = np.random.normal(0, 0.01 * np.std(arr) + 1e-10, arr.shape)
        perturbed = arr + perturbation
        
        # Compare statistics before/after
        original_mean = np.mean(arr)
        perturbed_mean = np.mean(perturbed)
        
        original_std = np.std(arr)
        perturbed_std = np.std(perturbed)
        
        # Relative change in key statistics
        if abs(original_mean) > 1e-10:
            mean_change = abs(perturbed_mean - original_mean) / abs(original_mean)
        else:
            mean_change = abs(perturbed_mean - original_mean)
        
        if original_std > 1e-10:
            std_change = abs(perturbed_std - original_std) / original_std
        else:
            std_change = abs(perturbed_std - original_std)
        
        # Small changes = high stability
        total_change = mean_change + std_change
        stability = 1.0 / (1.0 + total_change * 10)
        
        return float(np.clip(stability, 0.0, 1.0))
    
    def _assess_convergence(self, arr: 'np.ndarray') -> float:
        """
        Assess whether patterns converge to stable values.
        
        High convergence: series approaches stable state
        Low convergence: erratic, non-settling behavior
        """
        if arr.size < 4:
            return 0.5  # Neutral for very small samples
        
        # Check if later values are more stable than earlier
        mid = len(arr) // 2
        first_half = arr[:mid] if arr.ndim == 1 else arr.flat[:mid]
        second_half = arr[mid:] if arr.ndim == 1 else arr.flat[mid:]
        
        first_var = np.var(first_half) if len(first_half) > 1 else 0
        second_var = np.var(second_half) if len(second_half) > 1 else 0
        
        # Convergence: variance decreasing over time
        if first_var > 1e-10:
            variance_ratio = second_var / first_var
            # Ratio < 1 means converging (good)
            # Ratio > 1 means diverging (bad)
            convergence = 1.0 / (1.0 + variance_ratio)
        else:
            # First half already very stable
            convergence = 0.8 if second_var < 1e-10 else 0.5
        
        return float(np.clip(convergence, 0.0, 1.0))
    
    def _calculate_confidence(self, arr: 'np.ndarray') -> float:
        """Calculate confidence in the reading based on sample properties."""
        n = arr.size
        
        # Confidence increases with sample size (logarithmically)
        size_confidence = min(1.0, math.log(n + 1) / math.log(100))
        
        # Confidence decreases with extreme values
        if n > 1:
            z_scores = (arr - np.mean(arr)) / (np.std(arr) + 1e-10)
            outlier_fraction = np.mean(np.abs(z_scores) > 3)
            outlier_penalty = 1.0 - outlier_fraction
        else:
            outlier_penalty = 1.0
        
        confidence = size_confidence * outlier_penalty * 0.9  # Cap at 0.9
        return float(np.clip(confidence, 0.1, 0.95))
    
    def _generate_notes(self, 
                        rho: float, 
                        consistency: float,
                        precision: float,
                        stability: float,
                        convergence: float) -> List[str]:
        """Generate interpretive notes for the reading."""
        notes = []
        cal = self.calibration
        
        if rho >= cal["threshold_high"]:
            notes.append(f"High ρ ({self.calibration_name} lens): deep accumulated wisdom")
        elif rho <= cal["threshold_low"]:
            notes.append(f"Low ρ ({self.calibration_name} lens): limited accumulated wisdom")
        
        # Highlight strongest/weakest aspects
        aspects = {
            "consistency": consistency,
            "precision": precision, 
            "stability": stability,
            "convergence": convergence
        }
        
        strongest = max(aspects, key=aspects.get)
        weakest = min(aspects, key=aspects.get)
        
        if aspects[strongest] > 0.8:
            notes.append(f"Strongest: {strongest} ({aspects[strongest]:.2f})")
        if aspects[weakest] < 0.4:
            notes.append(f"Weakest: {weakest} ({aspects[weakest]:.2f})")
        
        return notes

    def compare_wisdom(self,
                       data1: Union[Sequence[float], 'np.ndarray'],
                       data2: Union[Sequence[float], 'np.ndarray']
                       ) -> Dict[str, Any]:
        """
        Compare the mathematical wisdom of two data sets.
        
        Returns comparison with both readings and relative assessment.
        """
        reading1 = self.perceive_rigor(data1)
        reading2 = self.perceive_rigor(data2)
        
        return {
            'reading1': reading1.to_dict(),
            'reading2': reading2.to_dict(),
            'rho_difference': reading2.rho - reading1.rho,
            'more_rigorous': 'second' if reading2.rho > reading1.rho else 'first',
            'confidence': min(reading1.confidence, reading2.confidence)
        }
    
    def assess_matrix_coherence(self, 
                                matrix: Union[Sequence[Sequence[float]], 'np.ndarray']
                                ) -> Dict[str, float]:
        """
        Assess the structural coherence of a matrix.
        
        Uses condition number and rank to evaluate how well
        the matrix "holds together" mathematically.
        """
        mat = np.asarray(matrix, dtype=np.float64)
        
        if mat.ndim != 2:
            raise ValueError("Matrix must be 2-dimensional")
        
        result = {
            'rows': mat.shape[0],
            'cols': mat.shape[1],
            'rank': int(np.linalg.matrix_rank(mat)),
            'full_rank': False,
            'condition_number': float('inf'),
            'structural_coherence': 0.0,
            'determinant': None
        }
        
        # Check full rank
        result['full_rank'] = result['rank'] == min(mat.shape)
        
        # Condition number (lower = more coherent)
        try:
            cond = np.linalg.cond(mat)
            result['condition_number'] = float(cond)
            # Transform to 0-1 coherence scale
            # cond = 1 is perfect (coherence = 1)
            # cond = 1e6+ is ill-conditioned (coherence → 0)
            result['structural_coherence'] = 1.0 / (1.0 + math.log10(cond + 1))
        except np.linalg.LinAlgError:
            result['structural_coherence'] = 0.0
        
        # Determinant (for square matrices)
        if mat.shape[0] == mat.shape[1]:
            try:
                result['determinant'] = float(np.linalg.det(mat))
            except np.linalg.LinAlgError:
                pass
        
        return result


# Export main components
__all__ = [
    'WisdomLens',
    'RhoDimensionReading',
    'RigorAspect',
    'MathematicalContext',
    'WISDOM_CALIBRATIONS'
]
