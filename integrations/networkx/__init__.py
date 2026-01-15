"""
Cerata NetworkX Integration
===========================

f-Dimension relational perception powered by NetworkX.

This integration metabolizes NetworkX's graph algorithms into 
Rose Glass dimensional perception. Graph centrality becomes
social belonging. Community detection becomes coherence clustering.

Nematocysts:
    - BelongingLens: f-dimension perception via centrality
    - CommunityDetector: Coherence cluster detection
    - ConnectionPathfinder: Relational pathway analysis
    - RelationalGraph: Rose Glass optimized graph wrapper

Philosophy:
    "We don't measure how central - we perceive how they belong."
    
    NetworkX algorithms are translated through cultural lenses,
    not treated as objective measurements. Each reading is a
    valid translation, not a score to be judged.

Usage:
    from integrations.networkx import BelongingLens, RelationalGraph
    
    graph = RelationalGraph()
    graph.add_interaction("alice", "bob", weight=0.8)
    graph.add_interaction("bob", "carol", weight=0.6)
    
    lens = BelongingLens(cultural_calibration="modern_social")
    reading = lens.perceive_position(graph.nx_graph, "bob")
    
    print(f"f-dimension: {reading.f}")
    print(f"Bridge position: {reading.bridge_f}")

Hunt Record:
    Target: networkx/networkx
    Coherence: 0.85 (PRIME PREY)
    Hunt Date: 2026-01-15
    Status: CONSUMED
    License: BSD-3-Clause
    
Author: Christopher MacGregor bin Joseph
Date: January 2026
"""

from .belonging_lens import (
    BelongingLens,
    RelationalGraph,
    FDimensionReading,
    NetworkArchitecture,
    BelongingAspect
)

from .community_detector import (
    CommunityDetector,
    ConnectionPathfinder,
    CoherenceCluster,
    DetectionMethod
)

__version__ = '1.0.0'
__author__ = 'Christopher MacGregor bin Joseph'
__prey__ = 'networkx/networkx'
__coherence__ = 0.85
__hunt_date__ = '2026-01-15'

__all__ = [
    # Version info
    '__version__',
    '__author__',
    '__prey__',
    '__coherence__',
    '__hunt_date__',
    
    # Belonging lens (centrality → f-dimension)
    'BelongingLens',
    'RelationalGraph',
    'FDimensionReading',
    'NetworkArchitecture',
    'BelongingAspect',
    
    # Community detection (coherence clusters)
    'CommunityDetector',
    'ConnectionPathfinder',
    'CoherenceCluster',
    'DetectionMethod',
]
