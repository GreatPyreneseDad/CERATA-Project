# Cerata Examples

**Real-world hunt scenarios and outcomes**

---

## Example 1: Hunting Retry Logic

### Initial State
```
Generation: 0
Capabilities: None
Goal: Add robust retry logic for API calls
```

### Hunt Command
```
You: Hunt github.com/invl/retry
```

### Perception Analysis
```
SCANNING: github.com/invl/retry

COHERENCE ANALYSIS:
├── Ψ: 0.88 — Clean decorator pattern, minimal coupling
├── ρ: 0.71 — 5 years, 200+ stars, proven in production
├── q: 0.42 — Maintenance mode (stable, not actively developed)
├── f: 0.82 — Pure Python, no exotic deps
├── τ: 0.79 — Survived Python 2→3, async additions
└── λ: 0.24 — Very low adaptation needed

OVERALL COHERENCE: 0.76 (VIABLE PREY)

NEMATOCYST CANDIDATES:
1. retry() decorator — exponential backoff with jitter
2. retry_call() — function wrapper variant
3. RetryError exception — custom error type

RECOMMENDATION: Good prey. Simple, battle-tested, Pythonic.
```

### Consumption
```
You: Consume retry decorator and RetryError

INGESTION: retry.py

DIGESTION:
├── retry() decorator → Pure function, 0 deps
├── RetryError class → Exception type
└── _calculate_delay() → Utility (internal)

INTEGRATION:
├── Domain: reliability_tools (NEW)
├── Nematocysts: 2 (retry decorator, RetryError)
└── Integration point: /capabilities/reliability_tools/

TRIAL CREATED:
├── CLASSIC: None (new domain)
└── EXPERIMENTAL: reliability_tools v1

Trial duration: 5 conversations
```

### Usage During Trial
```
[Conversation 1]
You: Make an API call to https://api.example.com with retry logic

Cerata: [Uses experimental branch]
        [Wraps call with @retry decorator]
        SUCCESS - retrieved data after 2 retries

[Conversation 2]
You: Fetch data from flaky endpoint

Cerata: [Uses experimental branch]
        [Applies retry with exponential backoff]
        SUCCESS - completed after 1 retry

[... 3 more uses ...]
```

### Evaluation
```
You: Evaluate reliability_tools

TRIAL EVALUATION: reliability_tools

CLASSIC BRANCH: N/A (new domain)

EXPERIMENTAL BRANCH (v1):
├── Invocations: 5
├── Successes: 5 (100%)
├── Failures: 0
├── New nematocyst uses: retry decorator 5x
├── Coherence drift: +0.01 (slight improvement)
└── FITNESS: 0.94

VERDICT: EXPERIMENTAL PROMOTED (no competition)

Generation: 0 → 1
Nematocyst count: 0 → 2

Cerata has grown.
```

---

## Example 2: Failed Integration

### Hunt Command
```
You: Hunt github.com/someone/complex-parser
```

### Perception Analysis
```
SCANNING: github.com/someone/complex-parser

COHERENCE ANALYSIS:
├── Ψ: 0.61 — Mixed paradigms, some coupling
├── ρ: 0.44 — 1 year old, single author
├── q: 0.83 — Active development (lots of changes)
├── f: 0.58 — Some unusual dependencies
├── τ: 0.32 — Young, hasn't weathered changes
└── λ: 0.67 — HIGH adaptation needed

OVERALL COHERENCE: 0.52 (MARGINAL PREY)

NEMATOCYST CANDIDATES:
1. parse_complex() — AST manipulation
2. TokenStream class — Stateful tokenizer
3. validate() — Syntax checker

RECOMMENDATION: Marginal prey. High λ suggests difficult integration.
Proceed with caution. Extract only parse_complex().
```

### Consumption (Against Recommendation)
```
You: Consume all three functions

[Cerata warns but proceeds]

INGESTION: parser.py, tokenizer.py, validator.py

DIGESTION:
├── parse_complex() — Moderate coupling
├── TokenStream class — Stateful, hard to extract
└── validate() — Depends on TokenStream

INTEGRATION:
├── Domain: code_tools
├── Attempted nematocysts: 3
└── WARNING: High coupling detected

TRIAL CREATED:
├── CLASSIC: code_tools v2
└── EXPERIMENTAL: code_tools v3 + 3 nematocysts

Trial duration: 5 conversations
```

