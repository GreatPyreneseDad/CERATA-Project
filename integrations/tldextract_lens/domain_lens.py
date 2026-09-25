"""
Domain Lens - f-Dimension Perception via Public Suffix List
===========================================================

Nematocyst metabolized from john-kurkowski/tldextract (BSD-3-Clause,
see LICENSE-tldextract).

Splits a host into subdomain / domain / suffix using the Public Suffix List
(PSL), so callers can reason about *which organisation a host belongs to*
(its registered domain) instead of naive string matching.

- f (Belonging): a host belongs to the owner of its registered domain.
  ``accounts.google.com.evil.io`` belongs to ``evil.io``, not Google.

Digestion notes (what changed from the prey):
- Suffix trie + wildcard/exception lookup ported from
  ``tldextract.tldextract.Trie`` and ``_PublicSuffixListTLDExtractor``.
  The matched suffix node is tracked explicitly, so ``is_private`` reflects
  the rule that actually matched.
- Lenient netloc parsing and IP detection ported from ``tldextract.remote``.
- No network, disk cache, ``requests`` or ``idna`` dependencies: the PSL
  snapshot is bundled (``public_suffix_list.dat``, MPL-2.0) and punycode is
  decoded with the stdlib ``idna`` codec.
- PSL private domains (e.g. ``github.io``, ``blogspot.com``) are included by
  default. For security perception, ``evil.github.io`` must belong to
  ``evil.github.io``, not to ``github.io``.
"""

import re
from dataclasses import dataclass, field
from ipaddress import AddressValueError, IPv6Address
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.parse import scheme_chars

DEFAULT_SUFFIX_LIST = Path(__file__).parent / "public_suffix_list.dat"
PRIVATE_SEPARATOR = "// ===BEGIN PRIVATE DOMAINS==="

_IPV4_RE = re.compile(
    r"^(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.)"
    r"{3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$",
    re.ASCII,
)
_SCHEME_CHARS = set(scheme_chars)
_DOT_VARIANTS = ("\u3002", "\uff0e", "\uff61")


def _schemeless_url(url: str) -> str:
    double_slashes_start = url.find("//")
    if double_slashes_start == 0:
        return url[2:]
    if (
        double_slashes_start < 2
        or url[double_slashes_start - 1] != ":"
        or set(url[: double_slashes_start - 1]) - _SCHEME_CHARS
    ):
        return url
    return url[double_slashes_start + 2:]


def lenient_netloc(url: str) -> str:
    """Extract the host of a URL-like string without raising.

    Strips scheme, userinfo (``user@``), port, path, query, fragment and the
    trailing root label. Bracketed IPv6 hosts are returned with brackets.
    """
    after_userinfo = (
        _schemeless_url(url.strip())
        .partition("/")[0]
        .partition("?")[0]
        .partition("#")[0]
        .rpartition("@")[-1]
    )
    if after_userinfo and after_userinfo[0] == "[":
        maybe_ipv6 = after_userinfo.partition("]")
        if maybe_ipv6[1] == "]":
            return f"{maybe_ipv6[0]}]"
    hostname = after_userinfo.partition(":")[0].strip()
    for dot in _DOT_VARIANTS:
        hostname = hostname.replace(dot, ".")
    return hostname.rstrip(".")


def looks_like_ipv4(host: str) -> bool:
    return bool(host) and host[0].isdecimal() and _IPV4_RE.fullmatch(host) is not None


def looks_like_ipv6(host: str) -> bool:
    try:
        IPv6Address(host)
    except AddressValueError:
        return False
    return True


def _decode_punycode(label: str) -> str:
    lowered = label.lower()
    if lowered.startswith("xn--"):
        try:
            return lowered.encode("ascii").decode("idna")
        except (UnicodeError, ValueError):
            pass
    return lowered


class SuffixTrie:
    """Trie of PSL rules, stored label-reversed (``co.uk`` -> uk -> co)."""

    __slots__ = ("children", "end", "is_private")

    def __init__(self) -> None:
        self.children: Dict[str, "SuffixTrie"] = {}
        self.end = False
        self.is_private = False

    def add(self, rule: str, is_private: bool = False) -> None:
        node = self
        for label in reversed(rule.split(".")):
            node = node.children.setdefault(label, SuffixTrie())
        node.end = True
        node.is_private = is_private

    def suffix_index(self, labels: List[str]) -> Optional[Tuple[int, bool]]:
        """Return (index of first suffix label, matched rule is private).

        Implements the PSL algorithm including ``*`` wildcards and ``!``
        exceptions. Returns ``None`` when no rule matches.
        """
        node = self
        label_idx = len(labels)
        match: Optional[Tuple[int, bool]] = None

        for label in reversed(labels):
            decoded = _decode_punycode(label)
            if decoded in node.children:
                label_idx -= 1
                node = node.children[decoded]
                if node.end:
                    match = (label_idx, node.is_private)
                continue

            wildcard = node.children.get("*")
            if wildcard is not None:
                if "!" + decoded in node.children:
                    return label_idx, wildcard.is_private
                return label_idx - 1, wildcard.is_private
            break

        return match


