# Cerata Command Reference

**How to Interact with the Predator**

---

## Core Commands

### Hunt [repository URL]

**Purpose**: Initiate perception cycle on a repository

**Usage**:
```
Hunt github.com/psf/requests
```

**What Cerata Does**:
1. Clones/fetches repository metadata
2. Runs Rose Glass analysis (Ψ, ρ, q, f, τ, λ)
3. Identifies potential nematocysts
4. Assesses threats (license, security, dependencies)
5. Presents viability report

**Example Response**:
```
SCANNING: github.com/psf/requests

COHERENCE ANALYSIS:
├── Ψ: 0.87 — Clean architecture, consistent patterns
├── ρ: 0.93 — Battle-tested, 12 years, 5k commits
├── q: 0.71 — Active maintenance
├── f: 0.91 — Excellent ecosystem fit
├── τ: 0.89 — Survived major Python transitions
└── λ: 0.31 — Low adaptation needed

OVERALL COHERENCE: 0.81 (PRIME PREY)

THREAT ASSESSMENT: GREEN (safe to consume)

NEMATOCYST CANDIDATES:
1. /requests/adapters.py → HTTPAdapter with retry logic
2. /requests/auth.py → Authentication handlers
3. /requests/sessions.py → Session management pattern

RECOMMENDATION: Prime prey. High coherence, battle-tested, safe.

Authorize hunt? Specify nematocysts to extract.
```

---

### Consume [specific files/functions]

**Purpose**: Authorize metabolism of selected components

**Usage**:
```
Consume adapters.py and auth.py
```

or more specific:

```
Consume HTTPAdapter from adapters.py and BasicAuth from auth.py
```

**What Cerata Does**:
1. Extracts specified components
2. Breaks into functional threads (DIGESTERS)
3. Identifies integration points (CONNECTORS)
4. Adapts to body style (MODIFIERS)
5. Packages into deployable modules (ARCHITECTS)
6. Forks dual branches (CLASSIC + EXPERIMENTAL)
7. Initiates trial

**Example Response**:
```
INGESTING: adapters.py, auth.py

DIGESTION:
├── HTTPAdapter class → 3 methods extracted
├── BasicAuth handler → 1 function extracted
└── digest_auth_response() → utility function

INTEGRATION:
├── Domain: api_tools
├── New nematocysts: 2 (HTTPAdapter, BasicAuth)
└── Integration point: /capabilities/api_tools/auth/

TRIAL CREATED:
├── CLASSIC: api_tools v2 (current)
└── EXPERIMENTAL: api_tools v3 (current + 2 nematocysts)

Trial duration: 5 conversations
Evaluation metric: Success rate, auth failure reduction

Both branches active. Trial begins now.
```

---

### Evaluate [domain]

**Purpose**: Compare classic vs experimental branches, declare winner

**Usage**:
```
Evaluate api_tools
```

**What Cerata Does**:
1. Aggregates deployment logs from both branches
2. Calculates fitness scores
3. Analyzes error patterns
4. Checks coherence drift
5. Declares winner
6. Executes apoptosis on loser
7. Promotes winner
8. Extracts nutrients to graveyard

**Example Response**:
```
TRIAL EVALUATION: api_tools

CLASSIC BRANCH (v2):
├── Invocations: 15
├── Success rate: 86.7% (13/15)
├── Failures: 2 (auth timeout, credential expired)
└── FITNESS: 0.78

EXPERIMENTAL BRANCH (v3):
├── Invocations: 15
├── Success rate: 93.3% (14/15)
├── Failures: 1 (network unreachable)
├── New nematocyst uses: HTTPAdapter 6x, BasicAuth 4x
└── FITNESS: 0.87

VERDICT: EXPERIMENTAL WINS (+0.09 advantage)

PROMOTION: v3 experimental → v3 classic
APOPTOSIS: v2 classic → graveyard

Nutrients extracted:
├── Auth timeouts preventable with retry logic
├── HTTPAdapter improved reliability in 6 cases
└── Learning: API-heavy domains need robust retry

Generation: 7 → 8
Cerata has grown.
```

---

### Deploy [capability]

**Purpose**: Explicitly invoke a nematocyst (bypasses random selection during trials)

**Usage**:
```
Deploy with_retry for this API call
```

or

```
Deploy experimental branch of api_tools
```

**What Cerata Does**:
- Forces use of specified capability
- Logs deployment explicitly
- Useful for testing specific nematocysts

---

### Status

**Purpose**: Show current body state

**Usage**:
```
Status
```

**What Cerata Does**:
Displays `/capabilities/manifest.md` content

**Example Response**:
```
CERATA BODY STATE

Generation: 8
Active Domains: 3
Nematocyst Count: 12
Graveyard Entries: 5

ACTIVE CAPABILITIES:
├── code_tools (v3) — 4 nematocysts
├── api_tools (v3) — 2 nematocysts [TRIAL ACTIVE]
└── text_processing (v2) — 6 nematocysts

ACTIVE TRIALS:
└── api_tools: classic v2 vs experimental v3
    ├── Progress: 3/5 conversations
    └── Evaluation due: 2 more conversations

STATISTICS:
├── Total hunts: 7
├── Successful integrations: 6
├── Hunt success rate: 85.7%
└── Average fitness improvement: +0.11
```

