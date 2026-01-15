# Cerata Tools

**Defensive security tools demonstrating Rose Glass in practice**

---

## Overview

This directory contains practical implementations of Rose Glass analysis for defensive security purposes. These tools show how the perception framework can be applied to real-world security challenges.

---

## Available Tools

### PhishGuard - Phishing Kit Detection

**Location**: `security/phishguard.py`

**Purpose**: Detects phishing attempts using multi-layer analysis including Rose Glass coherence analysis.

**Detection Vectors**:
1. URL Analysis - typosquatting, suspicious TLDs, IP addresses
2. HTML Analysis - form hijacking, hidden fields, obfuscated JS
3. Network Analysis - SSL certificates, HTTP headers
4. Kit Fingerprinting - SocialFish and other known phishing kits
5. **Rose Glass Coherence** - dimensional fracture detection

**Usage**:
```bash
# Run demo with test cases
python3 tools/security/phishguard.py

# Use in your own code
from tools.security.phishguard import PhishGuard

guard = PhishGuard()
result = guard.analyze(
    url="https://suspicious-site.com/login",
    html_content=page_html,
    claimed_identity="facebook"
)

print(f"Threat Level: {result.threat_level.name}")
print(f"Confidence: {result.confidence:.1%}")
```

**Rose Glass Dimensions Applied**:

| Dimension | Application to Phishing Detection |
|-----------|-----------------------------------|
| **Ψ (Psi)** | Brand consistency - does visual claim match actual behavior? |
| **ρ (Rho)** | Professional implementation - amateur patterns vs. legitimate quality |
| **q (Q)** | Urgency manipulation - artificially elevated activation (fear/greed) |
| **f (F)** | Trust signals - fake badges vs. authentic security indicators |

**Dimensional Fracture Detection**:

Phishing pages create **inconsistencies between dimensions** that legitimate pages don't:

- **High q + Low Ψ**: "URGENT! Verify now!" but branding inconsistent → manipulation
- **High f + Low ρ**: "100% Bank-Grade Security!" but amateur implementation → fakery
- **Visual claims ≠ Form targets**: Claims to be Facebook but posts to external domain → hijack

These fractures are the phishing signature that simple pattern matching misses.

---

## Rose Glass in Practice

These tools demonstrate the core Cerata philosophy: **perception reveals intent**.

Traditional security tools look for:
- Known bad signatures (reactive)
- Blacklisted domains (always behind)
- Pattern matching (brittle)

Rose Glass looks for:
- **Dimensional coherence** (intent analysis)
- **Fracture patterns** (inconsistency detection)
- **Behavioral signatures** (how things work, not what they are)

This is the same perception layer Cerata uses to evaluate code repositories, applied to security analysis.

---

## Contributing Tools

To add a new tool demonstrating Rose Glass:

1. Create subdirectory in `tools/` (e.g., `tools/malware/`, `tools/forensics/`)
2. Implement Rose Glass dimensions for your domain
3. Show dimensional fractures unique to your threat model
4. Document which dimensions matter most for your use case
5. Add entry to this README

**Requirements**:
- Must be defensive security only (detection, analysis, forensics)
- Must implement Rose Glass coherence analysis
- Must show dimensional fractures as signatures
- Must be educational and open source

---

## Philosophy

These tools are **nematocysts** - weapons stolen from the security domain and integrated into Cerata's body.

They show that Rose Glass isn't just theory. It's a practical framework for:
- Detecting deception
- Analyzing intent
- Finding inconsistencies that reveal hidden behavior

If phishing pages show dimensional fractures, what else does? Malware? Data exfiltration? Supply chain attacks?

**The perception layer is the weapon.**

---

## License

MIT - Because defensive security should be open.

---

## Acknowledgments

- **SocialFish**: Studied (ethically) to understand phishing kit architecture
- **Rose Glass Framework**: Christopher MacGregor bin Joseph
- **Defensive Philosophy**: "Know thy enemy by perceiving their incoherence"
