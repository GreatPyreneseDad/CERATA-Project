"""
Precision Engine - Numerical Rigor via NumPy
=============================================

Nematocyst extracted from NumPy's precision handling capabilities.
Transforms numerical comparison into Rose Glass rigor perception.

Precision is not about more decimal places - it's about appropriate
exactness for the context. This engine perceives that appropriateness.
"""

from typing import Dict, List, Optional, Any, Union, Sequence
from dataclasses import dataclass, field
from enum import Enum
import math

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None


class PrecisionContext(Enum):
    """Context determines appropriate precision standards."""
    EXACT = "exact"
    FINANCIAL = "financial"
    SCIENTIFIC = "scientific"
    ENGINEERING = "engineering"
    STATISTICAL = "statistical"
    COMMUNICATION = "communication"


@dataclass
class ToleranceProfile:
    """Tolerance settings for a given context."""
    absolute: float
    relative: float
    significant_figures: int
    description: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'absolute': self.absolute,
            'relative': self.relative,
            'significant_figures': self.significant_figures,
            'description': self.description
        }


TOLERANCE_PROFILES = {
    PrecisionContext.EXACT: ToleranceProfile(
        absolute=0.0, relative=0.0, significant_figures=15,
        description="Exact comparison - no tolerance"
    ),
    PrecisionContext.FINANCIAL: ToleranceProfile(
        absolute=0.005, relative=0.0001, significant_figures=2,
        description="Currency precision - 2 decimal places"
    ),
    PrecisionContext.SCIENTIFIC: ToleranceProfile(
        absolute=1e-10, relative=0.0001, significant_figures=4,
        description="Scientific - 4 significant figures"
    ),
    PrecisionContext.ENGINEERING: ToleranceProfile(
        absolute=1e-6, relative=0.001, significant_figures=3,
        description="Engineering tolerance"
    ),
    PrecisionContext.STATISTICAL: ToleranceProfile(
        absolute=0.001, relative=0.01, significant_figures=3,
        description="Statistical precision"
    ),
    PrecisionContext.COMMUNICATION: ToleranceProfile(
        absolute=0.5, relative=0.05, significant_figures=2,
        description="Human-readable approximation"
    ),
}


@dataclass
class ComparisonResult:
    """Result of precision-aware comparison."""
    equivalent: bool
    difference: float
    relative_difference: float
    within_tolerance: bool
    tolerance_used: ToleranceProfile
    confidence: float
    notes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'equivalent': self.equivalent,
            'difference': self.difference,
            'relative_difference': self.relative_difference,
            'within_tolerance': self.within_tolerance,
            'confidence': self.confidence
        }


