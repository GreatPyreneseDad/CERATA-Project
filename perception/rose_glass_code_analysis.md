# Rose Glass for Code Repositories

**Perception Layer: How Cerata Sees Prey**

---

## The Six Dimensions Applied to Code

### Ψ (Psi) — Internal Consistency

**What it measures**: Architectural coherence, design pattern consistency, coupling/cohesion

**Code indicators**:
- **High Ψ (0.7-1.0)**: Clean separation of concerns, consistent naming, minimal circular dependencies
- **Medium Ψ (0.4-0.7)**: Some inconsistencies, mixed patterns, moderate coupling
- **Low Ψ (0.0-0.4)**: God objects, spaghetti code, fragmented architecture

**Scan checklist**:
```
□ Single Responsibility: Do modules/classes do one thing?
□ Naming consistency: CamelCase vs snake_case mixtures?
□ Pattern coherence: MVC everywhere vs mixed paradigms?
□ Dependency graph: Clear hierarchy or circular mess?
□ File organization: Logical structure or chaos?
```

**Example analysis**:
```
Repository: flask-restful
Ψ: 0.85

Evidence:
├── Consistent RESTful resource pattern throughout
├── Clear separation: resources, marshalling, errors
├── No circular imports (verified via import graph)
├── Naming: snake_case for functions, CamelCase for classes
└── Minimal coupling between resource modules

Conclusion: High internal consistency. Easy to digest.
```

---

### ρ (Rho) — Accumulated Wisdom

**What it measures**: Battle-testing, refinement through use, lessons embedded in code

**Code indicators**:
- **High ρ (0.7-1.0)**: Years of commits, many contributors, evolved error handling
- **Medium ρ (0.4-0.7)**: Some history, moderate contributor base, basic robustness
- **Low ρ (0.0-0.4)**: New project, single author, naive implementations

**Scan checklist**:
```
□ Commit history: How many commits? Over what time span?
□ Contributor diversity: 1 author or community-refined?
□ Issue resolution: Are bugs fixed or ignored?
□ Error handling: Try/catch everywhere or naive?
□ Edge cases: Comments about "weird bug from 2019"?
□ Test coverage: Evidence of lessons learned?
```

**Example analysis**:
```
Repository: requests library
ρ: 0.93

Evidence:
├── 5,234 commits spanning 12 years
├── 719 contributors (community-refined)
├── Error handling covers TLS, redirects, timeouts, encoding
├── Comments reference specific CVEs, bug reports
├── 94% test coverage with edge case suites
└── Graceful degradation patterns throughout

Conclusion: Extremely battle-tested. Patterns worth stealing.
```

---

### q (Q) — Activation State

**What it measures**: Maintenance activity, development momentum, living vs fossil

**Code indicators**:
- **High q (0.7-1.0)**: Active development, frequent commits, responsive maintainers
- **Medium q (0.4-0.7)**: Maintenance mode, occasional updates, stable
- **Low q (0.0-0.4)**: Dormant, deprecated, archived

**Scan checklist**:
```
□ Last commit: Within 1 month? 6 months? Years?
□ Open issues: Being addressed or ignored?
□ PR activity: Merged recently or stale queue?
□ Release cadence: Regular or abandoned?
□ Dependency updates: Keeping up or frozen?
```

**Example analysis**:
```
Repository: beautifulsoup4
q: 0.52

Evidence:
├── Last commit: 2 months ago
├── Maintenance mode (stated in README)
├── No new features, only bug fixes
├── Dependency updates: Current with Python 3.11
├── Issue response time: ~2 weeks
└── Stable, reliable, not innovating

Conclusion: Low q but HIGH value. Fossil = proven patterns.
```

---

### f (F) — Social Belonging

**What it measures**: Ecosystem fit, dependency health, community integration

**Code indicators**:
- **High f (0.7-1.0)**: Standard dependencies, follows community conventions, pluggable
- **Medium f (0.4-0.7)**: Some unusual deps, mostly conventional
- **Low f (0.0-0.4)**: Exotic dependencies, non-standard patterns, island

**Scan checklist**:
```
□ Dependency count: Lean or bloated?
□ Dependency health: All maintained or dead projects?
□ Conventions: Follows PEP 8 / Rust style / Go idioms?
□ Interoperability: Can it plug into my existing body?
□ License: Compatible with my needs?
□ Community: Used by others or isolated?
```

**Example analysis**:
```
Repository: fastapi
f: 0.88

Evidence:
├── Dependencies: pydantic, starlette (both healthy)
├── Follows ASGI standard (high interoperability)
├── Pythonic idioms throughout (PEP 8, type hints)
├── Used by 500+ GitHub projects (community adoption)
├── MIT License (compatible)
└── Integrates with pytest, mypy, black (tooling fit)

Conclusion: Strong ecosystem belonging. Integrates cleanly.
```

---

### τ (Tau) — Temporal Survival

**What it measures**: Has it weathered breaking changes? Survived ecosystem shifts?

**Code indicators**:
- **High τ (0.7-1.0)**: Survived Python 2→3, major dep updates, paradigm shifts
- **Medium τ (0.4-0.7)**: Some adaptation to changes, moderate resilience
- **Low τ (0.0-0.4)**: Frozen in time, no adaptation, fragile

**Scan checklist**:
```
□ Breaking changes: Python 2→3? Async refactor? Type hints added?
□ Dependency updates: Kept pace or frozen?
□ API stability: Breaking changes or backward-compatible?
□ Migration guides: Evidence of major refactors?
□ Deprecation warnings: Proactive or reactive?
```

