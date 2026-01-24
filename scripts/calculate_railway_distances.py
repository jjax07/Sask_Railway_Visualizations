#!/usr/bin/env python3
"""
Calculate railway distances between connected settlements.

Step 3 of railway distance calculation:
- Use shortest path algorithm (Dijkstra) between settlement nodes
- Sum actual track lengths along path
- Store railway distances alongside haversine distances

Reads:
- data/railway_network.json - Network graph from Step 1
- data/settlement_network_mapping.json - Settlement to node mappings from Step 2
- data/settlement_connections.json - Existing connections with haversine distances

Outputs:
- data/settlement_connections.json - Updated with railway distances
"""

import json
import os
import networkx as nx

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
NETWORK_FILE = os.path.join(PROJECT_DIR, "data", "railway_network.json")
MAPPING_FILE = os.path.join(PROJECT_DIR, "data", "settlement_network_mapping.json")
CONNECTIONS_FILE = os.path.join(PROJECT_DIR, "data", "settlement_connections.json")


def load_network_graph():
    """Load railway network and build NetworkX graph."""
    with open(NETWORK_FILE, 'r') as f:
        network = json.load(f)

    # Build graph
    G = nx.Graph()

    # Add nodes
    for node in network['nodes']:
        G.add_node(node['id'], lat=node['lat'], lon=node['lon'])

    # Add edges with length as weight
    for edge in network['edges']:
        G.add_edge(
            edge['source'],
            edge['target'],
            weight=edge['length_m'],
            length_km=edge['length_km'],
            built_year=edge['built_year'],
            abandoned_year=edge['abandoned_year'],
            builder_name=edge['builder_name']
        )

    return G


def load_settlement_mappings():
    """Load settlement to node mappings."""
    with open(MAPPING_FILE, 'r') as f:
        data = json.load(f)

    # Build dict: settlement name -> node info
    mappings = {}
    for m in data['mappings']:
        mappings[m['settlement']] = {
            'node': m['snap_node'],
            'nodes': m['snap_nodes'],
            'snap_type': m['snap_type'],
            'edge_t': m.get('snap_edge_t'),
            'edge_length_km': m.get('snap_edge_length_km'),
            'distance_km': m['snap_distance_km'],
            'quality': m['snap_quality']
        }

    return mappings


def load_connections():
    """Load existing connections."""
    with open(CONNECTIONS_FILE, 'r') as f:
        return json.load(f)


def are_on_same_edge(mapping1, mapping2):
    """Check if two settlements are snapped to the same edge."""
    if mapping1['snap_type'] != 'edge' or mapping2['snap_type'] != 'edge':
        return False
    # Same edge if same nodes in either order
    nodes1 = set(mapping1['nodes'])
    nodes2 = set(mapping2['nodes'])
    return nodes1 == nodes2


def calculate_same_edge_distance(mapping1, mapping2):
    """Calculate distance between two settlements on the same edge."""
    t1 = mapping1['edge_t']
    t2 = mapping2['edge_t']
    edge_length = mapping1['edge_length_km']

    if t1 is None or t2 is None or edge_length is None:
        return None

    return abs(t2 - t1) * edge_length


def get_edge_offset(mapping):
    """
    Get the distance from settlement position to the primary snap node.
    Returns (offset_km, from_which_end) where from_which_end is 'start' or 'end'.
    """
    if mapping['snap_type'] != 'edge' or mapping.get('edge_t') is None:
        return 0, 'node'

    t = mapping['edge_t']
    edge_length = mapping.get('edge_length_km', 0)

    # Distance to start node (t=0) vs end node (t=1)
    dist_to_start = t * edge_length
    dist_to_end = (1 - t) * edge_length

    # Primary node is the first in snap_nodes (start of edge)
    # Return distance from settlement to that node
    return dist_to_start, 'start'


def calculate_railway_distance(G, node1, node2):
    """
    Calculate shortest railway distance between two nodes.
    Returns (distance_km, path) or (None, None) if no path exists.
    """
    try:
        # Use Dijkstra's algorithm with edge weight = length in meters
        path = nx.dijkstra_path(G, node1, node2, weight='weight')

        # Calculate total distance along path
        total_m = 0
        for i in range(len(path) - 1):
            edge_data = G[path[i]][path[i + 1]]
            total_m += edge_data['weight']

        return total_m / 1000, path

    except nx.NetworkXNoPath:
        return None, None


