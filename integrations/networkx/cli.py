#!/usr/bin/env python3
"""
CLI wrapper for BelongingLens nematocyst.
Allows invocation from TypeScript MCP tools.
"""

import json
import sys
from typing import Dict, List, Any
import networkx as nx
from belonging_lens import BelongingLens

def main():
    """
    CLI entrypoint for BelongingLens.

    Expects JSON input on stdin:
    {
        "nodes": ["A", "B", "C", ...],
        "edges": [["A", "B"], ["B", "C"], ...],
        "node": "A",  // Optional: specific node to analyze
        "calibration": "modern_social|traditional_community|organizational|research_network",
        "directed": false
    }

    Outputs JSON to stdout:
    {
        "success": true,
        "reading": {...} or "readings": {...}
    }
    """
    try:
        # Read input
        input_data = json.loads(sys.stdin.read())

        nodes = input_data.get('nodes', [])
        edges = input_data.get('edges', [])
        target_node = input_data.get('node')
        calibration = input_data.get('calibration', 'modern_social')
        directed = input_data.get('directed', False)

        # Build graph
        G = nx.DiGraph() if directed else nx.Graph()
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)

        # Create lens
        lens = BelongingLens(cultural_calibration=calibration)

        # Perceive
        if target_node:
            # Single node analysis
            reading = lens.perceive_position(G, target_node)
            result = {
                'success': True,
                'reading': {
                    'f': reading.f,
                    'local_f': reading.local_f,
                    'bridge_f': reading.bridge_f,
                    'influence_f': reading.influence_f,
                    'reach_f': reading.reach_f,
                    'confidence': reading.confidence,
                    'node_id': reading.node_id,
                    'notes': reading.notes
                },
                'calibration': calibration
            }
        else:
            # All nodes analysis
            readings_dict = lens.perceive_network(G)

            # Convert to serializable format
            readings = {}
            for node_id, reading in readings_dict.items():
                readings[str(node_id)] = {
                    'f': reading.f,
                    'local_f': reading.local_f,
                    'bridge_f': reading.bridge_f,
                    'influence_f': reading.influence_f,
                    'reach_f': reading.reach_f,
                    'confidence': reading.confidence,
                    'node_id': reading.node_id,
                    'notes': reading.notes
                }

            result = {
                'success': True,
                'readings': readings,
                'node_count': len(readings),
                'calibration': calibration
            }

        print(json.dumps(result, indent=2))
        return 0

    except Exception as e:
        error_result = {
            'success': False,
            'error': str(e),
            'type': type(e).__name__
        }
        print(json.dumps(error_result, indent=2))
        return 1

if __name__ == '__main__':
    sys.exit(main())
