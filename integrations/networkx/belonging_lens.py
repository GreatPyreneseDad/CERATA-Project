"""
Belonging Lens - f-Dimension Perception via NetworkX
=====================================================

Nematocyst extracted from NetworkX's centrality algorithms.
Transforms graph metrics into Rose Glass f-dimension readings.

The f-dimension measures social belonging architecture:
- How an individual connects to collective structures
- Relational positioning within networks
- Bridge positions and influence flows
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import math

# NetworkX import with graceful fallback
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    nx = None


class BelongingAspect(Enum):
    """Aspects of f-dimension belonging"""
    LOCAL = "local"           # Direct connections (degree)
    BRIDGE = "bridge"         # Information flow control (betweenness)
    INFLUENCE = "influence"   # Recursive connection quality (eigenvector)
    REACH = "reach"           # Accessibility to network (closeness)


@dataclass
class FDimensionReading:
    """
    Rose Glass f-dimension reading from network analysis.
    
    Unlike raw centrality scores, these are normalized translations
    through the Rose Glass lens, not measurements.
    """
    f: float                  # Overall f-dimension (0.0-1.0)
    local_f: float            # Degree-based local belonging
    bridge_f: float           # Betweenness-based bridge position
    influence_f: float        # Eigenvector-based influence position
    reach_f: float            # Closeness-based accessibility
    
    confidence: float = 0.8   # Translation confidence
    node_id: Optional[str] = None
    notes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, float]:
        return {
            'f': self.f,
            'local_f': self.local_f,
            'bridge_f': self.bridge_f,
            'influence_f': self.influence_f,
            'reach_f': self.reach_f,
            'confidence': self.confidence
        }


@dataclass
class NetworkArchitecture:
    """Structural properties of a relational network"""
    density: float            # Edge density (0.0-1.0)
    clustering: float         # Average clustering coefficient
    components: int           # Number of connected components
    diameter: Optional[int]   # Longest shortest path (if connected)
    avg_path_length: Optional[float]  # Average shortest path
    nodes: int
    edges: int


class BelongingLens:
    """
    Rose Glass lens for perceiving f-dimension through network structure.
    
    Transforms NetworkX centrality algorithms into Rose Glass readings.
    Each centrality metric becomes an aspect of social belonging.
    
    Philosophy:
        - We don't measure "how central" someone is
        - We perceive "how they belong" to relational structures
        - Multiple valid readings exist through different lens calibrations
    """
    
    def __init__(self, 
                 weights: Optional[Dict[BelongingAspect, float]] = None,
                 cultural_calibration: str = "modern_social"):
        """
        Initialize the belonging lens.
        
        Args:
            weights: Custom weights for combining f-dimension aspects.
                    Default balances all four aspects equally.
            cultural_calibration: Cultural lens for interpretation.
                    Different cultures weight belonging aspects differently.
        """
        if not NETWORKX_AVAILABLE:
            raise ImportError(
                "NetworkX not available. Install with: pip install networkx"
            )
        
        # Default weights balance all aspects
        self.weights = weights or {
            BelongingAspect.LOCAL: 0.25,
            BelongingAspect.BRIDGE: 0.25,
            BelongingAspect.INFLUENCE: 0.25,
            BelongingAspect.REACH: 0.25
        }
        
        self.calibration = cultural_calibration
        self._apply_cultural_calibration()
    
    def _apply_cultural_calibration(self):
        """Adjust weights based on cultural lens"""
        calibrations = {
            "modern_social": {
                # Modern social networks value influence and reach
                BelongingAspect.LOCAL: 0.20,
                BelongingAspect.BRIDGE: 0.25,
                BelongingAspect.INFLUENCE: 0.30,
                BelongingAspect.REACH: 0.25
            },
            "traditional_community": {
                # Traditional communities value local bonds
                BelongingAspect.LOCAL: 0.40,
                BelongingAspect.BRIDGE: 0.15,
                BelongingAspect.INFLUENCE: 0.20,
                BelongingAspect.REACH: 0.25
            },
            "organizational": {
                # Organizations value bridge positions (gatekeepers)
                BelongingAspect.LOCAL: 0.20,
                BelongingAspect.BRIDGE: 0.40,
                BelongingAspect.INFLUENCE: 0.25,
                BelongingAspect.REACH: 0.15
            },
            "research_network": {
                # Research networks value influence (citations)
                BelongingAspect.LOCAL: 0.15,
                BelongingAspect.BRIDGE: 0.20,
                BelongingAspect.INFLUENCE: 0.45,
                BelongingAspect.REACH: 0.20
            }
        }
        
        if self.calibration in calibrations:
            self.weights = calibrations[self.calibration]
    
    def perceive_position(self, 
                          graph: nx.Graph, 
                          node: Any) -> FDimensionReading:
        """
        Perceive f-dimension reading for a specific node.
        
        This is TRANSLATION, not measurement. The same node viewed
        through different cultural calibrations yields different
        valid readings.
        
        Args:
            graph: NetworkX graph representing relational structure
            node: Node ID to analyze
            
        Returns:
            FDimensionReading with normalized f-dimension components
        """
        if node not in graph:
            return FDimensionReading(
                f=0.0, local_f=0.0, bridge_f=0.0, 
                influence_f=0.0, reach_f=0.0,
                confidence=0.0, node_id=str(node),
                notes=["Node not found in graph"]
            )
        
        notes = []
        n_nodes = graph.number_of_nodes()
        
        # Local belonging (degree centrality)
        degree_cent = nx.degree_centrality(graph)
        local_f = degree_cent.get(node, 0.0)
        
        # Bridge position (betweenness centrality)
        try:
            between_cent = nx.betweenness_centrality(graph)
            bridge_f = between_cent.get(node, 0.0)
        except Exception as e:
            bridge_f = 0.0
            notes.append(f"Betweenness calculation failed: {e}")
        
        # Influence position (eigenvector centrality)
        try:
            eigen_cent = nx.eigenvector_centrality(graph, max_iter=500)
            influence_f = eigen_cent.get(node, 0.0)
        except nx.PowerIterationFailedConvergence:
            # Fallback to degree for disconnected graphs
            influence_f = local_f * 0.8
            notes.append("Eigenvector fell back to degree approximation")
        except Exception as e:
            influence_f = 0.0
            notes.append(f"Eigenvector calculation failed: {e}")
        
        # Reach (closeness centrality)
        try:
            close_cent = nx.closeness_centrality(graph)
            reach_f = close_cent.get(node, 0.0)
        except Exception as e:
            reach_f = 0.0
            notes.append(f"Closeness calculation failed: {e}")
        
        # Apply biological optimization (prevent extremes)
        local_f = self._biological_optimize(local_f)
        bridge_f = self._biological_optimize(bridge_f)
        influence_f = self._biological_optimize(influence_f)
        reach_f = self._biological_optimize(reach_f)
        
        # Weighted combination for overall f
        f = (
            self.weights[BelongingAspect.LOCAL] * local_f +
            self.weights[BelongingAspect.BRIDGE] * bridge_f +
            self.weights[BelongingAspect.INFLUENCE] * influence_f +
            self.weights[BelongingAspect.REACH] * reach_f
        )
        
        # Confidence based on graph size and connectivity
        confidence = self._calculate_confidence(graph, node)
        
        return FDimensionReading(
            f=f,
            local_f=local_f,
            bridge_f=bridge_f,
            influence_f=influence_f,
            reach_f=reach_f,
            confidence=confidence,
            node_id=str(node),
            notes=notes
        )
    
    def perceive_network(self, 
                         graph: nx.Graph) -> Dict[Any, FDimensionReading]:
        """
        Perceive f-dimension readings for all nodes in network.
        
        Returns dict mapping node_id -> FDimensionReading
        """
        readings = {}
        
        # Calculate all centralities once (efficiency)
        degree_cent = nx.degree_centrality(graph)
        
        try:
            between_cent = nx.betweenness_centrality(graph)
        except:
            between_cent = {n: 0.0 for n in graph.nodes()}
        
        try:
            eigen_cent = nx.eigenvector_centrality(graph, max_iter=500)
        except:
            eigen_cent = degree_cent.copy()
        
        try:
            close_cent = nx.closeness_centrality(graph)
        except:
            close_cent = {n: 0.0 for n in graph.nodes()}
        
        for node in graph.nodes():
            local_f = self._biological_optimize(degree_cent.get(node, 0.0))
            bridge_f = self._biological_optimize(between_cent.get(node, 0.0))
            influence_f = self._biological_optimize(eigen_cent.get(node, 0.0))
            reach_f = self._biological_optimize(close_cent.get(node, 0.0))
            
            f = (
                self.weights[BelongingAspect.LOCAL] * local_f +
                self.weights[BelongingAspect.BRIDGE] * bridge_f +
                self.weights[BelongingAspect.INFLUENCE] * influence_f +
                self.weights[BelongingAspect.REACH] * reach_f
            )
            
            readings[node] = FDimensionReading(
                f=f,
                local_f=local_f,
                bridge_f=bridge_f,
                influence_f=influence_f,
                reach_f=reach_f,
                confidence=self._calculate_confidence(graph, node),
                node_id=str(node)
            )
        
        return readings
    
    def _biological_optimize(self, value: float, 
                             k_m: float = 0.5, 
                             v_max: float = 1.0) -> float:
        """
        Apply Michaelis-Menten biological optimization.
        
        Prevents extreme values, mirrors how biological systems
        naturally regulate against overstimulation.
        
        Args:
            value: Raw value to optimize
            k_m: Half-saturation constant
            v_max: Maximum velocity
            
        Returns:
            Biologically optimized value (0.0-1.0)
        """
        if value <= 0:
            return 0.0
        return (v_max * value) / (k_m + value)
    
    def _calculate_confidence(self, graph: nx.Graph, node: Any) -> float:
        """
        Calculate confidence in f-dimension reading.
        
        Confidence is higher for:
        - Larger networks (more context)
        - Well-connected nodes (more data)
        - Connected graphs (complete picture)
        """
        n_nodes = graph.number_of_nodes()
        n_edges = graph.number_of_edges()
        
        # Size factor (more nodes = more confidence, diminishing returns)
        size_factor = min(1.0, math.log10(n_nodes + 1) / 3)
        
        # Connectivity factor
        if n_nodes > 1:
            density = 2 * n_edges / (n_nodes * (n_nodes - 1))
        else:
            density = 0.0
        connectivity_factor = min(1.0, density * 2)
        
        # Node integration factor (how well connected is this node)
        degree = graph.degree(node)
        max_possible = n_nodes - 1
        if max_possible > 0:
            integration_factor = degree / max_possible
        else:
            integration_factor = 0.0
        
        # Weighted combination
        confidence = (
            0.4 * size_factor +
            0.3 * connectivity_factor +
            0.3 * integration_factor
        )
        
        return min(1.0, max(0.1, confidence))


class RelationalGraph:
    """
    Wrapper around NetworkX graph optimized for Rose Glass analysis.
    
    Provides semantic methods for building communication/interaction networks.
    """
    
    def __init__(self, directed: bool = False):
        """
        Initialize relational graph.
        
        Args:
            directed: Whether relationships have direction
        """
        if not NETWORKX_AVAILABLE:
            raise ImportError("NetworkX not available")
        
        self.graph = nx.DiGraph() if directed else nx.Graph()
        self.directed = directed
    
    def add_interaction(self, 
                        source: Any, 
                        target: Any,
                        weight: float = 1.0,
                        sentiment: Optional[float] = None,
                        **attrs):
        """
        Add an interaction edge between entities.
        
        Args:
            source: Source entity
            target: Target entity
            weight: Interaction strength (0.0-1.0)
            sentiment: Optional sentiment of interaction (-1.0 to 1.0)
            **attrs: Additional edge attributes
        """
        edge_attrs = {'weight': weight, **attrs}
        if sentiment is not None:
            edge_attrs['sentiment'] = sentiment
        
        if self.graph.has_edge(source, target):
            # Accumulate weights for repeated interactions
            current_weight = self.graph[source][target].get('weight', 0)
            edge_attrs['weight'] = min(1.0, current_weight + weight * 0.5)
        
        self.graph.add_edge(source, target, **edge_attrs)
    
    def add_entity(self, entity: Any, **attrs):
        """Add entity with attributes"""
        self.graph.add_node(entity, **attrs)
    
    def get_architecture(self) -> NetworkArchitecture:
        """
        Analyze the structural architecture of the network.
        
        Returns NetworkArchitecture with key structural metrics.
        """
        n_nodes = self.graph.number_of_nodes()
        n_edges = self.graph.number_of_edges()
        
        # Density
        if n_nodes > 1:
            max_edges = n_nodes * (n_nodes - 1)
            if not self.directed:
                max_edges //= 2
            density = n_edges / max_edges if max_edges > 0 else 0.0
        else:
            density = 0.0
        
        # Clustering (convert to undirected if needed)
        undirected = self.graph.to_undirected() if self.directed else self.graph
        try:
            clustering = nx.average_clustering(undirected)
        except:
            clustering = 0.0
        
        # Components
        if self.directed:
            components = nx.number_weakly_connected_components(self.graph)
        else:
            components = nx.number_connected_components(self.graph)
        
        # Diameter and average path length (only if connected)
        diameter = None
        avg_path_length = None
        
        if components == 1 and n_nodes > 1:
            try:
                if self.directed:
                    if nx.is_strongly_connected(self.graph):
                        diameter = nx.diameter(self.graph)
                        avg_path_length = nx.average_shortest_path_length(self.graph)
                else:
                    diameter = nx.diameter(self.graph)
                    avg_path_length = nx.average_shortest_path_length(self.graph)
            except:
                pass
        
        return NetworkArchitecture(
            density=density,
            clustering=clustering,
            components=components,
            diameter=diameter,
            avg_path_length=avg_path_length,
            nodes=n_nodes,
            edges=n_edges
        )
    
    @property
    def nx_graph(self) -> nx.Graph:
        """Access underlying NetworkX graph"""
        return self.graph


# Export main components
__all__ = [
    'BelongingLens',
    'RelationalGraph', 
    'FDimensionReading',
    'NetworkArchitecture',
    'BelongingAspect'
]