### Usage During Trial
```
[Conversation 1]
You: Parse this Python code

Cerata: [Uses experimental branch]
        ERROR - TypeError in parse_complex()

[Conversation 2]
You: Parse this code snippet

Cerata: [Uses classic branch]
        SUCCESS - basic parser worked

[Conversation 3]
You: Parse function definitions

Cerata: [Uses experimental branch]
        ERROR - TokenStream state corruption

[... pattern continues ...]
```

### Evaluation
```
You: Evaluate code_tools

TRIAL EVALUATION: code_tools

CLASSIC BRANCH (v2):
├── Invocations: 6
├── Successes: 5 (83%)
├── Failures: 1
└── FITNESS: 0.79

EXPERIMENTAL BRANCH (v3):
├── Invocations: 6
├── Successes: 2 (33%)
├── Failures: 4
│   ├── TypeError in parse_complex() (2x)
│   ├── StateError in TokenStream (1x)
│   └── AttributeError in validate() (1x)
├── Coherence drift: -0.12 (SEVERE FRAGMENTATION)
└── FITNESS: 0.38

VERDICT: CLASSIC WINS (by large margin)

APOPTOSIS: Experimental branch v3 → graveyard

NUTRIENTS EXTRACTED:
├── Lesson: High λ (0.67) predicted integration difficulty
├── Pattern: Stateful classes (TokenStream) hard to extract
├── Warning: Tightly coupled code fragments body
└── Impact: Future hunts with λ > 0.6 require extra caution

GRAVEYARD ENTRY: /graveyard/gen3_code_tools_experimental.md

Generation: 3 (no increment - failed integration)
```

### Perception Layer Updated
```
Rose Glass adjustments:
├── Prey with λ > 0.6: Now flagged as HIGH RISK
├── Stateful classes: Extraction difficulty +0.2
└── Single-author repos <2 years: ρ score -0.1
```

---

## Example 3: Autophagy (Self-Pruning)

### Body State Before
```
Generation: 7
Active Capabilities: 3
Nematocyst Count: 14

ACTIVE CAPABILITIES:
├── code_tools (v3) — 5 nematocysts
├── api_tools (v4) — 6 nematocysts
└── text_processing (v2) — 3 nematocysts

[text_processing unused for 12 conversations]
```

### Autophagy Command
```
You: Autophagy text_processing
```

### Execution
```
AUTOPHAGY INITIATED: text_processing

Reason: Unused for 12 conversations (decay threshold)

NEMATOCYSTS DIGESTED:
├── semantic_chunking() → removed
├── embedding_cache() → removed
└── text_normalize() → removed

COHERENCE IMPACT: +0.06 (reduced complexity)

GRAVEYARD ENTRY: Autophagy event recorded
├── Cause: Decay through disuse
├── Lesson: Maintain lean body, shed unused capabilities
└── Resurrection: Possible if use case emerges

Cerata has simplified.
Generation: 7 → 8 (growth through subtraction)
Nematocyst count: 14 → 11
```

### Result
```
You: Status

CERATA BODY STATE

Generation: 8
Active Capabilities: 2 (reduced from 3)
Nematocyst Count: 11 (reduced from 14)

ACTIVE CAPABILITIES:
├── code_tools (v3) — 5 nematocysts [ACTIVE]
└── api_tools (v4) — 6 nematocysts [ACTIVE]

RECENT AUTOPHAGY:
└── text_processing v2 (conversation #89)
    └── Reason: Unused for 12 conversations

Coherence: Improved (+0.06)
```

---

## Example 4: Perceiving Non-Code

### Perception Command
```
You: Perceive the concept of using Redis for session storage
```

### Analysis
```
PERCEIVING: Redis for session storage

Ψ (Internal Consistency): 0.81
├── Concept: Clear separation (app ↔ cache)
├── Logic: Sessions = temporary data = cache-appropriate
├── Fragmentation risk: Redis failure = session loss
└── Coherence note: Requires fallback strategy

ρ (Accumulated Wisdom): 0.92
├── Pattern used by: GitHub, Stack Overflow, Twitter
├── Battle-tested: 10+ years in production at scale
├── Lessons embedded: Key expiry, persistence options, clustering
└── Known pitfalls: Memory limits, eviction policies

q (Activation): 0.88
├── Currently standard practice for session storage
├── Active tooling: redis-py, ioredis, etc.
├── High momentum in industry
└── Alternatives emerging: Valkey (Redis fork)

f (Social Belonging): 0.87
├── Fits microservices architecture well
├── Standard in cloud-native stacks
├── Well-supported by frameworks (Django, Express, etc.)
└── Integration: Straightforward with existing tools

τ (Temporal Survival): 0.83
├── Redis itself: 15 years old, still dominant
├── Has adapted: Clustering, Streams, JSON support
├── Survived: NoSQL hype cycles, new competitors
└── Longevity: Likely to persist 5+ more years

λ (Lens Interference): 0.34
├── From stateful sessions: LOW adaptation (natural fit)
├── From stateless JWT: MEDIUM adaptation (paradigm shift)
├── From database sessions: LOW adaptation (drop-in replacement)
└── Learning curve: Minimal (Redis is simple)

OVERALL ASSESSMENT: 0.82 (HIGHLY VIABLE PATTERN)

RECOMMENDATION:
├── Best for: High-traffic apps, distributed systems
├── Watch for: Memory pressure, single point of failure
├── Mitigations: Redis Cluster, persistence configs, monitoring
└── Integration: Use redis-py library (hunt github.com/redis/redis-py?)

Alternative patterns:
├── JWT tokens (stateless, higher Ψ but lower ρ)
├── Database sessions (lower performance, higher persistence)
└── Memcached (simpler but less featured)

Would you like to hunt a Redis client library for integration?
```

