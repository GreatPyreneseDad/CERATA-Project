"""
Community Detector - f-Dimension Coherence Cluster Detection
=============================================================

Nematocyst extracted from NetworkX's community detection algorithms.
Identifies coherence clusters - groups of nodes with shared f-dimension patterns.

Philosophy:
    Communities are not just "groups" - they are coherence clusters
    where belonging patterns (f-dimension) resonate together.
"""

from typing import Dict, List, Optional, Set, Any, Iterator
from dataclasses import dataclass, field
from enum import Enum

try:
    import networkx as nx
    from networkx.algorithms import community as nx_community
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    nx = None


class DetectionMethod(Enum):
    """Community detection algorithms"""
    LOUVAIN = "louvain"         # Modularity optimization (fast, good)
    LABEL_PROP = "label_prop"   # Label propagation (fast, stochastic)
    GREEDY = "greedy"           # Greedy modularity (deterministic)
    GIRVAN_NEWMAN = "girvan"    # Edge betweenness (slow, structural)


@dataclass
class CoherenceCluster:
    """
    A community reframed as a coherence cluster.
    
    Members share belonging patterns - their f-dimensions resonate.
    """
    id: int
    members: Set[Any]
    internal_f: float           # Average internal f-dimension
    boundary_f: float           # Average boundary f-dimension
    cohesion: float            # How tightly bound (internal density)
    separation: float          # How distinct from other clusters
    bridge_nodes: Set[Any]     # Nodes connecting to other clusters
    
    def __len__(self) -> int:
        return len(self.members)
    
    def __contains__(self, item: Any) -> bool:
        return item in self.members
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'members': list(self.members),
            'size': len(self.members),
            'internal_f': self.internal_f,
            'boundary_f': self.boundary_f,
            'cohesion': self.cohesion,
            'separation': self.separation,
            'bridge_nodes': list(self.bridge_nodes)
        }


class CommunityDetector:
    """
    Detect coherence clusters in relational networks.
    
    Rose Glass Interpretation:
        - Communities are coherence clusters
        - Members share f-dimension patterns
        - Bridges connect different coherence spaces
        - Clustering reveals belonging architecture
    """
    
    def __init__(self, 
                 method: DetectionMethod = DetectionMethod.LOUVAIN,
                 resolution: float = 1.0):
        """
        Initialize detector.
        
        Args:
            method: Community detection algorithm
            resolution: Resolution parameter (higher = more smaller clusters)
        """
        if not NETWORKX_AVAILABLE:
            raise ImportError("NetworkX not available")
        
        self.method = method
        self.resolution = resolution
    
    def find_coherence_clusters(self, 
                                 graph: nx.Graph) -> List[CoherenceCluster]:
        """
        Find coherence clusters in network.
        
        Args:
            graph: NetworkX graph (undirected preferred)
            
        Returns:
            List of CoherenceCluster objects
        """
        # Convert to undirected if needed
        if graph.is_directed():
            graph = graph.to_undirected()
        
        # Detect communities
        communities = self._detect_communities(graph)
        
        # Build coherence clusters
        clusters = []
        community_map = {}  # node -> cluster_id
        
        for i, community in enumerate(communities):
            for node in community:
                community_map[node] = i
        
        for i, community in enumerate(communities):
            cluster = self._build_cluster(
                graph, i, community, community_map
            )
            clusters.append(cluster)
        
        return sorted(clusters, key=lambda c: len(c), reverse=True)
    
    def _detect_communities(self, 
                            graph: nx.Graph) -> List[Set[Any]]:
        """Run community detection algorithm"""
        
        if self.method == DetectionMethod.LOUVAIN:
            try:
                communities = nx_community.louvain_communities(
                    graph, resolution=self.resolution
                )
                return list(communities)
            except:
                # Fallback to greedy
                self.method = DetectionMethod.GREEDY
        
        if self.method == DetectionMethod.GREEDY:
            communities = nx_community.greedy_modularity_communities(graph)
            return [set(c) for c in communities]
        
        if self.method == DetectionMethod.LABEL_PROP:
            communities = nx_community.label_propagation_communities(graph)
            return [set(c) for c in communities]
        
        if self.method == DetectionMethod.GIRVAN_NEWMAN:
            # Get first meaningful partition
            comp = nx_community.girvan_newman(graph)
            try:
                communities = next(comp)
                return [set(c) for c in communities]
            except StopIteration:
                return [set(graph.nodes())]
        
        # Default fallback
        return [set(graph.nodes())]
    
    def _build_cluster(self,
                       graph: nx.Graph,
                       cluster_id: int,
                       members: Set[Any],
                       community_map: Dict[Any, int]) -> CoherenceCluster:
        """Build CoherenceCluster from community"""
        
        # Calculate internal metrics
        subgraph = graph.subgraph(members)
        n_members = len(members)
        
        # Internal density (cohesion)
        if n_members > 1:
            internal_edges = subgraph.number_of_edges()
            max_internal = n_members * (n_members - 1) / 2
            cohesion = internal_edges / max_internal if max_internal > 0 else 0
        else:
            cohesion = 1.0
        
        # Find bridge nodes (connected to other clusters)
        bridge_nodes = set()
        external_edges = 0
        
        for node in members:
            for neighbor in graph.neighbors(node):
                if neighbor not in members:
                    bridge_nodes.add(node)
                    external_edges += 1
        
        # Separation (1 - external connectivity)
        if n_members > 0:
            max_external = n_members * (graph.number_of_nodes() - n_members)
            if max_external > 0:
                separation = 1 - (external_edges / max_external)
            else:
                separation = 1.0
        else:
            separation = 0.0
        
        # Internal f (average degree centrality within subgraph)
        if n_members > 1:
            internal_f = nx.density(subgraph)
        else:
            internal_f = 0.0
        
        # Boundary f (proportion that are bridges)
        boundary_f = len(bridge_nodes) / n_members if n_members > 0 else 0
        
        return CoherenceCluster(
            id=cluster_id,
            members=members,
            internal_f=internal_f,
            boundary_f=boundary_f,
            cohesion=cohesion,
            separation=separation,
            bridge_nodes=bridge_nodes
        )
    
    def get_modularity(self, 
                       graph: nx.Graph,
                       clusters: List[CoherenceCluster]) -> float:
        """
        Calculate modularity score of clustering.
        
        Higher modularity = better defined coherence clusters.
        """
        if graph.is_directed():
            graph = graph.to_undirected()
        
        communities = [c.members for c in clusters]
        try:
            return nx_community.modularity(graph, communities)
        except:
            return 0.0


