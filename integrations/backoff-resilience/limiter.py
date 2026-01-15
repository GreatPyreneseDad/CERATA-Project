"""
CERATA Nematocyst: Rate Limiter
Source Prey: github.com/alexdelorenzo/limiter

Metabolized rate limiting algorithms for request throttling.
Enhanced with Rose Glass coherence-aware throttling.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import wraps
from typing import Callable, Optional, TypeVar, Union
import asyncio
import threading
import time


T = TypeVar('T')


@dataclass
class RateLimitResult:
    """Result of a rate limit check."""
    allowed: bool
    remaining: int
    reset_at: Optional[datetime] = None
    retry_after: Optional[float] = None
    
    # Rose Glass dimensions
    coherence: float = 1.0  # Ψ: How coherent is current rate
    pressure: float = 0.0   # Load pressure (0 = idle, 1 = at limit)


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded."""
    
    def __init__(
        self,
        result: RateLimitResult,
        message: Optional[str] = None
    ):
        self.result = result
        super().__init__(
            message or f"Rate limit exceeded. Retry after {result.retry_after:.2f}s"
        )


# ═══════════════════════════════════════════════════════════
# BASE ALGORITHM
# ═══════════════════════════════════════════════════════════

class RateLimitAlgorithm(ABC):
    """Base class for rate limiting algorithms."""
    
    @abstractmethod
    def acquire(self, tokens: int = 1) -> RateLimitResult:
        """Attempt to acquire tokens."""
        pass
        
    @abstractmethod
    def reset(self) -> None:
        """Reset the limiter state."""
        pass
        
    @property
    @abstractmethod
    def coherence(self) -> float:
        """Rose Glass Ψ: current coherence."""
        pass


# ═══════════════════════════════════════════════════════════
# TOKEN BUCKET
# ═══════════════════════════════════════════════════════════

class TokenBucket(RateLimitAlgorithm):
    """
    Token bucket rate limiter.
    
    Tokens are added at a fixed rate up to a maximum capacity.
    Requests consume tokens; blocked when bucket empty.
    
    Rose Glass interpretation:
    - Bucket level maps to system coherence (Ψ)
    - Refill rate represents recovery capacity (τ)
    - Allows bursts while maintaining average rate
    """
    
    def __init__(
        self,
        rate: float,           # Tokens per second
        capacity: int,         # Maximum bucket size
        initial: Optional[int] = None  # Starting tokens (default: full)
    ):
        self._rate = rate
        self._capacity = capacity
        self._tokens = initial if initial is not None else capacity
        self._last_refill = time.monotonic()
        self._lock = threading.Lock()
        
    def _refill(self) -> None:
        """Add tokens based on elapsed time."""
        now = time.monotonic()
        elapsed = now - self._last_refill
        new_tokens = elapsed * self._rate
        self._tokens = min(self._capacity, self._tokens + new_tokens)
        self._last_refill = now
        
    def acquire(self, tokens: int = 1) -> RateLimitResult:
        with self._lock:
            self._refill()
            
            if self._tokens >= tokens:
                self._tokens -= tokens
                return RateLimitResult(
                    allowed=True,
                    remaining=int(self._tokens),
                    coherence=self.coherence,
                    pressure=1.0 - (self._tokens / self._capacity)
                )
            else:
                # Calculate wait time
                deficit = tokens - self._tokens
                wait_time = deficit / self._rate
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    retry_after=wait_time,
                    reset_at=datetime.now() + timedelta(seconds=wait_time),
                    coherence=self.coherence,
                    pressure=1.0
                )
                
    def reset(self) -> None:
        with self._lock:
            self._tokens = self._capacity
            self._last_refill = time.monotonic()
            
    @property
    def coherence(self) -> float:
        """Ψ based on bucket fill level."""
        return self._tokens / self._capacity


# ═══════════════════════════════════════════════════════════
# SLIDING WINDOW
# ═══════════════════════════════════════════════════════════

class SlidingWindow(RateLimitAlgorithm):
    """
    Sliding window rate limiter.
    
    Tracks requests in a time window that slides with current time.
    More precise than fixed windows, prevents edge bursts.
    
    Rose Glass interpretation:
    - Window history represents accumulated wisdom (ρ)
    - Smooth limiting maintains temporal coherence (τ)
    """
    
    def __init__(
        self,
        limit: int,           # Max requests in window
        window_seconds: float  # Window size in seconds
    ):
        self._limit = limit
        self._window = window_seconds
        self._requests: list[float] = []  # Timestamps
        self._lock = threading.Lock()
        
    def _prune_old(self, now: float) -> None:
        """Remove requests outside current window."""
        cutoff = now - self._window
        self._requests = [t for t in self._requests if t > cutoff]
        
    def acquire(self, tokens: int = 1) -> RateLimitResult:
        with self._lock:
            now = time.monotonic()
            self._prune_old(now)
            
            if len(self._requests) + tokens <= self._limit:
                # Add request timestamps
                for _ in range(tokens):
                    self._requests.append(now)
                return RateLimitResult(
                    allowed=True,
                    remaining=self._limit - len(self._requests),
                    coherence=self.coherence,
                    pressure=len(self._requests) / self._limit
                )
            else:
                # Calculate when oldest request exits window
                if self._requests:
                    oldest = min(self._requests)
                    wait_time = (oldest + self._window) - now
                else:
                    wait_time = 0
                    
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    retry_after=max(0, wait_time),
                    reset_at=datetime.now() + timedelta(seconds=wait_time),
                    coherence=self.coherence,
                    pressure=1.0
                )
                
    def reset(self) -> None:
        with self._lock:
            self._requests.clear()
            
    @property
    def coherence(self) -> float:
        """Ψ based on window utilization."""
        return 1.0 - (len(self._requests) / self._limit)


