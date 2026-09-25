# tldextract Integration

> *Prey consumed: `john-kurkowski/tldextract`: Public Suffix List domain parsing metabolized into f-dimension ownership perception*

## Hunt Record

**Target**: https://github.com/john-kurkowski/tldextract
**Hunt Date**: 2026-09-25
**Status**: TRIAL
**Coherence Score**: 3.142 (`tools/hunt.py`, 0–4 scale); PRIME_PREY
**License**: BSD-3-Clause (`LICENSE-tldextract`); PSL data MPL-2.0 (header retained in `public_suffix_list.dat`)
**Gap Filled**: PhishGuard's string-based domain checks (`evilgoogle.com` passed the brand check; typosquat detection compared `www` labels; IP hosts scored CLEAN)

## Perception Analysis (Rose Glass)

Scores from `python3 tools/hunt.py john-kurkowski/tldextract`:

- **Ψ (Psi)**: 1.000 — README, tests, license, docs, classes + functions
- **ρ (Rho)**: 0.650 — tested, documented; `hunt.py` reported no CI, but upstream has `.github/workflows/ci.yml` (known `hunt.py` false negative: its `.git` filter also skips `.github`)
- **q (Q)**: 0.500 — `hunt.py` placeholder; upstream v5.3.2 released 2026-08-08, pushed 2026-09-20
- **f (F)**: 0.950 — standard packaging, small dependency set (`idna`, `requests`, `requests-file`, `filelock`)
- **τ / λ**: not measured by `hunt.py`

**Recommendation**: PRIME

## What Was Extracted

| tldextract Source | Nematocyst | Rose Glass Dimension |
|-------------------|-------------|---------------------|
| `tldextract.Trie`, `_PublicSuffixListTLDExtractor.suffix_index` | `SuffixTrie` | f (ownership boundary) |
| `TLDExtract._extract_netloc`, `ExtractResult` | `DomainLens.perceive` → `DomainReading` | f (belonging) |
| `remote.lenient_netloc`, `looks_like_ip`, `looks_like_ipv6` | `lenient_netloc`, `looks_like_ipv4/6` | infrastructure |
| `suffix_list.extract_tlds_from_suffix_list` | `parse_suffix_list` | infrastructure |

## Metabolism Process

- **Digested**: suffix trie with PSL `*` wildcard and `!` exception rules, lenient netloc parsing, IPv4/IPv6 detection.
- **Discarded**: remote fetching, disk cache, `requests`/`requests-file`/`filelock`/`idna` dependencies, CLI.
- **Adapted**:
  - Zero third-party dependencies; punycode decoded with the stdlib `idna` codec.
  - PSL snapshot bundled (`VERSION: 2026-09-24_13-26-36_UTC`, from publicsuffix.org), so perception is offline and deterministic.
  - PSL private domains included by default, so `evil.github.io` is its own registered domain.
  - Hosts are lower-cased; the matched rule's `is_private` flag is tracked explicitly.
  - Package named `tldextract_lens` so it cannot shadow the real `tldextract`.
- **Differential check**: 20 tricky hosts (wildcards, exceptions, private suffixes, IDN, IPv6, userinfo/ports) compared with upstream tldextract 5.3.x on the same PSL file: identical except for intentional lower-casing.

## Trial Status

Integration point: `tools/security/phishguard.py`.

- **CLASSIC** (Gen 3): original URL analysis, byte-for-byte identical demo output.
- **EXPERIMENTAL** (Gen 4): URL analysis through `DomainLens`, plus URL-only scoring on URL evidence (capped at `LIKELY_PHISH` without page content).

Select with `PhishGuard(branch="classic" | "experimental" | "trial")`; `trial` picks 50/50 per `analyze()` call and records `DetectionResult.branch`. See `forest/experimental_phishguard_gen4.md`.

| URL | CLASSIC | EXPERIMENTAL |
|-----|---------|--------------|
| `https://evilgoogle.com/login` | CLEAN | LIKELY_PHISH |
| `http://192.168.1.5/secure-login-verify` | CLEAN | LIKELY_PHISH |
| `https://accounts.google.com.evil.io/` | SUSPICIOUS | LIKELY_PHISH |
| `https://g00gle.com` | SUSPICIOUS | LIKELY_PHISH |
| `https://ab.com` | SUSPICIOUS (false positive vs `x.com`) | CLEAN |
| `https://www.google.com` | CLEAN | CLEAN |

## Usage

```python
from integrations.tldextract_lens import DomainLens

lens = DomainLens()
r = lens.perceive("https://accounts.google.com.evil.io/login")
r.subdomain, r.domain, r.suffix   # ('accounts.google.com', 'evil', 'io')
r.registered_domain               # 'evil.io'
r.belongs_to({"google.com"})      # False
lens.same_owner("a.bbc.co.uk", "b.bbc.co.uk")  # True
```

Refresh the snapshot (only from publicsuffix.org, per its maintainers):

```bash
curl -sSfL https://publicsuffix.org/list/public_suffix_list.dat \
  -o integrations/tldextract_lens/public_suffix_list.dat
```

## Tests

```bash
python3 -m unittest discover -s integrations/tldextract_lens/tests
```

## Known Limits

- Brand coverage is the 7 brands PhishGuard already knew; `paypa1.com` remains CLEAN in both branches.
- Brand-owned domains not in `BRAND_REGISTERED_DOMAINS` (e.g. `googleusercontent.com`) are flagged as brand abuse.
- The bundled PSL ages; refresh it periodically.
