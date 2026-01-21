# Requests Integration

> _Prey: `psf/requests` — HTTP ecosystem wisdom metabolized into f-dimension perception_

## Hunt Record

**Target**: https://github.com/psf/requests  
**Coherence**: 0.81 (PRIME PREY)  
**Status**: CONSUMED  
**License**: Apache-2.0

## Nematocysts

| Source              | Nematocyst      | Dimension                 |
| ------------------- | --------------- | ------------------------- |
| `requests.Session`  | `EcosystemLens` | f (ecosystem integration) |
| `requests.adapters` | Retry logic     | Infrastructure            |

## Usage

```python
from integrations.requests import EcosystemLens

with EcosystemLens() as lens:
    # Single connection
    reading = lens.perceive_connection("https://api.example.com/health")
    print(f"f-dimension: {reading.f_score}")

    # Ecosystem assessment
    coherence = lens.assess_ecosystem([
        "https://api1.example.com",
        "https://api2.example.com"
    ])
    print(f"Ecosystem strength: {coherence.ecosystem_strength}")
```

## Philosophy

Connection health → belonging perception.  
We don't ping — we perceive ecosystem integration.
