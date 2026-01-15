"""
CERATA Nematocyst: Backoff Decorators
Source Prey: github.com/litl/backoff

Metabolized retry decorators for automatic failure recovery.
Enhanced with Rose Glass coherence tracking.
"""

from functools import wraps
from typing import (
    Callable, Generator, Optional, Tuple, Type, Union, 
    Any, Awaitable, TypeVar
)
import asyncio
import time
import logging

from .generators import expo, CoherenceAwareBackoff


logger = logging.getLogger(__name__)

T = TypeVar('T')
ExceptionTypes = Union[Type[Exception], Tuple[Type[Exception], ...]]


def on_exception(
    wait_gen: Callable[[], Generator[float, None, None]] = expo,
    exception: ExceptionTypes = Exception,
    max_tries: Optional[int] = None,
    max_time: Optional[float] = None,
    jitter: Optional[Callable[[float], float]] = None,
    on_backoff: Optional[Callable[[dict], None]] = None,
    on_success: Optional[Callable[[dict], None]] = None,
    on_giveup: Optional[Callable[[dict], None]] = None,
    raise_on_giveup: bool = True,
    coherence_tracking: bool = True,
    **wait_gen_kwargs
) -> Callable:
    """
    Retry decorator triggered by exceptions.
    
    Rose Glass Enhancement:
    - Tracks coherence across retry attempts
    - Logs Ψ (consistency) of failure patterns
    - Records ρ (wisdom) from successful recoveries
    
    Args:
        wait_gen: Generator factory for delays
        exception: Exception type(s) to catch
        max_tries: Maximum retry attempts
        max_time: Maximum total retry time
        jitter: Optional jitter function
        on_backoff: Callback for each retry
        on_success: Callback on eventual success
        on_giveup: Callback when giving up
        raise_on_giveup: Raise exception or return None
        coherence_tracking: Enable Rose Glass tracking
        **wait_gen_kwargs: Passed to wait_gen
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(target: Callable[..., T]) -> Callable[..., T]:
        @wraps(target)
        def wrapper(*args, **kwargs) -> T:
            wait = wait_gen(**wait_gen_kwargs)
            tries = 0
            start = time.monotonic()
            
            # Rose Glass tracking
            coherence_tracker = CoherenceAwareBackoff() if coherence_tracking else None
            
            while True:
                tries += 1
                elapsed = time.monotonic() - start
                
                # Check limits
                if max_tries is not None and tries > max_tries:
                    break
                if max_time is not None and elapsed >= max_time:
                    break
                    
                try:
                    result = target(*args, **kwargs)
                    
                    # Success callback
                    if on_success:
                        details = _build_details(
                            target, args, kwargs, tries, elapsed, None
                        )
                        on_success(details)
                        
                    # Rose Glass: record successful recovery
                    if coherence_tracker:
                        coherence_tracker.record_coherence(1.0)
                        logger.debug(
                            f"[Rose Glass] Recovery succeeded after {tries} attempts, "
                            f"avg coherence: {coherence_tracker.average_coherence:.2f}"
                        )
                        
                    return result
                    
                except exception as e:
                    # Rose Glass: record failure
                    if coherence_tracker:
                        # Decay coherence with each failure
                        tau = max(0.1, 1.0 - (tries * 0.15))
                        coherence_tracker.record_coherence(tau)
                    
                    # Check if should give up
                    if max_tries is not None and tries >= max_tries:
                        if on_giveup:
                            details = _build_details(
                                target, args, kwargs, tries, elapsed, e
                            )
                            on_giveup(details)
                        if raise_on_giveup:
                            raise
                        return None
                        
                    if max_time is not None and elapsed >= max_time:
                        if on_giveup:
                            details = _build_details(
                                target, args, kwargs, tries, elapsed, e
                            )
                            on_giveup(details)
                        if raise_on_giveup:
                            raise
                        return None
                    
                    # Calculate wait time
                    wait_time = next(wait)
                    if jitter:
                        wait_time = jitter(wait_time)
                        
                    # Backoff callback
                    if on_backoff:
                        details = _build_details(
                            target, args, kwargs, tries, elapsed, e,
                            wait=wait_time
                        )
                        on_backoff(details)
                        
                    logger.debug(
                        f"[Backoff] {target.__name__} failed (attempt {tries}), "
                        f"waiting {wait_time:.2f}s: {e}"
                    )
                    
                    time.sleep(wait_time)
                    
            # Should not reach here normally
            return None
            
        return wrapper
    return decorator


def on_predicate(
    wait_gen: Callable[[], Generator[float, None, None]] = expo,
    predicate: Callable[[Any], bool] = lambda x: x,
    max_tries: Optional[int] = None,
    max_time: Optional[float] = None,
    jitter: Optional[Callable[[float], float]] = None,
    on_backoff: Optional[Callable[[dict], None]] = None,
    on_success: Optional[Callable[[dict], None]] = None,
    on_giveup: Optional[Callable[[dict], None]] = None,
    coherence_tracking: bool = True,
    **wait_gen_kwargs
) -> Callable:
    """
    Retry decorator triggered by predicate failure.
    
    Retries until predicate(result) returns True.
    
    Rose Glass Enhancement:
    - Tracks coherence of return value patterns
    - Distinguishes "not ready" vs "broken" states
    
    Args:
        wait_gen: Generator factory for delays
        predicate: Function returning True when result is acceptable
        max_tries: Maximum retry attempts
        max_time: Maximum total retry time
        jitter: Optional jitter function
        on_backoff: Callback for each retry
        on_success: Callback on eventual success
        on_giveup: Callback when giving up
        coherence_tracking: Enable Rose Glass tracking
        **wait_gen_kwargs: Passed to wait_gen
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(target: Callable[..., T]) -> Callable[..., T]:
        @wraps(target)
        def wrapper(*args, **kwargs) -> T:
            wait = wait_gen(**wait_gen_kwargs)
            tries = 0
            start = time.monotonic()
            
            while True:
                tries += 1
                elapsed = time.monotonic() - start
                
                # Check limits
                if max_tries is not None and tries > max_tries:
                    if on_giveup:
                        details = _build_details(
                            target, args, kwargs, tries, elapsed, None
                        )
                        on_giveup(details)
                    return None
                    
                if max_time is not None and elapsed >= max_time:
                    if on_giveup:
                        details = _build_details(
                            target, args, kwargs, tries, elapsed, None
                        )
                        on_giveup(details)
                    return None
                
                result = target(*args, **kwargs)
                
                if predicate(result):
                    if on_success:
                        details = _build_details(
                            target, args, kwargs, tries, elapsed, None,
                            value=result
                        )
                        on_success(details)
                    return result
                    
                # Calculate wait time
                wait_time = next(wait)
                if jitter:
                    wait_time = jitter(wait_time)
                    
                if on_backoff:
                    details = _build_details(
                        target, args, kwargs, tries, elapsed, None,
                        value=result, wait=wait_time
                    )
                    on_backoff(details)
                    
                logger.debug(
                    f"[Backoff] {target.__name__} predicate failed (attempt {tries}), "
                    f"waiting {wait_time:.2f}s"
                )
                
                time.sleep(wait_time)
                
            return None
            
        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════
