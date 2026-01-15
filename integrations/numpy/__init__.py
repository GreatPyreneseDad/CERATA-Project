"""
Cerata NumPy Integration
========================

ρ-Dimension mathematical rigor perception powered by NumPy.

This integration metabolizes NumPy's 20 years of mathematical wisdom into 
Rose Glass dimensional perception. Mathematical operations become wisdom 
indicators. Precision becomes rigor metrics.

Nematocysts:
    - WisdomLens: ρ-dimension perception via mathematical analysis
    - CoherenceAnalyzer: Pattern decomposition for coherence assessment
    - PrecisionEngine: Numerical precision and tolerance handling
    - UncertaintyEngine: Stochastic wisdom and confidence intervals

Philosophy:
    "We don't calculate numbers - we perceive accumulated wisdom."
    
    NumPy operations are translated through cultural lenses,
    not treated as objective measurements. Each reading is a
    valid translation, not a score to be judged.

Usage:
    from integrations.numpy import WisdomLens, PrecisionEngine
    
    lens = WisdomLens()
    reading = lens.perceive_rigor([0.8, 0.9, 0.7, 0.85])
    
    print(f"ρ-dimension: {reading.rho}")
    print(f"Consistency: {reading.consistency}")
    print(f"Confidence: {reading.confidence}")

Hunt Record:
    Target: numpy/numpy
    Coherence: 0.88 (PRIME PREY)
    Hunt Date: 2026-01-15
    Status: CONSUMED
    License: BSD-3-Clause
    
Author: Christopher MacGregor bin Joseph
Date: January 2026
"""

from .wisdom_lens import (
    WisdomLens,
    RhoDimensionReading,
    RigorAspect,
    MathematicalContext
)

from .coherence_analyzer import (
    CoherenceAnalyzer,
    PatternDecomposition,
    FrequencyPattern,
    CoherenceResult
)

from .precision_engine import (
    PrecisionEngine,
    PrecisionContext,
    ComparisonResult,
    ToleranceProfile
)

__version__ = '1.0.0'
__author__ = 'Christopher MacGregor bin Joseph'
__prey__ = 'numpy/numpy'
__coherence__ = 0.88
__hunt_date__ = '2026-01-15'

__all__ = [
    # Version info
    '__version__',
    '__author__',
    '__prey__',
    '__coherence__',
    '__hunt_date__',
    
    # Wisdom lens (mathematical rigor → ρ-dimension)
    'WisdomLens',
    'RhoDimensionReading',
    'RigorAspect',
    'MathematicalContext',
    
    # Coherence analyzer (pattern decomposition)
    'CoherenceAnalyzer',
    'PatternDecomposition',
    'FrequencyPattern',
    'CoherenceResult',
    
    # Precision engine (numerical rigor)
    'PrecisionEngine',
    'PrecisionContext',
    'ComparisonResult',
    'ToleranceProfile',
]
