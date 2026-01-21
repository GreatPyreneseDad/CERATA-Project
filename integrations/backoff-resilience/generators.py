"""
CERATA Nematocyst: Backoff Generators
Source Prey: github.com/litl/backoff

Metabolized algorithms for calculating retry delays.
Enhanced with Rose Glass temporal awareness (τ dimension).
"""

from typing import Generator, Optional, Callable
import random
import math


def expo(
    base: float = 2,
    factor: float = 1,
    max_value: Optional[float] = None
) -> Generator[float, None, None]:
    """
    Exponential backoff generator.
    
    Produces: factor * base^n for n = 0, 1, 2, ...
    
    Rose Glass τ interpretation:
    - Higher base = faster temporal pressure increase
    - max_value caps accumulated temporal stress
    
    Args:
        base: Exponential base (default 2)
        factor: Multiplier (default 1)
        max_value: Maximum delay cap
        
    Yields:
        Successive delay values
    """
    n = 0
    while True:
        value = factor * (base ** n)
        if max_value is not None:
            value = min(value, max_value)
        yield value
        n += 1


def fibo(max_value: Optional[float] = None) -> Generator[float, None, None]:
    """
    Fibonacci backoff generator.
    
    Produces: 1, 1, 2, 3, 5, 8, 13, ...
    
    Rose Glass τ interpretation:
    - Natural growth pattern mirrors organic recovery
    - Golden ratio convergence = coherent temporal scaling
    
    Args:
        max_value: Maximum delay cap
        
    Yields:
        Fibonacci sequence values
    """
    a, b = 1, 1
    while True:
        value = a if max_value is None else min(a, max_value)
        yield value
        a, b = b, a + b


def constant(interval: float = 1) -> Generator[float, None, None]:
    """
    Constant interval generator.
    
    Produces: interval, interval, interval, ...
    
    Rose Glass τ interpretation:
    - Flat temporal pressure = steady state recovery
    - Use when system coherence is known-stable
    
    Args:
        interval: Fixed delay value
        
    Yields:
        Same interval repeatedly
    """
    while True:
        yield interval


def linear(
    initial: float = 1,
    increment: float = 1,
    max_value: Optional[float] = None
) -> Generator[float, None, None]:
    """
    Linear backoff generator.
    
    Produces: initial, initial+increment, initial+2*increment, ...
    
    Rose Glass τ interpretation:
    - Linear temporal pressure increase
    - Predictable recovery trajectory
    
    Args:
        initial: Starting delay
        increment: Added each iteration
        max_value: Maximum delay cap
        
    Yields:
        Linearly increasing values
    """
    value = initial
    while True:
        yield value if max_value is None else min(value, max_value)
        value += increment


def decorrelated_jitter(
    base: float = 1,
    cap: float = 60
) -> Generator[float, None, None]:
    """
    Decorrelated jitter generator (AWS-style).
    
    Produces: random between base and 3 * previous
    
    Rose Glass λ interpretation:
    - Jitter reduces lens interference between concurrent retries
    - Decorrelation prevents synchronized failures
    
    Args:
        base: Minimum delay floor
        cap: Maximum delay ceiling
        
    Yields:
        Decorrelated random delays
    """
    sleep = base
    while True:
        sleep = min(cap, random.uniform(base, sleep * 3))
        yield sleep


def full_jitter(
    base: float = 2,
    factor: float = 1,
    max_value: Optional[float] = None
) -> Generator[float, None, None]:
    """
    Full jitter exponential backoff (AWS-recommended).
    
    Produces: random(0, min(cap, base * 2^n))
    
    Rose Glass λ interpretation:
    - Maximum decorrelation = minimum λ interference
    - Optimal for high-contention scenarios
    
    Args:
        base: Exponential base
        factor: Base multiplier
        max_value: Delay ceiling
        
    Yields:
        Jittered exponential delays
    """
    n = 0
    while True:
        ceiling = factor * (base ** n)
        if max_value is not None:
            ceiling = min(ceiling, max_value)
        yield random.uniform(0, ceiling)
        n += 1


