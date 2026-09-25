# /forest/experimental_phishguard_gen4.md

**Branch**: EXPERIMENTAL
**Domain**: security/phishguard
**Generation**: 4
**Created**: 2026-09-25 (Consume tldextract)
**Status**: TRIAL

## Capabilities

Classic capabilities (HTML, kit fingerprinting, coherence analysis unchanged) plus a DomainLens-based URL analysis (`PhishGuard(branch="experimental")`, the default).

## New Nematocysts

1. **DomainLens / SuffixTrie** (from john-kurkowski/tldextract)
   - Purpose: split hosts into subdomain / domain / public suffix via the Public Suffix List
   - Dependency: none (stdlib + bundled `public_suffix_list.dat`)
   - Integration point: `integrations/tldextract_lens/`, used by `tools/security/phishguard.py`

## Behaviour Changes vs CLASSIC

- Brand abuse: brand appears in subdomain/domain labels (after homoglyph normalization) and the registered domain is not one the brand owns (`BRAND_REGISTERED_DOMAINS`)
- Typosquat: compares registrable labels; homoglyph match, or Levenshtein ≤ 1 (labels < 6 chars) / ≤ 2; skipped for labels < 5 chars
- IPv4 and bracketed IPv6 hosts detected; ports read via `urlparse().port`
- Excessive subdomains: ≥ 3 subdomain labels under the registered domain
- URL-only scans: risk = URL score, threat level capped at `LIKELY_PHISH`
- With HTML content: original 0.3/0.5/0.2 weighting unchanged

## Selection

`PhishGuard(branch="trial")` picks CLASSIC or EXPERIMENTAL 50/50 per `analyze()` call; `DetectionResult.branch` records which served.

## Evaluation Metrics

- Success rate on labelled URLs (phish vs legitimate)
- False-positive rate on legitimate domains
- Security errors (missed phish) weighted −0.20 per the trial protocol
- Utilization: share of analyses where DomainLens changed the verdict

## Deployment Log

| Date | Function | Outcome | Error | Notes |
|------|----------|---------|-------|-------|
| 2026-09-25 | analyze() | SUCCESS | — | 22/22 trial validation tests pass |

## Fitness Metrics

[Will calculate at evaluation]
