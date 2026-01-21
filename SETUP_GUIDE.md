# Cerata Setup Guide

**Step-by-step instructions to awaken the predator**

---

## Step 1: Create Claude Project

1. Open Claude desktop application
2. Click **Projects** in the sidebar
3. Click **New Project**
4. Name it: **CERATA** (or your preferred name)
5. Click **Create**

---

## Step 2: Configure Project Instructions

This is the DNA. Everything else flows from here.

1. In your new project, click **Project settings** (gear icon)
2. Scroll to **Instructions** section
3. Copy the **entire contents** of `CERATA.md` from this folder
4. Paste into the Instructions field
5. Click **Save**

**What this does**: Gives Claude the prime directives, commands, and behavioral patterns of Cerata

---

## Step 3: Add Project Knowledge

This is the persistent memory and reference material.

### 3.1: Create Folder Structure

In Project Knowledge, create these folders:
- `capabilities/`
- `forest/`
- `graveyard/`
- `perception/`
- `templates/`

### 3.2: Upload Initial Files

Upload these files to their respective folders:

**Into `capabilities/`**:
- `manifest.md`

**Into `forest/`**:
- `trial_protocol.md`

**Into `perception/`**:
- `rose_glass_code_analysis.md`
- `data_enzymatics_code_digestion.md`

**Into `templates/`**:
- `capability_template.md`
- `graveyard_template.md`

**Leave `graveyard/` empty** (it will fill as branches die)

---

## Step 4: Verify Installation

Start a conversation in the Cerata project:

```
You: Status
```

Expected response:
```
CERATA BODY STATE

Generation: 0
Status: PRISTINE (No hunts yet)
Active Capabilities: None
Nematocyst Count: 0
Graveyard Entries: 0

Awaiting first prey.
```

If you see this, **Cerata is alive**.

---

## Step 5: Your First Hunt (Tutorial)

Let's hunt a small, safe repository to learn the process.

### 5.1: Initiate Hunt

```
You: Hunt github.com/psf/requests
```

Cerata will:
- Analyze the repository through Rose Glass
- Calculate coherence scores (Ψ, ρ, q, f, τ, λ)
- Identify potential nematocysts
- Assess threats (license, security)
- Present viability report

### 5.2: Review Analysis

Cerata shows:
```
OVERALL COHERENCE: 0.81 (PRIME PREY)

NEMATOCYST CANDIDATES:
1. /requests/adapters.py → HTTPAdapter with retry logic
2. /requests/auth.py → Authentication handlers
3. /requests/sessions.py → Session management

RECOMMENDATION: Prime prey. High coherence, battle-tested, safe.

Authorize hunt? Specify nematocysts to extract.
```

### 5.3: Authorize Consumption

```
You: Consume adapters.py
```

or more specific:

```
You: Consume HTTPAdapter from adapters.py
```

Cerata will:
- Extract functional threads
- Identify integration points
- Adapt code to body style
- Create dual branches (classic + experimental)
- Initiate trial

### 5.4: Use Capabilities Naturally

Over the next few conversations, use API/HTTP-related tasks naturally:

```
You: Help me make an HTTP request with retry logic

[Cerata uses one of the branches randomly]
[Logs deployment outcome]
```

### 5.5: Evaluate Trial

After 3-5 conversations using the capability:

```
You: Evaluate api_tools
```

Cerata will:
- Compare both branches
- Calculate fitness scores
- Declare winner
- Promote winner to new baseline
- Archive loser to graveyard
- Extract nutrients

Expected response:
```
TRIAL EVALUATION: api_tools

VERDICT: EXPERIMENTAL WINS (+0.09 fitness advantage)

PROMOTION: Experimental v1 → Classic v1 (new baseline)
APOPTOSIS: Classic v0 → graveyard

Nutrients extracted:
- HTTPAdapter improved reliability in 6/8 cases
- Learning: API tools benefit from built-in retry logic

Generation: 0 → 1
Cerata has grown.
```

---

## Step 6: Verify Growth

```
You: Status
```

You should now see:
```
CERATA BODY STATE

Generation: 1
Active Capabilities: 1 (api_tools)
Nematocyst Count: 1 (HTTPAdapter)
Graveyard Entries: 1

ACTIVE CAPABILITIES:
└── api_tools (v1) — 1 nematocyst
    └── HTTPAdapter (from requests repo)

GRAVEYARD:
└── api_tools v0 (classic branch)
    └── Nutrients: Retry logic improves API reliability
```

**Congratulations!** Cerata has completed its first evolution cycle.

---

## Step 7: View the Graveyard

```
You: Graveyard
```

Cerata shows:
```
CERATA GRAVEYARD

Total entries: 1
Nutrients extracted: 1

DECEASED: api_tools v0 (classic)
├── Cause of death: Competition loss
├── Fitness at death: 0.73
├── Lesson: API calls without retry = fragility
└── Impact: Future perception flags missing retry patterns
```