class PrecisionEngine:
    """
    Rose Glass engine for precision-aware numerical operations.
    
    Philosophy:
        "Precision is wisdom about exactness - knowing when
        0.999 equals 1.0 and when it doesn't."
    """
    
    def __init__(self, default_context: PrecisionContext = PrecisionContext.SCIENTIFIC):
        if not NUMPY_AVAILABLE:
            raise ImportError("NumPy required. Install: pip install numpy")
        self.default_context = default_context
    
    def get_tolerance(self, context: Optional[PrecisionContext] = None) -> ToleranceProfile:
        """Get tolerance profile for context."""
        ctx = context or self.default_context
        return TOLERANCE_PROFILES[ctx]
    
    def coherent_compare(self,
                         value1: float,
                         value2: float,
                         context: Optional[PrecisionContext] = None
                         ) -> ComparisonResult:
        """
        Compare values with context-appropriate tolerance.
        """
        ctx = context or self.default_context
        tol = self.get_tolerance(ctx)
        
        diff = abs(value1 - value2)
        base = max(abs(value1), abs(value2), 1e-10)
        rel_diff = diff / base
        
        within_abs = diff <= tol.absolute
        within_rel = rel_diff <= tol.relative
        within_tolerance = within_abs or within_rel
        
        # Exact context requires both
        if ctx == PrecisionContext.EXACT:
            equivalent = value1 == value2
            within_tolerance = equivalent
        else:
            equivalent = within_tolerance
        
        notes = []
        if equivalent:
            notes.append(f"Values equivalent within {ctx.value} tolerance")
        else:
            notes.append(f"Difference {diff:.2e} exceeds tolerance")
        
        confidence = 0.95 if ctx != PrecisionContext.COMMUNICATION else 0.7
        
        return ComparisonResult(
            equivalent=equivalent,
            difference=float(diff),
            relative_difference=float(rel_diff),
            within_tolerance=within_tolerance,
            tolerance_used=tol,
            confidence=confidence,
            notes=notes
        )
    
    def coherent_array_compare(self,
                               arr1: Union[Sequence[float], 'np.ndarray'],
                               arr2: Union[Sequence[float], 'np.ndarray'],
                               context: Optional[PrecisionContext] = None
                               ) -> Dict[str, Any]:
        """Compare arrays element-wise with tolerance."""
        ctx = context or self.default_context
        tol = self.get_tolerance(ctx)
        
        a1 = np.asarray(arr1, dtype=np.float64)
        a2 = np.asarray(arr2, dtype=np.float64)
        
        if a1.shape != a2.shape:
            return {
                'equivalent': False,
                'reason': 'Shape mismatch',
                'shape1': a1.shape,
                'shape2': a2.shape
            }
        
        close = np.isclose(a1, a2, rtol=tol.relative, atol=tol.absolute)
        
        return {
            'equivalent': bool(np.all(close)),
            'match_fraction': float(np.mean(close)),
            'max_difference': float(np.max(np.abs(a1 - a2))),
            'mean_difference': float(np.mean(np.abs(a1 - a2))),
            'mismatches': int(np.sum(~close)),
            'context': ctx.value
        }
    
    def assess_numerical_rigor(self,
                               data: Union[Sequence[float], 'np.ndarray']
                               ) -> Dict[str, float]:
        """
        Assess numerical rigor of data for ρ-dimension.
        """
        arr = np.asarray(data, dtype=np.float64)
        
        if arr.size == 0:
            return {'rigor': 0.0, 'confidence': 0.0}
        
        # Check for NaN/Inf (low rigor)
        nan_fraction = np.mean(np.isnan(arr))
        inf_fraction = np.mean(np.isinf(arr))
        clean_fraction = 1.0 - nan_fraction - inf_fraction
        
        # Check precision consistency
        clean_data = arr[np.isfinite(arr)]
        if len(clean_data) > 1:
            # Coefficient of variation
            mean_val = np.mean(clean_data)
            if abs(mean_val) > 1e-10:
                cv = np.std(clean_data) / abs(mean_val)
                consistency = 1.0 / (1.0 + cv)
            else:
                consistency = 0.5
            
            # Check for suspiciously round numbers
            def is_round(x):
                return abs(x - round(x)) < 1e-10 or abs(x * 10 - round(x * 10)) < 1e-9
            round_fraction = np.mean([is_round(x) for x in clean_data])
            # Too many round numbers might indicate fabrication
            roundness_penalty = 0.0 if round_fraction < 0.8 else (round_fraction - 0.8)
        else:
            consistency = 0.5
            roundness_penalty = 0.0
        
        rigor = clean_fraction * 0.4 + consistency * 0.4 + (1.0 - roundness_penalty) * 0.2
        confidence = min(0.9, 0.5 + 0.1 * math.log(len(arr) + 1))
        
        return {
            'rigor': float(np.clip(rigor, 0.0, 1.0)),
            'clean_fraction': float(clean_fraction),
            'consistency': float(consistency),
            'confidence': float(confidence)
        }
    
    def round_to_context(self,
                         value: float,
                         context: Optional[PrecisionContext] = None
                         ) -> float:
        """Round value appropriately for context."""
        ctx = context or self.default_context
        tol = self.get_tolerance(ctx)
        
        if ctx == PrecisionContext.EXACT:
            return value
        elif ctx == PrecisionContext.FINANCIAL:
            return round(value, 2)
        elif ctx == PrecisionContext.COMMUNICATION:
            if abs(value) >= 1000:
                return round(value, -2)
            elif abs(value) >= 100:
                return round(value, -1)
            elif abs(value) >= 1:
                return round(value, 1)
            else:
                return round(value, 2)
        else:
            # Round to significant figures
            if value == 0:
                return 0.0
            magnitude = math.floor(math.log10(abs(value)))
            factor = 10 ** (tol.significant_figures - 1 - magnitude)
            return round(value * factor) / factor


__all__ = [
    'PrecisionEngine',
    'PrecisionContext', 
    'ComparisonResult',
    'ToleranceProfile',
    'TOLERANCE_PROFILES'
]