def equal_jitter(
    base: float = 2,
    factor: float = 1,
    max_value: Optional[float] = None
) -> Generator[float, None, None]:
    """
    Equal jitter exponential backoff.
    
    Produces: (ceiling / 2) + random(0, ceiling / 2)
    
    Rose Glass λ interpretation:
    - Balanced jitter = moderate λ reduction
    - Guarantees minimum wait time
    
    Args:
        base: Exponential base
        factor: Base multiplier
        max_value: Delay ceiling
        
    Yields:
        Half-jittered exponential delays
    """
    n = 0
    while True:
        ceiling = factor * (base ** n)
        if max_value is not None:
            ceiling = min(ceiling, max_value)
        half = ceiling / 2
        yield half + random.uniform(0, half)
        n += 1


def jittered(
    generator: Generator[float, None, None],
    jitter_factor: float = 0.5
) -> Generator[float, None, None]:
    """
    Wrapper to add jitter to any generator.
    
    Produces: value * (1 - jitter + random(0, 2*jitter))
    
    Rose Glass λ interpretation:
    - Universal λ reducer for any backoff pattern
    - jitter_factor controls interference dampening
    
    Args:
        generator: Base delay generator
        jitter_factor: Jitter range (0-1)
        
    Yields:
        Jittered values from base generator
    """
    for value in generator:
        jitter_range = value * jitter_factor
        yield value + random.uniform(-jitter_range, jitter_range)


def adaptive(
    success_shrink: float = 0.5,
    failure_grow: float = 2.0,
    initial: float = 1.0,
    min_value: float = 0.1,
    max_value: float = 60.0
) -> Generator[float, None, None]:
    """
    Adaptive backoff that responds to send signals.
    
    Send True for success (shrink delay), False for failure (grow delay).
    
    Rose Glass ρ interpretation:
    - Accumulated wisdom drives delay adaptation
    - Success/failure history shapes recovery trajectory
    
    Args:
        success_shrink: Multiply factor on success
        failure_grow: Multiply factor on failure
        initial: Starting delay
        min_value: Floor for adaptation
        max_value: Ceiling for adaptation
        
    Yields:
        Adapted delay values (send success/failure feedback)
    """
    delay = initial
    while True:
        success = yield delay
        if success is True:
            delay = max(min_value, delay * success_shrink)
        elif success is False:
            delay = min(max_value, delay * failure_grow)
        # None = no feedback, keep current delay


# ═══════════════════════════════════════════════════════════
# ROSE GLASS COHERENCE TRACKING
# ═══════════════════════════════════════════════════════════

class CoherenceAwareBackoff:
    """
    Backoff generator with Rose Glass coherence tracking.
    
    Monitors temporal dimension (τ) and adjusts strategy
    based on observed system coherence patterns.
    """
    
    def __init__(
        self,
        base_generator: Callable[[], Generator[float, None, None]] = expo,
        coherence_threshold: float = 0.6,
        **generator_kwargs
    ):
        """
        Args:
            base_generator: Generator factory function
            coherence_threshold: τ threshold for strategy switch
            **generator_kwargs: Passed to base_generator
        """
        self.base_generator = base_generator
        self.generator_kwargs = generator_kwargs
        self.coherence_threshold = coherence_threshold
        self._generator: Optional[Generator[float, None, None]] = None
        self._attempt_count = 0
        self._coherence_history: list[float] = []
        
    def reset(self) -> None:
        """Reset generator state."""
        self._generator = None
        self._attempt_count = 0
        
    def record_coherence(self, tau: float) -> None:
        """Record observed temporal coherence."""
        self._coherence_history.append(tau)
        # Keep last 10 observations
        self._coherence_history = self._coherence_history[-10:]
        
    @property
    def average_coherence(self) -> float:
        """Average τ from recent observations."""
        if not self._coherence_history:
            return 1.0
        return sum(self._coherence_history) / len(self._coherence_history)
    
    def __iter__(self):
        return self
    
    def __next__(self) -> float:
        if self._generator is None:
            # Select strategy based on coherence
            if self.average_coherence < self.coherence_threshold:
                # Low coherence = more aggressive backoff
                self._generator = full_jitter(
                    max_value=self.generator_kwargs.get('max_value', 60)
                )
            else:
                self._generator = self.base_generator(**self.generator_kwargs)
                
        self._attempt_count += 1
        return next(self._generator)