# ═══════════════════════════════════════════════════════════
# FIXED WINDOW
# ═══════════════════════════════════════════════════════════

class FixedWindow(RateLimitAlgorithm):
    """
    Fixed window rate limiter.
    
    Simple counter that resets at fixed intervals.
    Less precise but very efficient.
    
    Rose Glass note:
    - Can have edge effects (burst at window boundaries)
    - Use sliding window for smoother coherence
    """
    
    def __init__(
        self,
        limit: int,
        window_seconds: float
    ):
        self._limit = limit
        self._window = window_seconds
        self._count = 0
        self._window_start = time.monotonic()
        self._lock = threading.Lock()
        
    def _check_window(self, now: float) -> None:
        """Reset if window expired."""
        if now - self._window_start >= self._window:
            self._count = 0
            self._window_start = now
            
    def acquire(self, tokens: int = 1) -> RateLimitResult:
        with self._lock:
            now = time.monotonic()
            self._check_window(now)
            
            if self._count + tokens <= self._limit:
                self._count += tokens
                return RateLimitResult(
                    allowed=True,
                    remaining=self._limit - self._count,
                    coherence=self.coherence,
                    pressure=self._count / self._limit
                )
            else:
                wait_time = (self._window_start + self._window) - now
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    retry_after=max(0, wait_time),
                    reset_at=datetime.now() + timedelta(seconds=wait_time),
                    coherence=self.coherence,
                    pressure=1.0
                )
                
    def reset(self) -> None:
        with self._lock:
            self._count = 0
            self._window_start = time.monotonic()
            
    @property
    def coherence(self) -> float:
        return 1.0 - (self._count / self._limit)


# ═══════════════════════════════════════════════════════════
# UNIFIED LIMITER
# ═══════════════════════════════════════════════════════════

class Limiter:
    """
    Unified rate limiter with multiple algorithm support.
    
    Rose Glass enhanced with coherence tracking and
    adaptive behavior based on system state.
    """
    
    def __init__(
        self,
        algorithm: RateLimitAlgorithm,
        blocking: bool = True,
        max_wait: Optional[float] = None,
        on_limit: Optional[Callable[[RateLimitResult], None]] = None
    ):
        """
        Args:
            algorithm: Rate limiting algorithm to use
            blocking: Wait when limited vs raise immediately
            max_wait: Maximum seconds to wait if blocking
            on_limit: Callback when rate limited
        """
        self._algorithm = algorithm
        self._blocking = blocking
        self._max_wait = max_wait
        self._on_limit = on_limit
        
    def acquire(self, tokens: int = 1) -> RateLimitResult:
        """
        Acquire tokens, potentially blocking.
        
        Args:
            tokens: Number of tokens to acquire
            
        Returns:
            RateLimitResult with status
            
        Raises:
            RateLimitExceeded: When non-blocking and limited
        """
        result = self._algorithm.acquire(tokens)
        
        if result.allowed:
            return result
            
        # Rate limited
        if self._on_limit:
            self._on_limit(result)
            
        if not self._blocking:
            raise RateLimitExceeded(result)
            
        # Block and retry
        wait_time = result.retry_after or 0
        if self._max_wait is not None:
            wait_time = min(wait_time, self._max_wait)
            
        if wait_time > 0:
            time.sleep(wait_time)
            
        return self._algorithm.acquire(tokens)
        
    async def acquire_async(self, tokens: int = 1) -> RateLimitResult:
        """Async variant of acquire."""
        result = self._algorithm.acquire(tokens)
        
        if result.allowed:
            return result
            
        if self._on_limit:
            self._on_limit(result)
            
        if not self._blocking:
            raise RateLimitExceeded(result)
            
        wait_time = result.retry_after or 0
        if self._max_wait is not None:
            wait_time = min(wait_time, self._max_wait)
            
        if wait_time > 0:
            await asyncio.sleep(wait_time)
            
        return self._algorithm.acquire(tokens)
        
    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """Use as decorator."""
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            self.acquire()
            return func(*args, **kwargs)
        return wrapper
        
    @property
    def coherence(self) -> float:
        """Current coherence from algorithm."""
        return self._algorithm.coherence
        
    def reset(self) -> None:
        """Reset limiter state."""
        self._algorithm.reset()


# ═══════════════════════════════════════════════════════════
# CONVENIENCE FACTORIES
# ═══════════════════════════════════════════════════════════

def rate_limit(
    rate: float,
    per_seconds: float = 1.0,
    burst: Optional[int] = None,
    algorithm: str = 'token_bucket'
) -> Limiter:
    """
    Create a rate limiter with simple parameters.
    
    Args:
        rate: Requests allowed per time period
        per_seconds: Time period in seconds
        burst: Burst capacity (token bucket only)
        algorithm: 'token_bucket', 'sliding_window', or 'fixed_window'
        
    Returns:
        Configured Limiter instance
        
    Example:
        limiter = rate_limit(10, per_seconds=60)  # 10 per minute
        
        @limiter
        def api_call():
            ...
    """
    tokens_per_second = rate / per_seconds
    capacity = burst if burst else int(rate)
    
    if algorithm == 'token_bucket':
        algo = TokenBucket(rate=tokens_per_second, capacity=capacity)
    elif algorithm == 'sliding_window':
        algo = SlidingWindow(limit=int(rate), window_seconds=per_seconds)
    elif algorithm == 'fixed_window':
        algo = FixedWindow(limit=int(rate), window_seconds=per_seconds)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")
        
    return Limiter(algo)