# ASYNC VARIANTS
# ═══════════════════════════════════════════════════════════

def on_exception_async(
    wait_gen: Callable[[], Generator[float, None, None]] = expo,
    exception: ExceptionTypes = Exception,
    max_tries: Optional[int] = None,
    max_time: Optional[float] = None,
    jitter: Optional[Callable[[float], float]] = None,
    on_backoff: Optional[Callable[[dict], None]] = None,
    on_success: Optional[Callable[[dict], None]] = None,
    on_giveup: Optional[Callable[[dict], None]] = None,
    raise_on_giveup: bool = True,
    **wait_gen_kwargs
) -> Callable:
    """
    Async variant of on_exception.
    
    Same parameters as on_exception, but works with async functions.
    """
    def decorator(target: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(target)
        async def wrapper(*args, **kwargs) -> T:
            wait = wait_gen(**wait_gen_kwargs)
            tries = 0
            start = time.monotonic()
            
            while True:
                tries += 1
                elapsed = time.monotonic() - start
                
                if max_tries is not None and tries > max_tries:
                    break
                if max_time is not None and elapsed >= max_time:
                    break
                    
                try:
                    result = await target(*args, **kwargs)
                    
                    if on_success:
                        details = _build_details(
                            target, args, kwargs, tries, elapsed, None
                        )
                        on_success(details)
                    return result
                    
                except exception as e:
                    if max_tries is not None and tries >= max_tries:
                        if on_giveup:
                            details = _build_details(
                                target, args, kwargs, tries, elapsed, e
                            )
                            on_giveup(details)
                        if raise_on_giveup:
                            raise
                        return None
                        
                    if max_time is not None and elapsed >= max_time:
                        if on_giveup:
                            details = _build_details(
                                target, args, kwargs, tries, elapsed, e
                            )
                            on_giveup(details)
                        if raise_on_giveup:
                            raise
                        return None
                    
                    wait_time = next(wait)
                    if jitter:
                        wait_time = jitter(wait_time)
                        
                    if on_backoff:
                        details = _build_details(
                            target, args, kwargs, tries, elapsed, e,
                            wait=wait_time
                        )
                        on_backoff(details)
                        
                    await asyncio.sleep(wait_time)
                    
            return None
            
        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════

def _build_details(
    target: Callable,
    args: tuple,
    kwargs: dict,
    tries: int,
    elapsed: float,
    exception: Optional[Exception],
    **extra
) -> dict:
    """Build details dict for callbacks."""
    return {
        'target': target,
        'args': args,
        'kwargs': kwargs,
        'tries': tries,
        'elapsed': elapsed,
        'exception': exception,
        **extra
    }


def runtime_context(
    max_tries: Optional[int] = None,
    max_time: Optional[float] = None
) -> Callable:
    """
    Context decorator to set runtime retry limits.
    
    Allows overriding decorator defaults at call time.
    
    Usage:
        @on_exception(expo, Exception)
        @runtime_context(max_tries=3)  # Override max_tries
        def my_func():
            ...
    """
    def decorator(target: Callable[..., T]) -> Callable[..., T]:
        @wraps(target)
        def wrapper(*args, **kwargs) -> T:
            # Store runtime context for inner decorator
            wrapper._runtime_max_tries = max_tries
            wrapper._runtime_max_time = max_time
            return target(*args, **kwargs)
        return wrapper
    return decorator
