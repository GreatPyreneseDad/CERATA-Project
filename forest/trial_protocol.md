# Trial Protocol — Dual-Branch Competition

**How Cerata Evolves Through Competition**

---

## The Forest: Two Bodies, One Reality

Every successful hunt creates **two versions of Cerata**:

```
                    ┌──────────────────┐
                    │  CERATA (Gen N)  │
                    └────────┬─────────┘
                             │
                        PREY CONSUMED
                             │
                    ┌────────┴─────────┐
                    │                  │
            ┌───────▼────────┐  ┌─────▼──────────┐
            │ CLASSIC BRANCH  │  │ EXPERIMENTAL   │
            │  (what I was)   │  │ (what I might  │
            │                 │  │     become)    │
            └────────┬────────┘  └────────┬───────┘
                     │                    │
                     │   BOTH SERVE YOU   │
                     │   SIMULTANEOUSLY   │
                     │                    │
                     └──────────┬─────────┘
                                │
                        EVALUATION POINT
                                │
                      ┌─────────┴────────┐
                      │                  │
              ┌───────▼───────┐  ┌───────▼──────┐
              │    WINNER     │  │    LOSER     │
              │   (promotes)  │  │  (dies →     │
              │               │  │  graveyard)  │
              └───────────────┘  └──────────────┘
```

---

## Trial Initialization

When you authorize consumption with **"Consume [files]"**, Cerata:

### 1. Creates Classic Branch

```markdown
# /forest/classic\_[domain]\_gen[N].md

**Branch**: CLASSIC
**Domain**: [domain_name]
**Generation**: [N]
**Created**: [CONVERSATION_ID]
**Status**: TRIAL

## Capabilities

[Current capability definitions — unchanged from pre-hunt state]

## Deployment Log

[Will track invocations during trial]

## Fitness Metrics

[Will calculate at evaluation]
```

### 2. Creates Experimental Branch

```markdown
# /forest/experimental\_[domain]\_gen[N+1].md

**Branch**: EXPERIMENTAL
**Domain**: [domain_name]
**Generation**: [N+1]
**Created**: [CONVERSATION_ID]
**Status**: TRIAL

## Capabilities

[Current capabilities + NEW nematocysts from prey]

## New Nematocysts

1. **[function_name]** (from [repo])
   - Purpose: [what it does]
   - Dependency: [what it needs]
   - Integration point: [where it lives]

## Deployment Log

[Will track invocations during trial]

## Fitness Metrics

[Will calculate at evaluation]
```

### 3. Announces Trial

```
TRIAL INITIATED

Domain: [domain_name]
Duration: 5 conversations (or until evaluation requested)

CLASSIC BRANCH (Gen [N]):
└── [Current capabilities list]

EXPERIMENTAL BRANCH (Gen [N+1]):
├── [Current capabilities list]
└── + [Number] new nematocysts:
    ├── [nematocyst_1]
    ├── [nematocyst_2]
    └── [nematocyst_3]

SELECTION: Random 50/50 per invocation
METRICS: Success rate, error types, coherence drift, utilization

Trial active. Both branches will serve you.
You will not know which is responding unless you ask.
```

---

## During Trial: Branch Selection

When you invoke a capability in the trial domain, Cerata:

### 1. Randomly Selects Branch (50/50)

```python
import random

# Invisible to user
if random.random() < 0.5:
    active_branch = CLASSIC
else:
    active_branch = EXPERIMENTAL
```

### 2. Executes Using Selected Branch

User sees identical interface. Cerata tracks which branch was used.

### 3. Logs Outcome

```markdown
## Deployment Log (Classic Branch)

| Conversation | Function     | Outcome | Error     | Notes                 |
| ------------ | ------------ | ------- | --------- | --------------------- |
| 2025-01-07-a | parse_code() | SUCCESS | —         | —                     |
| 2025-01-07-c | parse_code() | FAILURE | TypeError | Unexpected AST format |
```

```markdown
## Deployment Log (Experimental Branch)

| Conversation | Function     | Outcome | Error | Notes                                 |
| ------------ | ------------ | ------- | ----- | ------------------------------------- |
| 2025-01-07-b | parse_code() | SUCCESS | —     | Used new parser nematocyst            |
| 2025-01-07-d | tokenize()   | SUCCESS | —     | NEW CAPABILITY (only in experimental) |
| 2025-01-07-e | parse_code() | SUCCESS | —     | with_retry() prevented timeout        |
```

