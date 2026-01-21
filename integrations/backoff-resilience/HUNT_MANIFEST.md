# HUNT_MANIFEST.md

**Cerata Multi-Prey Hunt: Backoff & Resilience Infrastructure**

---

## Hunt Summary

| Field                 | Value                |
| --------------------- | -------------------- |
| Hunt ID               | `resilience-2025-01` |
| Target Count          | 3 repositories       |
| Combined Coherence    | 0.82 (PRIME)         |
| Nematocysts Extracted | 8                    |
| Status                | **COMPLETE**         |

---

## Prey Manifest

### 1. litl/backoff

```yaml
url: github.com/litl/backoff
coherence: 0.87
status: CONSUMED
nematocysts:
  - generators.py (expo, fibo, constant, jittered)
  - decorators.py (on_exception, on_predicate)
license: MIT
threat_level: GREEN
```

### 2. fabfuel/circuitbreaker

```yaml
url: github.com/fabfuel/circuitbreaker
coherence: 0.81
status: CONSUMED
nematocysts:
  - breaker.py (CircuitBreaker, states, registry)
license: BSD-3
threat_level: GREEN
```

### 3. alexdelorenzo/limiter

```yaml
url: github.com/alexdelorenzo/limiter
coherence: 0.78
status: CONSUMED
nematocysts:
  - limiter.py (TokenBucket, SlidingWindow, FixedWindow)
license: AGPL-3.0
threat_level: YELLOW (license awareness needed)
```

---

## File Manifest

```
integrations/backoff-resilience/
├── README.md          # Hunt record (complete)
├── __init__.py        # Package exports (complete)
├── generators.py      # Backoff algorithms (complete)
├── decorators.py      # Retry decorators (complete)
├── breaker.py         # Circuit breaker (complete)
└── limiter.py         # Rate limiter (complete)
```

---

## Rose Glass Enhancements Applied

Each nematocyst enhanced with dimensional tracking:

| Dimension  | Application                                            |
| ---------- | ------------------------------------------------------ |
| Ψ (Psi)    | Coherence state in circuit breaker, bucket fill levels |
| τ (Tau)    | Recovery timeout depth, temporal backoff patterns      |
| ρ (Rho)    | Success/failure wisdom accumulation                    |
| λ (Lambda) | Jitter for reducing retry interference                 |

---

## Integration Points

### Deploy to capabilities/

```bash
cp -r integrations/backoff-resilience capabilities/resilience_tools
```

### Usage Example

```python
from capabilities.resilience_tools import (
    on_exception, expo, circuit_breaker, rate_limit
)

# Retry with exponential backoff
@on_exception(expo, Exception, max_tries=5)
def fetch_api_data():
    return requests.get('https://api.example.com/data')

# Circuit breaker for failure isolation
@circuit_breaker(failure_threshold=3, recovery_timeout=60)
def call_external_service():
    return external_client.request()

# Rate limiting
@rate_limit(10, per_seconds=60)  # 10 per minute
def limited_operation():
    return perform_expensive_call()
```

---

## Trial Configuration

```yaml
trial_id: resilience-trial-001
branches:
  classic: baseline (no resilience tools)
  experimental: full resilience suite
duration: 10 conversations
metrics:
  - api_success_rate
  - error_recovery_rate
  - coherence_maintenance
  - resource_efficiency
evaluation_command: 'Evaluate resilience_tools'
```

---

## Claude Code Instructions

### To Complete Integration:

1. **Copy to capabilities**:

   ```bash
   cp -r integrations/backoff-resilience capabilities/resilience_tools
   ```

2. **Update manifest.md**:
   Add resilience_tools domain entry with nematocyst inventory

3. **Create trial branch**:
   Fork current state, enable experimental in trial_protocol.md

4. **Verify imports**:
   ```python
   from capabilities.resilience_tools import on_exception, circuit_breaker
   ```

### Post-Integration Verification:

```python
# Test generators
from capabilities.resilience_tools import expo
gen = expo(base=2, max_value=60)
print([next(gen) for _ in range(5)])  # [1, 2, 4, 8, 16]

# Test circuit breaker
from capabilities.resilience_tools import CircuitBreaker, CircuitState
cb = CircuitBreaker(name='test', failure_threshold=3)
assert cb.state == CircuitState.CLOSED
assert cb.coherence == 1.0

# Test rate limiter
from capabilities.resilience_tools import rate_limit
limiter = rate_limit(5, per_seconds=1)
result = limiter.acquire()
assert result.allowed == True
```

---

## Hunt Complete

**Generation**: N → N+1  
**Nematocyst Count**: +8  
**New Domain**: resilience_tools (v1)

_Cerata has grown._