def main():
    print("=" * 60)
    print("Calculating Railway Distances - Step 3")
    print("=" * 60)

    # Load data
    print("\nLoading data...")
    G = load_network_graph()
    mappings = load_settlement_mappings()
    connections = load_connections()

    print(f"Network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    print(f"Mappings: {len(mappings)} settlements")
    print(f"Connections: {len(connections['connections'])} settlement entries")

    # Track statistics
    stats = {
        'total_pairs': 0,
        'calculated': 0,
        'same_edge': 0,
        'no_path': 0,
        'no_mapping': 0,
        'same_node': 0
    }

    # Track distance comparisons
    comparisons = []

    # Track calculated distances by pair (key = sorted tuple of names)
    pair_distances = {}

    # Process each settlement's connections
    print("\nCalculating railway distances...")

    processed_pairs = set()  # Track which pairs we've processed

    for settlement, conns in connections['connections'].items():
        if settlement not in mappings:
            continue

        mapping1 = mappings[settlement]
        node1 = mapping1['node']

        for conn in conns:
            other = conn['to']
            stats['total_pairs'] += 1

            # Skip if we've already processed this pair (bidirectional)
            pair_key = tuple(sorted([settlement, other]))
            if pair_key in processed_pairs:
                continue
            processed_pairs.add(pair_key)

            # Check if other settlement has a mapping
            if other not in mappings:
                stats['no_mapping'] += 1
                pair_distances[pair_key] = None
                continue

            mapping2 = mappings[other]
            node2 = mapping2['node']

            # Check if both settlements are on the same edge (check this first!)
            if are_on_same_edge(mapping1, mapping2):
                rail_dist = calculate_same_edge_distance(mapping1, mapping2)
                if rail_dist is not None:
                    stats['same_edge'] += 1
                    stats['calculated'] += 1
                    pair_distances[pair_key] = round(rail_dist, 1)

                    # Store comparison data
                    haversine = conn['distance_km']
                    ratio = rail_dist / haversine if haversine > 0 else 1.0
                    comparisons.append({
                        'from': settlement,
                        'to': other,
                        'haversine_km': haversine,
                        'railway_km': round(rail_dist, 1),
                        'ratio': round(ratio, 2),
                        'path_nodes': 0  # Same edge, no intermediate nodes
                    })
                    continue

            # Handle same node case (different edges meeting at same junction)
            if node1 == node2:
                stats['same_node'] += 1
                pair_distances[pair_key] = 0.0
                continue

            # Calculate railway distance via network routing
            rail_dist, path = calculate_railway_distance(G, node1, node2)

            if rail_dist is not None:
                stats['calculated'] += 1
                pair_distances[pair_key] = round(rail_dist, 1)

                # Store comparison data
                haversine = conn['distance_km']
                ratio = rail_dist / haversine if haversine > 0 else 1.0
                comparisons.append({
                    'from': settlement,
                    'to': other,
                    'haversine_km': haversine,
                    'railway_km': round(rail_dist, 1),
                    'ratio': round(ratio, 2),
                    'path_nodes': len(path)
                })
            else:
                stats['no_path'] += 1
                pair_distances[pair_key] = None

    # Apply calculated distances to ALL connections (both directions)
    for settlement, conns in connections['connections'].items():
        for conn in conns:
            other = conn['to']
            pair_key = tuple(sorted([settlement, other]))
            if pair_key in pair_distances:
                conn['railway_distance_km'] = pair_distances[pair_key]

    # Print statistics
    print("\n=== Calculation Statistics ===")
    print(f"Total connection pairs: {len(processed_pairs)}")
    print(f"Successfully calculated: {stats['calculated']}")
    print(f"  - Same edge (direct): {stats['same_edge']}")
    print(f"  - Via network routing: {stats['calculated'] - stats['same_edge']}")
    print(f"No path found: {stats['no_path']}")
    print(f"Same node (0 distance): {stats['same_node']}")
    print(f"Missing mapping: {stats['no_mapping']}")

    # Analyze distance comparisons
    if comparisons:
        ratios = [c['ratio'] for c in comparisons]
        avg_ratio = sum(ratios) / len(ratios)

        print("\n=== Distance Comparison (Railway vs Haversine) ===")
        print(f"Average ratio: {avg_ratio:.2f}x")
        print(f"Min ratio: {min(ratios):.2f}x")
        print(f"Max ratio: {max(ratios):.2f}x")

        # Show examples
        print("\n=== Sample Comparisons ===")

        # Closest to 1:1
        by_ratio = sorted(comparisons, key=lambda x: abs(x['ratio'] - 1.0))
        print("\nMost direct routes (ratio closest to 1.0):")
        for c in by_ratio[:5]:
            print(f"  {c['from']} -> {c['to']}: {c['haversine_km']}km direct, "
                  f"{c['railway_km']}km by rail ({c['ratio']}x)")

        # Highest ratio (most indirect)
        by_ratio_desc = sorted(comparisons, key=lambda x: -x['ratio'])
        print("\nMost indirect routes (highest ratio):")
        for c in by_ratio_desc[:5]:
            print(f"  {c['from']} -> {c['to']}: {c['haversine_km']}km direct, "
                  f"{c['railway_km']}km by rail ({c['ratio']}x)")

        # Major city examples
        print("\nMajor city connections:")
        major = ['Saskatoon', 'Regina', 'Prince Albert', 'Moosejaw']
        for c in comparisons:
            if c['from'] in major and c['to'] in major:
                print(f"  {c['from']} -> {c['to']}: {c['haversine_km']}km direct, "
                      f"{c['railway_km']}km by rail ({c['ratio']}x)")

    # Save updated connections
    print(f"\nSaving to {CONNECTIONS_FILE}")
    with open(CONNECTIONS_FILE, 'w') as f:
        json.dump(connections, f, indent=2)

    print("\n" + "=" * 60)
    print("Step 3 Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