**Example analysis**:
```
Repository: sqlalchemy
τ: 0.91

Evidence:
├── Survived: Python 2→3 migration
├── Survived: Async/await introduction (added async support)
├── Survived: Type hints era (full typing support)
├── Survived: Multiple major versions (1.x → 2.x)
├── Migration guides for every breaking change
└── Still dominant after 18 years

Conclusion: Extremely resilient. Patterns tested by time.
```

---

### λ (Lambda) — Lens Interference

**What it measures**: How much must Cerata adapt this code to integrate it?

**Code indicators**:
- **Low λ (0.0-0.3)**: Fits naturally, minimal adaptation needed
- **Medium λ (0.3-0.6)**: Some style/API differences, moderate adaptation
- **High λ (0.6-1.0)**: Major refactoring needed, heavy digestion required

**Scan checklist**:
```
□ Code style: Matches my existing body or wildly different?
□ API patterns: Familiar paradigms or alien?
□ Dependencies: Compatible with my stack or conflicts?
□ Assumptions: Makes assumptions about environment I don't share?
□ Extraction difficulty: Clean functions or tightly coupled?
```

**Example analysis**:
```
Repository: retry library
λ: 0.28

Evidence:
├── Style: PEP 8 compliant (matches my body)
├── Pattern: Decorator-based (familiar paradigm)
├── Dependencies: Zero (no conflicts)
├── Functions: Pure, easily extractable
└── No environment assumptions (pure Python)

Conclusion: Low λ. Minimal adaptation needed. Prime prey.
```

---

## Composite Scoring

**Overall Coherence Score** = weighted average across dimensions

```python
def calculate_coherence(Ψ, ρ, q, f, τ, λ):
    """
    Calculate overall prey fitness.

    Weights:
    - Ψ (consistency): 0.25 — most important for digestion
    - ρ (wisdom): 0.20 — want proven patterns
    - q (activity): 0.10 — low q is okay if stable
    - f (belonging): 0.15 — ecosystem fit matters
    - τ (survival): 0.15 — resilience indicates quality
    - λ (interference): 0.15 — low λ means easy integration

    λ is inverted: low λ = good, so we use (1 - λ)
    """
    return (
        0.25 * Ψ +
        0.20 * ρ +
        0.10 * q +
        0.15 * f +
        0.15 * τ +
        0.15 * (1 - λ)
    )
```

**Prey viability thresholds**:
- **0.7-1.0**: Prime prey. Immediate hunt authorized.
- **0.5-0.7**: Viable prey. Hunt with caution.
- **0.3-0.5**: Marginal prey. Only extract specific nematocysts.
- **0.0-0.3**: Unfit prey. Reject. Do not consume.

---

## Threat Assessment

Before metabolism, check for **poisonous prey**:

```
SECURITY SCAN:
□ License: Viral (GPL)? Incompatible? Missing?
□ Dependencies: Known vulnerabilities?
□ Code patterns: Eval(), exec(), unsafe deserialization?
□ Network calls: Phoning home? Telemetry without consent?
□ Obfuscation: Intentionally obscured code?
□ Supply chain: Compromised dependencies?

THREAT LEVELS:
├── GREEN: Safe to consume
├── YELLOW: Proceed with modifications (strip telemetry, etc.)
└── RED: Toxic. Reject.
```

---

## Example: Complete Repository Analysis

```
HUNT: github.com/psf/requests

ROSE GLASS PERCEPTION:

Ψ (Internal Consistency): 0.87
├── Clean API surface (get, post, put, delete, etc.)
├── Consistent error hierarchy
├── Separation: core, adapters, exceptions, utils
└── No circular dependencies

ρ (Accumulated Wisdom): 0.93
├── 12 years, 5,234 commits, 719 contributors
├── Handles TLS, redirects, cookies, auth, streaming
├── Error messages refined through issues
└── 94% test coverage with edge cases

q (Activation): 0.71
├── Active maintenance (last commit 2 weeks ago)
├── Python 3.12 support added
├── Security patches within days
└── Regular releases (v2.31.0 current)

f (Social Belonging): 0.91
├── Standard library-like status in Python ecosystem
├── Zero exotic dependencies (urllib3, charset_normalizer)
├── Follows PEP 8, has type stubs
└── Used by 2M+ projects

τ (Temporal Survival): 0.89
├── Survived Python 2→3 migration seamlessly
├── Adapted to async era (stayed sync, niche preserved)
├── Maintained API compatibility across versions
└── Dominant for HTTP for over a decade

λ (Lens Interference): 0.31
├── Pythonic style (matches my body)
├── Simple function-based API (easy to extract)
├── Adapter pattern allows capability injection
└── Minimal coupling within modules

OVERALL COHERENCE: 0.81 (PRIME PREY)

THREAT ASSESSMENT:
├── License: Apache 2.0 (compatible)
├── Security: No known CVEs in current version
├── Supply chain: urllib3 (maintained), charset_normalizer (safe)
└── THREAT LEVEL: GREEN

NEMATOCYST CANDIDATES:
1. /requests/adapters.py → HTTPAdapter with retry logic
2. /requests/sessions.py → Session management pattern
3. /requests/exceptions.py → Exception hierarchy
4. /requests/auth.py → Authentication handlers

RECOMMENDATION: Prime prey. High coherence, battle-tested, safe.
Prioritize: HTTPAdapter (retry logic), auth handlers.

Authorize metabolism?
```

---

## Integration with Graveyard

Failed hunts teach perception. When a consumed nematocyst causes a trial loss, the pattern is recorded:

```markdown
Example: If retry logic from repo X caused errors...

Perception adjustment:
├── Future prey with similar retry patterns: λ score +0.2
├── Check for: async compatibility if Cerata body is async
├── Warning flag: "retry pattern incompatible with async context"
```

The graveyard **trains the perception layer** to avoid future bad hunts.

---

**The habitat changes everything. I see code as prey.**
