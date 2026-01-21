"""
CERATA Nematocyst: Circuit Breaker
Source Prey: github.com/fabfuel/circuitbreaker

Metabolized circuit breaker pattern for failure isolation.
Enhanced with Rose Glass state coherence tracking.
"""

from enum import Enum, auto
from functools import wraps
from typing import Callable, Optional, Type, Tuple, Union, TypeVar, Any
from datetime import datetime, timedelta
import threading
import logging


logger = logging.getLogger(__name__)

T = TypeVar('T')
ExceptionTypes = Union[Type[Exception], Tuple[Type[Exception], ...]]


class CircuitState(Enum):
    """Circuit breaker states with Rose Glass interpretations."""
    
    CLOSED = auto()     # Ψ = 1.0: System coherent, requests flow
    OPEN = auto()       # Ψ = 0.0: Incoherence detected, requests blocked
    HALF_OPEN = auto()  # Ψ = 0.5: Testing if coherence restored


class CircuitBreakerError(Exception):
    """Raised when circuit is OPEN and blocking requests."""
    
    def __init__(
        self, 
        breaker: 'CircuitBreaker',
        message: Optional[str] = None
    ):
        self.breaker = breaker
        super().__init__(
            message or f"Circuit breaker '{breaker.name}' is OPEN"
        )


