"""
CERATA tldextract Integration
═════════════════════════════

Nematocyst metabolized from github.com/john-kurkowski/tldextract
(BSD-3-Clause). Public Suffix List snapshot from publicsuffix.org (MPL-2.0).

The package is named ``tldextract_lens`` (not ``tldextract``) so it can never
shadow the upstream library on ``sys.path``.
"""

from .domain_lens import (
    DomainLens,
    DomainReading,
    SuffixTrie,
    lenient_netloc,
    looks_like_ipv4,
    looks_like_ipv6,
    parse_suffix_list,
)

__all__ = [
    "DomainLens",
    "DomainReading",
    "SuffixTrie",
    "lenient_netloc",
    "looks_like_ipv4",
    "looks_like_ipv6",
    "parse_suffix_list",
]