def parse_suffix_list(text: str) -> Tuple[List[str], List[str]]:
    """Split raw PSL text into (public rules, private rules)."""
    public_text, _, private_text = text.partition(PRIVATE_SEPARATOR)

    def rules(block: str) -> List[str]:
        out = []
        for line in block.splitlines():
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            out.append(line.split()[0].lower())
        return out

    return rules(public_text), rules(private_text)


@dataclass
class DomainReading:
    """Structural perception of a URL's host."""

    host: str
    subdomain: str
    domain: str
    suffix: str
    is_private_suffix: bool = False
    ip_version: Optional[int] = None
    notes: List[str] = field(default_factory=list)

    @property
    def is_ip(self) -> bool:
        return self.ip_version is not None

    @property
    def registered_domain(self) -> str:
        """``domain.suffix`` (e.g. ``bbc.co.uk``); empty for IPs/bare labels."""
        if self.domain and self.suffix:
            return f"{self.domain}.{self.suffix}"
        return ""

    @property
    def fqdn(self) -> str:
        if not self.registered_domain:
            return ""
        return ".".join(p for p in (self.subdomain, self.registered_domain) if p)

    @property
    def subdomain_labels(self) -> List[str]:
        return self.subdomain.split(".") if self.subdomain else []

    def belongs_to(self, registered_domains: Iterable[str]) -> bool:
        """f-dimension check: is this host owned by one of these domains?"""
        own = self.registered_domain
        return bool(own) and own in {d.lower() for d in registered_domains}

    def to_dict(self) -> Dict:
        return {
            "host": self.host,
            "subdomain": self.subdomain,
            "domain": self.domain,
            "suffix": self.suffix,
            "registered_domain": self.registered_domain,
            "is_private_suffix": self.is_private_suffix,
            "ip_version": self.ip_version,
            "notes": list(self.notes),
        }


class DomainLens:
    """
    Perceive the ownership structure of URLs via the Public Suffix List.

    Usage:
        lens = DomainLens()
        reading = lens.perceive("https://accounts.google.com.evil.io/login")
        reading.registered_domain   # 'evil.io'
        reading.subdomain           # 'accounts.google.com'
    """

    _trie_cache: Dict[Tuple[str, bool], SuffixTrie] = {}

    def __init__(
        self,
        suffix_list_path: Optional[Path] = None,
        include_private: bool = True,
        extra_suffixes: Iterable[str] = (),
    ) -> None:
        self.suffix_list_path = Path(suffix_list_path or DEFAULT_SUFFIX_LIST)
        self.include_private = include_private
        self.extra_suffixes = tuple(s.lower().strip(".") for s in extra_suffixes)
        self._trie = self._load_trie()

    def _build_trie(self) -> SuffixTrie:
        public, private = parse_suffix_list(
            self.suffix_list_path.read_text(encoding="utf-8")
        )
        trie = SuffixTrie()
        for rule in public:
            trie.add(rule)
        if self.include_private:
            for rule in private:
                trie.add(rule, is_private=True)
        for rule in self.extra_suffixes:
            trie.add(rule)
        return trie

    def _load_trie(self) -> SuffixTrie:
        # Extra suffixes change the trie, so only the plain PSL trie is shared.
        if self.extra_suffixes:
            return self._build_trie()
        key = (str(self.suffix_list_path.resolve()), self.include_private)
        if key not in self._trie_cache:
            self._trie_cache[key] = self._build_trie()
        return self._trie_cache[key]

    def perceive(self, url: str) -> DomainReading:
        """Parse a URL (or bare host) into a DomainReading."""
        host = lenient_netloc(url).lower()

        if len(host) >= 4 and host[0] == "[" and host[-1] == "]" and looks_like_ipv6(host[1:-1]):
            return DomainReading(host, "", host, "", ip_version=6,
                                 notes=["IPv6 literal host"])

        labels = host.split(".") if host else []
        match = self._trie.suffix_index(labels) if labels else None

        if match is None and len(labels) == 4 and looks_like_ipv4(host):
            return DomainReading(host, "", host, "", ip_version=4,
                                 notes=["IPv4 literal host"])

        if match is None:
            return DomainReading(
                host,
                subdomain=".".join(labels[:-1]),
                domain=labels[-1] if labels else "",
                suffix="",
                notes=["No public suffix matched"],
            )

        idx, is_private = match
        return DomainReading(
            host,
            subdomain=".".join(labels[: idx - 1]) if idx >= 2 else "",
            domain=labels[idx - 1] if idx > 0 else "",
            suffix=".".join(labels[idx:]),
            is_private_suffix=is_private,
        )

    def registered_domain(self, url: str) -> str:
        return self.perceive(url).registered_domain

    def same_owner(self, url_a: str, url_b: str) -> bool:
        """True when both URLs resolve to the same non-empty registered domain."""
        a = self.registered_domain(url_a)
        return bool(a) and a == self.registered_domain(url_b)