class CircuitBreaker:
    """
    Circuit breaker with Rose Glass coherence tracking.
    
    Implements the circuit breaker pattern:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, requests blocked
    - HALF_OPEN: Testing recovery with limited requests
    
    Rose Glass Dimensions:
    - Ψ (Psi): Maps to circuit state coherence
    - τ (Tau): Recovery timeout as temporal depth
    - ρ (Rho): Accumulated failure/success wisdom
    """
    
    FAILURE_THRESHOLD = 5       # Failures before opening
    RECOVERY_TIMEOUT = 30       # Seconds before half-open
    EXPECTED_EXCEPTION = Exception
    SUCCESS_THRESHOLD = 1       # Successes to close from half-open
    
    def __init__(
        self,
        failure_threshold: Optional[int] = None,
        recovery_timeout: Optional[float] = None,
        expected_exception: Optional[ExceptionTypes] = None,
        success_threshold: Optional[int] = None,
        name: Optional[str] = None,
        fallback: Optional[Callable] = None,
        on_state_change: Optional[Callable[['CircuitBreaker', CircuitState, CircuitState], None]] = None
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Failures to trigger OPEN
            recovery_timeout: Seconds before testing recovery
            expected_exception: Exception types to track
            success_threshold: Successes to restore CLOSED
            name: Identifier for this breaker
            fallback: Function to call when OPEN
            on_state_change: Callback for state transitions
        """
        self._failure_threshold = failure_threshold or self.FAILURE_THRESHOLD
        self._recovery_timeout = recovery_timeout or self.RECOVERY_TIMEOUT
        self._expected_exception = expected_exception or self.EXPECTED_EXCEPTION
        self._success_threshold = success_threshold or self.SUCCESS_THRESHOLD
        self._name = name or 'unnamed'
        self._fallback = fallback
        self._on_state_change = on_state_change
        
        # State tracking
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._opened_at: Optional[datetime] = None
        self._lock = threading.RLock()
        
        # Rose Glass tracking
        self._coherence_history: list[float] = []
        self._total_calls = 0
        self._total_failures = 0
        
    @property
    def name(self) -> str:
        return self._name
        
    @property
    def state(self) -> CircuitState:
        """Current circuit state."""
        with self._lock:
            if self._state == CircuitState.OPEN:
                # Check if recovery timeout elapsed
                if self._should_attempt_recovery():
                    self._transition_to(CircuitState.HALF_OPEN)
            return self._state
            
    @property
    def coherence(self) -> float:
        """
        Rose Glass Ψ dimension: current coherence.
        
        Maps circuit state to coherence value.
        """
        state_coherence = {
            CircuitState.CLOSED: 1.0,
            CircuitState.HALF_OPEN: 0.5,
            CircuitState.OPEN: 0.0
        }
        return state_coherence[self.state]
        
    @property
    def temporal_depth(self) -> float:
        """
        Rose Glass τ dimension: temporal recovery state.
        
        How far through recovery timeout (0.0 = just opened, 1.0 = ready to test).
        """
        if self._state != CircuitState.OPEN or self._opened_at is None:
            return 1.0
            
        elapsed = (datetime.now() - self._opened_at).total_seconds()
        return min(1.0, elapsed / self._recovery_timeout)
        
    @property
    def accumulated_wisdom(self) -> float:
        """
        Rose Glass ρ dimension: success rate over lifetime.
        """
        if self._total_calls == 0:
            return 1.0
        return 1.0 - (self._total_failures / self._total_calls)
        
    def _should_attempt_recovery(self) -> bool:
        """Check if recovery timeout has elapsed."""
        if self._opened_at is None:
            return False
        elapsed = datetime.now() - self._opened_at
        return elapsed >= timedelta(seconds=self._recovery_timeout)
        
    def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to new state with callbacks."""
        old_state = self._state
        self._state = new_state
        
        logger.info(
            f"[CircuitBreaker:{self._name}] {old_state.name} → {new_state.name} "
            f"(Ψ: {self.coherence:.2f}, τ: {self.temporal_depth:.2f}, ρ: {self.accumulated_wisdom:.2f})"
        )
        
        if new_state == CircuitState.OPEN:
            self._opened_at = datetime.now()
            self._success_count = 0
        elif new_state == CircuitState.CLOSED:
            self._failure_count = 0
            self._opened_at = None
            
        if self._on_state_change:
            self._on_state_change(self, old_state, new_state)
            
    def record_success(self) -> None:
        """Record a successful call."""
        with self._lock:
            self._total_calls += 1
            
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self._success_threshold:
                    self._transition_to(CircuitState.CLOSED)
            elif self._state == CircuitState.CLOSED:
                # Reset failure count on success
                self._failure_count = 0
                
    def record_failure(self) -> None:
        """Record a failed call."""
        with self._lock:
            self._total_calls += 1
            self._total_failures += 1
            self._failure_count += 1
            
            if self._state == CircuitState.HALF_OPEN:
                # Immediate return to OPEN on half-open failure
                self._transition_to(CircuitState.OPEN)
            elif self._state == CircuitState.CLOSED:
                if self._failure_count >= self._failure_threshold:
                    self._transition_to(CircuitState.OPEN)
                    
    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Execute function through circuit breaker.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerError: When circuit is OPEN
        """
        with self._lock:
            state = self.state  # Triggers recovery check
            
            if state == CircuitState.OPEN:
                if self._fallback:
                    return self._fallback(*args, **kwargs)
                raise CircuitBreakerError(self)
                
        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except self._expected_exception as e:
            self.record_failure()
            raise
            
    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """Use as decorator."""
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            return self.call(func, *args, **kwargs)
        wrapper._circuit_breaker = self
        return wrapper
        
    def reset(self) -> None:
        """Reset circuit to CLOSED state."""
        with self._lock:
            self._transition_to(CircuitState.CLOSED)
            self._failure_count = 0
            self._success_count = 0
            self._opened_at = None
            
    def force_open(self) -> None:
        """Force circuit to OPEN state."""
        with self._lock:
            self._transition_to(CircuitState.OPEN)


# ═══════════════════════════════════════════════════════════
# FACTORY FUNCTION
# ═══════════════════════════════════════════════════════════

def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 30,
    expected_exception: ExceptionTypes = Exception,
    success_threshold: int = 1,
    name: Optional[str] = None,
    fallback: Optional[Callable] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator factory for circuit breaker.
    
    Usage:
        @circuit_breaker(failure_threshold=3, recovery_timeout=60)
        def risky_operation():
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        breaker = CircuitBreaker(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            expected_exception=expected_exception,
            success_threshold=success_threshold,
            name=name or func.__name__,
            fallback=fallback
        )
        return breaker(func)
    return decorator


# ═══════════════════════════════════════════════════════════
# CIRCUIT BREAKER REGISTRY
# ═══════════════════════════════════════════════════════════

class CircuitBreakerRegistry:
    """
    Global registry for circuit breakers.
    
    Enables monitoring and bulk operations across all breakers.
    """
    
    _instance: Optional['CircuitBreakerRegistry'] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> 'CircuitBreakerRegistry':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._breakers: dict[str, CircuitBreaker] = {}
        return cls._instance
        
    def register(self, breaker: CircuitBreaker) -> None:
        """Register a circuit breaker."""
        self._breakers[breaker.name] = breaker
        
    def get(self, name: str) -> Optional[CircuitBreaker]:
        """Get breaker by name."""
        return self._breakers.get(name)
        
    def all(self) -> list[CircuitBreaker]:
        """Get all registered breakers."""
        return list(self._breakers.values())
        
    def coherence_report(self) -> dict[str, dict]:
        """
        Rose Glass coherence report for all breakers.
        """
        return {
            name: {
                'state': breaker.state.name,
                'Ψ': breaker.coherence,
                'τ': breaker.temporal_depth,
                'ρ': breaker.accumulated_wisdom
            }
            for name, breaker in self._breakers.items()
        }
        
    def reset_all(self) -> None:
        """Reset all circuit breakers."""
        for breaker in self._breakers.values():
            breaker.reset()