class ConnectionPathfinder:
    """
    Find connection pathways through relational networks.
    
    Rose Glass Interpretation:
        - Paths are not just routes - they are coherence conduits
        - Shortest paths reveal strongest belonging connections
        - Path diversity shows relational resilience
    """
    
    def __init__(self):
        if not NETWORKX_AVAILABLE:
            raise ImportError("NetworkX not available")
    
    def find_shortest_path(self,
                           graph: nx.Graph,
                           source: Any,
                           target: Any,
                           weight: Optional[str] = 'weight') -> Optional[List[Any]]:
        """
        Find shortest coherence path between nodes.
        
        Uses edge weights as coherence strength (inverted for path finding).
        """
        try:
            # Invert weights (stronger connection = shorter path)
            if weight and nx.is_weighted(graph, weight=weight):
                path = nx.shortest_path(
                    graph, source, target, 
                    weight=lambda u, v, d: 1 / (d.get(weight, 1) + 0.01)
                )
            else:
                path = nx.shortest_path(graph, source, target)
            return path
        except nx.NetworkXNoPath:
            return None
        except:
            return None
    
    def find_all_paths(self,
                       graph: nx.Graph,
                       source: Any,
                       target: Any,
                       cutoff: int = 5) -> List[List[Any]]:
        """
        Find all simple paths up to cutoff length.
        
        Multiple paths = relational resilience.
        """
        try:
            paths = list(nx.all_simple_paths(
                graph, source, target, cutoff=cutoff
            ))
            return sorted(paths, key=len)
        except:
            return []
    
    def get_path_coherence(self,
                           graph: nx.Graph,
                           path: List[Any]) -> float:
        """
        Calculate coherence of a path.
        
        Path coherence = product of edge weights along path.
        """
        if len(path) < 2:
            return 1.0
        
        coherence = 1.0
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            if graph.has_edge(u, v):
                weight = graph[u][v].get('weight', 1.0)
                coherence *= weight
            else:
                coherence *= 0.5  # Penalty for missing edge
        
        return coherence


# Export main components
__all__ = [
    'CommunityDetector',
    'ConnectionPathfinder',
    'CoherenceCluster',
    'DetectionMethod'
]
