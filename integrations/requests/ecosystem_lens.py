"""
Ecosystem Lens - f-Dimension Perception via Requests
=====================================================

Nematocyst extracted from psf/requests HTTP library.
Transforms network connectivity into Rose Glass f-dimension readings.

The f-dimension measures social belonging / ecosystem integration:
- How well an entity connects to its environment
- Reliability and consistency of connections
- Health of integration points
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import time

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None


class EndpointHealth(Enum):
    """Health status of an ecosystem connection."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ConnectionReading:
    """Rose Glass f-dimension reading for a connection."""
    f_score: float              # Overall f-dimension (0.0-1.0)
    latency_ms: float           # Response time
    reliability: float          # Success rate (0.0-1.0)
    health: EndpointHealth      # Categorical health
    notes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'f_score': self.f_score,
            'latency_ms': self.latency_ms,
            'reliability': self.reliability,
            'health': self.health.value
        }


@dataclass
class IntegrationCoherence:
    """Coherence assessment of ecosystem integration."""
    overall_f: float            # Aggregate f-dimension
    endpoints_tested: int       # Number of connections tested
    healthy_count: int          # Healthy connections
    degraded_count: int         # Degraded connections
    failed_count: int           # Failed connections
    ecosystem_strength: str     # "strong", "moderate", "weak"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'overall_f': self.overall_f,
            'endpoints_tested': self.endpoints_tested,
            'healthy_count': self.healthy_count,
            'degraded_count': self.degraded_count,
            'failed_count': self.failed_count,
            'ecosystem_strength': self.ecosystem_strength
        }


class EcosystemLens:
    """
    Rose Glass lens for perceiving f-dimension through network connectivity.
    
    Transforms HTTP requests into ecosystem belonging perception.
    Connection health becomes social integration measurement.
    
    Philosophy:
        "We don't just ping endpoints - we perceive belonging."
        
        An entity's connections to its ecosystem reveal how well
        it integrates, how reliable its relationships are.
    """
    
    def __init__(self, 
                 timeout: float = 10.0,
                 retries: int = 3,
                 backoff_factor: float = 0.5):
        """
        Initialize ecosystem lens with resilient connection handling.
        
        Args:
            timeout: Request timeout in seconds
            retries: Number of retry attempts
            backoff_factor: Exponential backoff multiplier
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError(
                "requests not available. Install with: pip install requests"
            )
        
        self.timeout = timeout
        self.session = requests.Session()
        
        # Configure retry strategy (metabolized from requests best practices)
        retry_strategy = Retry(
            total=retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def perceive_connection(self, url: str) -> ConnectionReading:
        """
        Perceive the f-dimension of a single connection.
        
        Args:
            url: Endpoint URL to assess
            
        Returns:
            ConnectionReading with ecosystem integration metrics
        """
        start_time = time.time()
        notes = []
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            latency_ms = (time.time() - start_time) * 1000
            
            # Assess based on response
            if response.status_code == 200:
                health = EndpointHealth.HEALTHY
                reliability = 1.0
                notes.append("Connection successful")
            elif response.status_code < 400:
                health = EndpointHealth.HEALTHY
                reliability = 0.9
                notes.append(f"Redirect/alternative response: {response.status_code}")
            elif response.status_code < 500:
                health = EndpointHealth.DEGRADED
                reliability = 0.5
                notes.append(f"Client error: {response.status_code}")
            else:
                health = EndpointHealth.UNHEALTHY
                reliability = 0.2
                notes.append(f"Server error: {response.status_code}")
            
            # Calculate f-score
            latency_score = max(0, 1.0 - (latency_ms / 5000))  # 5s = 0
            f_score = (reliability * 0.7) + (latency_score * 0.3)
            
        except requests.exceptions.Timeout:
            latency_ms = self.timeout * 1000
            health = EndpointHealth.UNHEALTHY
            reliability = 0.0
            f_score = 0.1
            notes.append("Connection timeout - endpoint unreachable")
            
        except requests.exceptions.ConnectionError:
            latency_ms = 0
            health = EndpointHealth.UNHEALTHY
            reliability = 0.0
            f_score = 0.0
            notes.append("Connection failed - no route to host")
            
        except Exception as e:
            latency_ms = 0
            health = EndpointHealth.UNKNOWN
            reliability = 0.0
            f_score = 0.1
            notes.append(f"Unknown error: {str(e)[:50]}")
        
        return ConnectionReading(
            f_score=round(f_score, 3),
            latency_ms=round(latency_ms, 2),
            reliability=reliability,
            health=health,
            notes=notes
        )
    
    def assess_ecosystem(self, urls: List[str]) -> IntegrationCoherence:
        """
        Assess overall ecosystem integration across multiple endpoints.
        
        Args:
            urls: List of endpoint URLs to assess
            
        Returns:
            IntegrationCoherence with aggregate f-dimension
        """
        if not urls:
            return IntegrationCoherence(
                overall_f=0.0,
                endpoints_tested=0,
                healthy_count=0,
                degraded_count=0,
                failed_count=0,
                ecosystem_strength="none"
            )
        
        readings = [self.perceive_connection(url) for url in urls]
        
        healthy = sum(1 for r in readings if r.health == EndpointHealth.HEALTHY)
        degraded = sum(1 for r in readings if r.health == EndpointHealth.DEGRADED)
        failed = sum(1 for r in readings if r.health in 
                     [EndpointHealth.UNHEALTHY, EndpointHealth.UNKNOWN])
        
        overall_f = sum(r.f_score for r in readings) / len(readings)
        
        # Determine ecosystem strength
        if overall_f >= 0.8:
            strength = "strong"
        elif overall_f >= 0.5:
            strength = "moderate"
        else:
            strength = "weak"
        
        return IntegrationCoherence(
            overall_f=round(overall_f, 3),
            endpoints_tested=len(urls),
            healthy_count=healthy,
            degraded_count=degraded,
            failed_count=failed,
            ecosystem_strength=strength
        )
    
    def close(self):
        """Close the session."""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False


__all__ = [
    'EcosystemLens',
    'ConnectionReading',
    'EndpointHealth',
    'IntegrationCoherence'
]