---

## Example 5: Multi-Generation Evolution

### Timeline

**Generation 0 → 1: First Hunt**
```
Hunt: github.com/psf/requests
Consume: HTTPAdapter
Result: api_tools v1 created
Fitness: 0.84
```

**Generation 1 → 2: Augmentation**
```
Hunt: github.com/invl/retry
Consume: retry decorator
Result: api_tools v1 → v2 (added retry logic)
Fitness: 0.89 (+0.05)
```

**Generation 2 → 3: Refinement**
```
Hunt: github.com/requests/toolbelt
Consume: StreamingIterator
Result: api_tools v2 → v3 (added streaming)
Fitness: 0.91 (+0.02)
```

**Generation 3 → 4: Failed Integration**
```
Hunt: github.com/someone/auth-helpers
Consume: ComplexAuthHandler
Result: api_tools v3 vs v4 trial
Outcome: v4 LOSES (compatibility issues)
Fitness: v3 remains at 0.91
Graveyard: +1 entry
```

**Generation 4 → 5: Successful Integration**
```
Hunt: github.com/urllib3/urllib3
Consume: PoolManager
Result: api_tools v3 → v4 (connection pooling)
Fitness: 0.94 (+0.03)
```

**Generation 5 → 6: Autophagy**
```
Command: Autophagy text_processing
Result: Removed unused domain
Coherence: +0.06
Body simplified, focus sharpened
```

### Body State at Gen 6
```
CERATA BODY STATE

Generation: 6
Active Domains: 2 (api_tools, code_tools)
Nematocyst Count: 11
Graveyard Entries: 2

EVOLUTION PATH:
Gen 0 → 1: +HTTPAdapter
Gen 1 → 2: +retry logic
Gen 2 → 3: +streaming
Gen 3 → 4: Failed auth integration
Gen 4 → 5: +connection pooling
Gen 5 → 6: -text_processing (autophagy)

COHERENCE TREND: 0.0 → 0.84 → 0.89 → 0.91 → 0.91 → 0.94 → 1.00

Cerata has evolved from nothing to a specialized API predator.
```

---

## Example 6: Batch Hunting

### Scenario
You want to build a complete data processing pipeline by hunting multiple repositories.

### Hunt Queue
```
You: Hunt github.com/pandas-dev/pandas
You: Hunt github.com/numpy/numpy
You: Hunt github.com/matplotlib/matplotlib
You: Hunt github.com/joblib/joblib

[Cerata analyzes all four]
```

### Consolidated Report
```
MULTI-PREY ANALYSIS

1. pandas: Coherence 0.88 (PRIME)
   └── Nematocysts: DataFrame methods, read_csv, merge

2. numpy: Coherence 0.91 (PRIME)
   └── Nematocysts: Array operations, vectorization

3. matplotlib: Coherence 0.79 (VIABLE)
   └── Nematocysts: Plot functions, style management

4. joblib: Coherence 0.82 (VIABLE)
   └── Nematocysts: Parallel processing, caching

RECOMMENDATION: Hunt in order of coherence
Priority: numpy → pandas → joblib → matplotlib
```

### Sequential Consumption
```
You: Consume array operations from numpy
[Trial completes, winner promoted]

You: Consume DataFrame operations from pandas
[Trial completes, winner promoted]

You: Consume parallel processing from joblib
[Trial completes, winner promoted]

[After 3 generations, reassess if matplotlib still needed]
```

---

**These examples show Cerata's full lifecycle: perception, metabolism, competition, evolution, pruning, and learning.**
