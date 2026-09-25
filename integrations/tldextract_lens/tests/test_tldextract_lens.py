"""Trial validation tests for the tldextract_lens integration.

Run from the repository root:
    python3 -m unittest discover -s integrations/tldextract_lens/tests
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools" / "security"))

from integrations.tldextract_lens import DomainLens, lenient_netloc  # noqa: E402
import phishguard  # noqa: E402
from phishguard import PhishGuard, ThreatLevel  # noqa: E402


class DomainLensTests(unittest.TestCase):
    lens = DomainLens()

    def parts(self, url):
        r = self.lens.perceive(url)
        return r.subdomain, r.domain, r.suffix

    def test_multi_label_public_suffix(self):
        self.assertEqual(self.parts("http://forums.bbc.co.uk/x"), ("forums", "bbc", "co.uk"))

    def test_brand_in_subdomain_belongs_to_attacker(self):
        r = self.lens.perceive("https://accounts.google.com.evil.io/login")
        self.assertEqual(r.registered_domain, "evil.io")
        self.assertEqual(r.subdomain, "accounts.google.com")

    def test_wildcard_and_exception_rules(self):
        # PSL: *.kawasaki.jp with exception !city.kawasaki.jp
        self.assertEqual(self.parts("a.b.kawasaki.jp"), ("", "a", "b.kawasaki.jp"))
        self.assertEqual(self.parts("www.city.kawasaki.jp"), ("www", "city", "kawasaki.jp"))

    def test_private_suffix_isolates_tenants(self):
        r = self.lens.perceive("https://evil.github.io/")
        self.assertEqual(r.registered_domain, "evil.github.io")
        self.assertTrue(r.is_private_suffix)
        public_only = DomainLens(include_private=False).perceive("https://evil.github.io/")
        self.assertEqual(public_only.registered_domain, "github.io")

    def test_ip_hosts(self):
        self.assertEqual(self.lens.perceive("http://192.168.1.5:5000/x").ip_version, 4)
        self.assertEqual(self.lens.perceive("http://[2001:db8::1]:80/").ip_version, 6)
        self.assertFalse(self.lens.perceive("http://999.1.1.1/").is_ip)

    def test_punycode_and_unicode(self):
        self.assertEqual(self.parts("http://xn--fiqs8s.xn--55qx5d.cn"),
                         ("", "xn--fiqs8s", "xn--55qx5d.cn"))
        self.assertEqual(self.parts("http://www.公司.cn"), ("", "www", "公司.cn"))

    def test_lenient_netloc(self):
        self.assertEqual(lenient_netloc("user:pw@WWW.Example.com:8080/p?q#f"), "WWW.Example.com")
        self.assertEqual(lenient_netloc("http://example.com./"), "example.com")

    def test_no_suffix(self):
        r = self.lens.perceive("localhost")
        self.assertEqual((r.domain, r.suffix, r.registered_domain), ("localhost", "", ""))

    def test_belongs_to_and_same_owner(self):
        self.assertTrue(self.lens.perceive("https://mail.google.com").belongs_to({"google.com"}))
        self.assertFalse(self.lens.perceive("https://evilgoogle.com").belongs_to({"google.com"}))
        self.assertTrue(self.lens.same_owner("a.example.co.uk", "https://b.example.co.uk/x"))

    def test_extra_suffixes_do_not_leak_into_shared_trie(self):
        custom = DomainLens(extra_suffixes=["corp.internal"])
        self.assertEqual(custom.perceive("app.team.corp.internal").registered_domain,
                         "team.corp.internal")
        self.assertEqual(DomainLens().perceive("app.team.corp.internal").registered_domain, "")


class PhishGuardExperimentalTests(unittest.TestCase):
    guard = PhishGuard(branch="experimental")

    def level(self, url, html=""):
        return self.guard.analyze(url, html_content=html).threat_level

    def test_legitimate_hosts_are_clean(self):
        for url in ["https://www.google.com", "https://accounts.google.com/signin",
                    "https://login.microsoftonline.com/", "https://github.com/login",
                    "https://www.nytimes.com/"]:
            with self.subTest(url=url):
                self.assertEqual(self.level(url), ThreatLevel.CLEAN)

    def test_brand_suffix_bypass_is_closed(self):
        # Gen 3 classic rated this CLEAN because it ends with 'google.com'.
        self.assertEqual(self.level("https://evilgoogle.com/login"), ThreatLevel.LIKELY_PHISH)

    def test_brand_in_subdomain(self):
        self.assertEqual(self.level("https://accounts.google.com.evil.io/"), ThreatLevel.LIKELY_PHISH)

    def test_ip_host_not_clean_without_html(self):
        # Gen 3 classic diluted the 0.6 URL score to 0.18 -> CLEAN.
        self.assertEqual(self.level("http://192.168.1.5/secure-login-verify"),
                         ThreatLevel.LIKELY_PHISH)

    def test_homoglyph_typosquat(self):
        analysis = self.guard.analyze_url("https://g00gle.com")
        self.assertIn("Possible typosquat of google.com", analysis["anomalies"])

    def test_short_brand_labels_do_not_flag_unrelated_domains(self):
        for url in ["https://ab.com", "https://love.com", "https://life.org"]:
            with self.subTest(url=url):
                self.assertEqual(self.level(url), ThreatLevel.CLEAN)

    def test_url_only_is_capped_at_likely_phish(self):
        url = "http://faceb00k-login.github.io.x.y.xyz:8443/neptune"
        self.assertEqual(self.guard.analyze_url(url)["risk_score"], 1.0)
        self.assertEqual(self.level(url), ThreatLevel.LIKELY_PHISH)

    def test_result_records_branch(self):
        self.assertEqual(self.guard.analyze("https://example.com").branch, "experimental")


class PhishGuardClassicTests(unittest.TestCase):
    """CLASSIC branch must keep Gen 3 behaviour for a fair trial."""

    guard = PhishGuard(branch="classic")

    def test_classic_behaviour_preserved(self):
        self.assertEqual(self.guard.analyze("https://evilgoogle.com/login").threat_level,
                         ThreatLevel.CLEAN)
        self.assertEqual(self.guard.analyze("http://192.168.1.5/x").threat_level,
                         ThreatLevel.CLEAN)
        self.assertEqual(self.guard.analyze("https://g00gle.com").threat_level,
                         ThreatLevel.SUSPICIOUS)
        self.assertNotIn("domain_reading", self.guard.analyze_url("https://g00gle.com"))

    def test_trial_mode_uses_both_branches(self):
        trial = PhishGuard(branch="trial")
        seen = {trial.analyze("https://example.com").branch for _ in range(64)}
        self.assertEqual(seen, {"classic", "experimental"})

    def test_invalid_branch_rejected(self):
        with self.assertRaises(ValueError):
            PhishGuard(branch="mutant")

    def test_falls_back_to_classic_without_lens(self):
        original = phishguard.DOMAIN_LENS_AVAILABLE
        phishguard.DOMAIN_LENS_AVAILABLE = False
        try:
            self.assertEqual(PhishGuard().branch, "classic")
        finally:
            phishguard.DOMAIN_LENS_AVAILABLE = original


if __name__ == "__main__":
    unittest.main()