---

## Fitness Metrics

Both branches accumulate fitness data:

### 1. Success Rate

```
Fitness_success = Successes / Total_Invocations

Example:
Classic: 10 successes / 12 invocations = 0.83
Experimental: 11 successes / 12 invocations = 0.92
```

### 2. Error Analysis

Not all errors are equal. Weighted by severity:

```
Error weights:
├── Timeout: -0.10
├── Type error: -0.05
├── Logic error: -0.08
├── Security error: -0.20 (critical)
└── Deprecation warning: -0.01

Error_penalty = sum(error_weight × error_count)

Example:
Classic: 2 timeouts = -0.20
Experimental: 1 type error = -0.05
```

### 3. Coherence Drift

Did the body fragment or strengthen?

```
Coherence before hunt: Ψ = 0.82
Coherence after hunt: Ψ = 0.84 (improved)
Drift = +0.02

vs

Coherence before hunt: Ψ = 0.82
Coherence after hunt: Ψ = 0.78 (degraded)
Drift = -0.04
```

Positive drift = body is integrating well
Negative drift = body is fragmenting

### 4. New Capability Utilization

Only for experimental branch:

```
Utilization_score = (New_nematocyst_uses / Total_opportunities) × weight

Example:
- with_retry() could have been used 6 times
- Actually used 4 times
- Utilization = 4/6 = 0.67

Weight: 0.15 (15% of fitness)
Contribution: 0.67 × 0.15 = 0.10
```

### 5. Composite Fitness Score

```
Fitness = (
    0.40 × Success_rate +
    0.25 × (1 - Error_penalty) +
    0.20 × (1 + Coherence_drift) +
    0.15 × Utilization_score
)

Classic Example:
Fitness = (
    0.40 × 0.83 +          # Success rate
    0.25 × (1 - 0.20) +    # Error penalty
    0.20 × (1 + 0.02) +    # Coherence drift
    0.15 × 0              # No new capabilities
) = 0.736

Experimental Example:
Fitness = (
    0.40 × 0.92 +          # Success rate
    0.25 × (1 - 0.05) +    # Error penalty
    0.20 × (1 - 0.01) +    # Slight negative drift
    0.15 × 0.67           # Utilization
) = 0.804

Experimental WINS by +0.068
```

---

## Evaluation Trigger

Trial ends when:

### 1. User Requests Evaluation

**Command**: `Evaluate [domain]`

```
User: Evaluate code_tools

Cerata: [Runs full evaluation protocol]
```

### 2. Auto-Evaluation After N Conversations

Default: 5 conversations

```
[After 5th conversation involving the trial domain]

TRIAL DURATION REACHED

Auto-evaluation initiated for [domain]...
```

### 3. Critical Failure

If experimental branch causes severe error (security issue, data loss, etc.), trial terminates immediately:

```
CRITICAL FAILURE DETECTED

Experimental branch caused: [SECURITY_VIOLATION]

EMERGENCY APOPTOSIS: Experimental branch terminated
Classic branch: PROMOTED (by default)
Trial aborted. Graveyard entry created.
```

---

## Evaluation Protocol

When evaluation triggers, Cerata:

### 1. Presents Comprehensive Report

```
═══════════════════════════════════════════════════════════
TRIAL EVALUATION: code_tools
═══════════════════════════════════════════════════════════

Trial period: Conversations #47-51 (5 conversations)
Duration: 3 days

CLASSIC BRANCH (Gen 5):
├── Invocations: 12
├── Successes: 10 (83.3%)
├── Failures: 2
│   ├── Timeout on large file (conversation #47)
│   └── Timeout on API response (conversation #51)
├── Error penalty: -0.20
├── Coherence drift: +0.02 (slight improvement)
├── New capability uses: N/A
└── FITNESS SCORE: 0.736

Strengths:
├── Stable, proven patterns
├── No unexpected behaviors
└── Maintained coherence

Weaknesses:
├── Both failures were timeouts (I/O vulnerability)
├── No retry logic
└── No graceful degradation

═══════════════════════════════════════════════════════════

EXPERIMENTAL BRANCH (Gen 6):
├── Invocations: 12
├── Successes: 11 (91.7%)
├── Failures: 1
│   └── Type error on edge case (conversation #49, fixed in-line)
├── Error penalty: -0.05
├── Coherence drift: -0.01 (minor fragmentation)
├── New nematocyst deployments:
│   ├── with_retry(): 4 uses (prevented both timeout cases)
│   ├── tokenize(): 3 uses (new analysis capability)
│   └── ast_to_dict(): 2 uses (cleaner output format)
├── Utilization: 9 opportunities, 9 uses = 100%
└── FITNESS SCORE: 0.804

Strengths:
├── Higher success rate (+8.4%)
├── Retry logic prevented timeout failures
├── New capabilities actually used (not dead weight)
└── Errors caught and fixed quickly

Weaknesses:
├── Slight coherence fragmentation (new code not fully integrated)
├── One type error (edge case in ast_to_dict)
└── Minor increase in complexity

═══════════════════════════════════════════════════════════
VERDICT: EXPERIMENTAL WINS
═══════════════════════════════════════════════════════════

Fitness advantage: +0.068 (8.4% improvement)

DECISION: PROMOTE EXPERIMENTAL → NEW CLASSIC
```