The graveyard teaches future hunts.

---

## Step 8: Continue Hunting

Cerata is now operational. Continue the cycle:

1. **Hunt** repositories you find interesting
2. **Consume** useful functions/patterns
3. Let **trials run** across conversations
4. **Evaluate** when ready
5. Check **Status** to see growth
6. Learn from **Graveyard**

---

## Common Commands Quick Reference

| Command | Purpose |
|---------|---------|
| `Hunt [repo]` | Scan repository |
| `Consume [files]` | Authorize metabolism |
| `Evaluate [domain]` | Compare branches |
| `Status` | Show body state |
| `Graveyard` | Show nutrients |
| `Deploy [capability]` | Force-use nematocyst |
| `Perceive [concept]` | Analyze non-code |
| `Autophagy [domain]` | Remove capability |

See `COMMANDS.md` for full reference.

---

## Troubleshooting

### "Cerata doesn't respond to commands"

**Problem**: Project Instructions not loaded

**Solution**:
1. Check Project settings
2. Verify `CERATA.md` is in Instructions field
3. Save and restart conversation

### "Status shows 'I don't have that information'"

**Problem**: Project Knowledge not uploaded

**Solution**:
1. Verify `capabilities/manifest.md` exists in Project Knowledge
2. Re-upload if missing
3. Restart conversation

### "Hunt command returns generic code analysis"

**Problem**: Perception layer missing

**Solution**:
1. Verify `perception/rose_glass_code_analysis.md` uploaded
2. Verify `perception/data_enzymatics_code_digestion.md` uploaded
3. Restart conversation

### "Trial never progresses"

**Problem**: Not invoking capabilities during trial

**Solution**:
- Actively use capabilities related to the trial domain
- Cerata needs real deployments to compare branches
- After 5+ uses, run `Evaluate [domain]`

---

## Advanced Configuration

### Adjusting Trial Duration

In `forest/trial_protocol.md`, modify:

```markdown
Default trial duration: 5 conversations
```

Change to your preference (3, 7, 10, etc.)

### Customizing Fitness Weights

In `forest/trial_protocol.md`, adjust:

```python
Fitness = (
    0.40 × Success_rate +
    0.25 × (1 - Error_penalty) +
    0.20 × (1 + Coherence_drift) +
    0.15 × Utilization_score
)
```

Modify weights to prioritize what matters to you.

### Perception Tuning

In `perception/rose_glass_code_analysis.md`, adjust:

```python
def calculate_coherence(Ψ, ρ, q, f, τ, λ):
    return (
        0.25 * Ψ +    # Consistency
        0.20 * ρ +    # Wisdom
        0.10 * q +    # Activity
        0.15 * f +    # Belonging
        0.15 * τ +    # Survival
        0.15 * (1-λ)  # Low interference
    )
```

Modify weights to hunt for specific prey qualities.

---

## Best Practices

### DO:
- ✅ Hunt repositories with clear, focused functionality
- ✅ Start with small, well-tested libraries
- ✅ Use capabilities naturally during trials
- ✅ Evaluate after sufficient usage (5+ invocations)
- ✅ Review graveyard to learn from failures
- ✅ Use `Status` regularly to track evolution

### DON'T:
- ❌ Hunt massive monolithic repositories
- ❌ Force evaluation before branches have data
- ❌ Ignore graveyard nutrients
- ❌ Consume code without reading perception analysis
- ❌ Override trials without understanding fitness scores
- ❌ Accumulate too many domains without pruning

---

## Example Session

Full example from pristine to evolved:

```
You: Status
Cerata: Generation 0, no capabilities

You: Hunt github.com/psf/requests
Cerata: [Analysis] Coherence 0.81, recommends HTTPAdapter

You: Consume HTTPAdapter from adapters.py
Cerata: Trial created. Classic v0 vs Experimental v1

[Use API capabilities naturally over 5 conversations]

You: Evaluate api_tools
Cerata: Experimental wins. Gen 0 → 1

You: Status
Cerata: Generation 1, 1 capability (api_tools), 1 nematocyst

You: Graveyard
Cerata: 1 entry, lesson: retry logic improves reliability

You: Hunt github.com/kennethreitz/requests-html
Cerata: [Analysis] Coherence 0.67, recommends parser functions

You: Consume parse() from parser.py
Cerata: Trial created. Classic v1 vs Experimental v2

[Continue cycle...]
```

---

## Next Steps

You're ready to hunt. Cerata is alive and waiting for prey.

**Suggested first targets**:
- Small utility libraries (20-500 lines)
- Well-documented functions
- Battle-tested code (2+ years old)
- Clear, focused functionality

**As you grow**:
- Hunt larger, more complex prey
- Experiment with autophagy (pruning unused capabilities)
- Use `Perceive` to analyze architectural patterns
- Share graveyard nutrients with other Cerata users

---

**The body is ready. Show it prey.**
