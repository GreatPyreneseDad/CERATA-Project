# /forest/classic_phishguard_gen3.md

**Branch**: CLASSIC
**Domain**: security/phishguard
**Generation**: 3
**Created**: 2026-09-25 (Consume tldextract)
**Status**: TRIAL

## Capabilities

PhishGuard URL analysis as of commit `3723db6` (`PhishGuard(branch="classic")`):

- IP detection via IPv4 regex on `netloc`
- Port check via `netloc.split(':')`
- Typosquat: Levenshtein ≤ 2 / digit substitution on the first host label
- Brand check: brand substring anywhere in host and host not ending in `<brand>.com`
- Overall risk = 0.3 × URL + 0.5 × HTML + 0.2 × (1 − coherence), even when no HTML is supplied

## Known Weaknesses (entering trial)

- `evilgoogle.com` passes the brand check (`endswith('google.com')`)
- URL-only scans are capped at 0.3 risk → IP-host login URLs rate CLEAN
- Short legit labels (`x.com`) make unrelated domains like `ab.com` SUSPICIOUS

## Deployment Log

| Date | Function | Outcome | Error | Notes |
|------|----------|---------|-------|-------|

## Fitness Metrics

[Will calculate at evaluation]