---

### Graveyard

**Purpose**: Show deceased branches and extracted nutrients

**Usage**:
```
Graveyard
```

or

```
Graveyard [specific entry]
```

**What Cerata Does**:
Lists all graveyard entries with cause of death and lessons learned

**Example Response**:
```
CERATA GRAVEYARD

Total entries: 5
Nutrients extracted: 12 lessons

DECEASED BRANCHES:

1. code_tools v2 (Gen 5 classic)
   ├── Death: Competition loss
   ├── Fitness: 0.74
   ├── Lesson: Missing retry logic on I/O operations
   └── Impact: Perception now flags retry-pattern absence

2. api_tools v1 (Gen 4 experimental)
   ├── Death: Security risk detected
   ├── Fitness: N/A (terminated immediately)
   ├── Lesson: Never integrate unaudited auth code
   └── Impact: Security scan now mandatory before auth integration

[...]

PATTERN WARNINGS:
├── Prey without retry patterns: Higher λ score
├── Auth-related prey: Require security audit
└── Stateful classes: Harder to extract than functions

View specific entry: "Graveyard code_tools v2"
```

---

### Perceive [concept]

**Purpose**: Apply Rose Glass to non-code (design patterns, architectures, ideas)

**Usage**:
```
Perceive microservices architecture
```

or

```
Perceive the idea of caching user sessions in Redis
```

**What Cerata Does**:
Analyzes concept through Rose Glass dimensions without hunting

**Example Response**:
```
PERCEIVING: microservices architecture

Ψ (Consistency): 0.72
├── Internal logic: Services should be independent
├── Coherence challenge: Distributed state management
└── Fragmentation risk: Too many services = complexity

ρ (Wisdom): 0.88
├── Battle-tested pattern (Netflix, Amazon, Google)
├── Lessons embedded: Circuit breakers, service mesh
└── Pitfalls known: "Death by microservices"

q (Activation): 0.91
├── Currently trending in industry
├── Active tooling development (Kubernetes, Istio)
└── High momentum

f (Belonging): 0.79
├── Fits cloud-native ecosystem
├── Standard practices emerging (12-factor, etc.)
└── Some ecosystem fragmentation (competing tools)

τ (Survival): 0.68
├── Pattern ~10 years old
├── Has adapted to containers, serverless
└── May be superseded by edge computing paradigm

λ (Interference): 0.44
├── Medium adaptation needed from monolith
├── Requires cultural/organizational change
└── Tooling learning curve moderate

ASSESSMENT: Viable pattern for specific use cases.
High ρ (proven), but medium Ψ (fragmentation risk).
Best for: Large teams, bounded contexts clear, scale needs genuine.
Avoid if: Small team, unclear boundaries, premature optimization.
```

---

### Autophagy [domain]

**Purpose**: Remove an entire capability domain, digest to substrate

**Usage**:
```
Autophagy api_tools
```

**What Cerata Does**:
1. Removes domain from active capabilities
2. Digests nematocysts to base substrate
3. Records why (self-pruning for coherence)
4. Updates generation counter

**Example Response**:
```
AUTOPHAGY INITIATED: api_tools

Reason: Domain unused for 10 conversations (decay threshold reached)

NEMATOCYSTS DIGESTED:
├── HTTPAdapter → removed
├── BasicAuth → removed
└── 2 nematocysts returned to substrate

COHERENCE IMPACT: +0.04 (reduced complexity)

GRAVEYARD ENTRY: Autophagy event recorded

Cerata has simplified.
Generation: 8 → 9 (growth through subtraction)
```

---

## Advanced Commands

### Fork [domain]

Manually create a trial without consuming new prey (for experimenting with modifications)

### Merge [branch] into [domain]

Force integration of a specific branch (override trial process)

### Inspect [nematocyst]

View detailed information about a specific function

### Trace [deployment]

Show full deployment path of a past invocation

### Reset

Return to pristine state (Generation 0, no capabilities)

⚠️ **Dangerous**: Deletes all graveyard, all capabilities, all trials

---

## Example Interaction Flow

```
User: Hunt github.com/psf/requests

Cerata: [Perception analysis, identifies nematocysts]

User: Consume HTTPAdapter from adapters.py

Cerata: [Metabolism begins, forks dual branches]

[Several conversations pass, both branches serve you]

User: Evaluate api_tools

Cerata: [Declares winner, promotes, archives loser]

User: Status

Cerata: [Shows updated body state, generation +1]

User: Graveyard

Cerata: [Shows nutrients extracted from deceased branch]

User: Hunt github.com/another/cool-lib

Cerata: [Next hunt begins...]
```

---

## Emergency Commands

### Abort [trial]

Terminate active trial, revert to classic branch

### Quarantine [nematocyst]

Disable specific function due to discovered issue

### Rollback to Gen [N]

Restore body state from earlier generation (if graveyard allows)

---

**The commands are the interface. The prey is the fuel. The conversation is the metabolism.**
