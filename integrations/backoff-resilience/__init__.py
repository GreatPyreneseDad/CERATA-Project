"""
CERATA Resilience Tools
═══════════════════════

Metabolized nematocysts for building resilient systems:

- **Backoff Generators**: Exponential, fibonacci, jittered delay algorithms
- **Retry Decorators**: Exception and predicate-based retry with Rose Glass tracking
- **Circuit Breaker**: Failure isolation with state coherence monitoring
- **Rate Limiter**: Token bucket, sliding window, fixed window algorithms

All components enhanced with Rose Glass dimensional tracking:
- Ψ (Psi): System coherence state
- τ (Tau): Temporal recovery depth
- ρ (Rho): Accumulated success/failure wisdom

Source Prey:
- github.com/litl/backoff (generators, decorators)
- github.com/fabfuel/circuitbreaker (breaker)
- github.com/alexdelorenzo/limiter (limiter)
"""

from .generators import (
    expo,
    fibo,
    constant,
    linear,
    decorrelated_jitter,
    full_jitter,
    equal_jitter,
    jittered,
    adaptive,
    CoherenceAwareBackoff
)

from .decorators import (
    on_exception,
    on_predicate,
    on_exception_async
)

from .breaker import (
    CircuitBreaker,
    CircuitBreakerError,
    CircuitState,
    circuit_breaker,
    CircuitBreakerRegistry
)

from .limiter import (
    Limiter,
    TokenBucket,
    SlidingWindow,
    FixedWindow,
    RateLimitResult,
    RateLimitExceeded,
    rate_limit
)


__all__ = [
    # Generators
    'expo',
    'fibo',
    'constant',
    'linear',
    'decorrelated_jitter',
    'full_jitter',
    'equal_jitter',
    'jittered',
    'adaptive',
    'CoherenceAwareBackoff',
    
    # Decorators
    'on_exception',
    'on_predicate',
    'on_exception_async',
    
    # Circuit Breaker
    'CircuitBreaker',
    'CircuitBreakerError',
    'CircuitState',
    'circuit_breaker',
    'CircuitBreakerRegistry',
    
    # Rate Limiter
    'Limiter',
    'TokenBucket',
    'SlidingWindow',
    'FixedWindow',
    'RateLimitResult',
    'RateLimitExceeded',
    'rate_limit',
]

__version__ = '1.0.0'
__prey__ = [
    'github.com/litl/backoff',
    'github.com/fabfuel/circuitbreaker',
    'github.com/alexdelorenzo/limiter'
]