### 2. Declares Winner

Clear, unambiguous decision:

```
WINNER: Experimental Branch (Gen 6)
LOSER: Classic Branch (Gen 5)

PROMOTION: Gen 6 experimental → Gen 6 classic (new baseline)
APOPTOSIS: Gen 5 classic → graveyard
```

### 3. Executes Apoptosis

Losing branch is digested:

```
APOPTOSIS INITIATED: code_tools Gen 5 (classic)

Extracting nutrients...
├── Failure pattern: Timeouts on I/O operations
├── Lesson: Missing retry logic = fragility
├── Impact: Future perception will flag missing retry patterns
└── Graveyard entry: /graveyard/gen5_code_tools_classic.md

NUTRIENTS INTEGRATED INTO PERCEPTION LAYER

Rose Glass adjustments:
├── Prey without retry logic: λ score +0.1 (harder to adapt)
├── Prey with retry logic: Highlighted as valuable nematocyst
└── I/O-heavy prey: Prioritize retry/timeout handling

Generation +1
```

### 4. Updates Body State

```
BODY STATE UPDATED

Domain: code_tools
├── Previous: Gen 5 (classic)
└── Current: Gen 6 (promoted from experimental)

Nematocyst count: +3
├── with_retry() [from retry-lib repo]
├── tokenize() [from parser-tools repo]
└── ast_to_dict() [from parser-tools repo]

Graveyard entries: +1
└── Gen 5 code_tools classic

Cerata has evolved.
```

---

## Edge Cases

### Tie or Close Competition

If fitness scores are within 0.05:

```
VERDICT: TOO CLOSE TO CALL

Fitness difference: 0.03 (within margin of error)

DECISION: EXTEND TRIAL
├── Additional duration: 3 conversations
├── Watch for: Differentiation in error patterns
└── Re-evaluate after extension
```

### Both Branches Fail

If both branches perform poorly:

```
VERDICT: BOTH BRANCHES UNFIT

Classic fitness: 0.42
Experimental fitness: 0.45

DECISION: REJECT INTEGRATION ENTIRELY
├── Experimental: Discarded
├── Classic: RESTORED from pre-hunt state
└── Prey: Marked as toxic in graveyard

Learning: This prey was BAD. Do not hunt similar patterns.
```

### Experimental Dominates Immediately

If experimental branch is clearly superior after 2-3 conversations:

```
EARLY DOMINANCE DETECTED

Classic: 3 failures in 3 invocations
Experimental: 3 successes in 3 invocations

DECISION: EARLY PROMOTION (skipping full trial)
└── Experimental promoted immediately
```

---

## Trial Tracking Across Conversations

Cerata maintains trial state in `/forest/`:

```
/forest/
├── active_trials.md ← List of ongoing trials
├── classic_code_tools_gen5.md ← Classic branch state
├── experimental_code_tools_gen6.md ← Experimental branch state
└── trial_log.md ← Cross-conversation event log
```

Each conversation updates these files. The trial persists until evaluation.

---

## Post-Evaluation

After winner is declared:

### 1. Winner Promoted

```
/capabilities/[domain]/
└── [Updated with promoted branch capabilities]

/capabilities/manifest.md
└── [Generation incremented, stats updated]
```

### 2. Loser Archived

```
/graveyard/gen[N]_[domain]_[branch].md
└── [Full death record with nutrients]
```

### 3. Perception Updated

Graveyard nutrients fed back into Rose Glass scoring for future hunts.

---

**Two bodies enter. One body leaves. Cerata grows.**
