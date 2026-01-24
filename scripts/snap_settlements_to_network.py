#!/usr/bin/env python3
"""
Snap settlements to the railway network graph.

Step 2 of railway distance calculation:
- For each settlement, find nearest node on railway network
- Handle settlements that are off-network
- Create mapping: settlement → network node(s)

Reads:
- data/settlements.json - 429 settlements with coordinates
- data/railway_network.json - Network graph from Step 1

Outputs:
- data/settlement_network_mapping.json - Settlement to node mappings
"""

import json
import os
from pyproj import Transformer
from collections import defaultdict

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
SETTLEMENTS_FILE = os.path.join(PROJECT_DIR, "data", "settlements.json")
NETWORK_FILE = os.path.join(PROJECT_DIR, "data", "railway_network.json")
OUTPUT_FILE = os.path.join(PROJECT_DIR, "data", "settlement_network_mapping.json")

# Lambert Conformal Conic projection used by the network
LCC_PROJ = '+proj=lcc +lat_1=49 +lat_2=77 +lat_0=49 +lon_0=-95 +x_0=0 +y_0=0 +datum=NAD27 +units=m +no_defs'

# Distance thresholds (meters)
ON_NETWORK_THRESHOLD = 5000  # 5km - considered "on" the railway
NEAR_NETWORK_THRESHOLD = 15000  # 15km - close enough to snap
MAX_SNAP_DISTANCE = 50000  # 50km - maximum snap distance


def load_settlements():
    """Load settlements from JSON file."""
    with open(SETTLEMENTS_FILE, 'r') as f:
        return json.load(f)


def load_network():
    """Load railway network from JSON file."""
    with open(NETWORK_FILE, 'r') as f:
        return json.load(f)


def build_node_index(network, transformer):
    """Build a spatial index of network nodes in projected coordinates."""
    nodes = {}
    for node in network['nodes']:
        # Convert lat/lon to projected coords
        x, y = transformer.transform(node['lon'], node['lat'])
        nodes[node['id']] = {
            'x': x,
            'y': y,
            'lat': node['lat'],
            'lon': node['lon']
        }
    return nodes


def find_nearest_node(x, y, nodes):
    """Find the nearest network node to a point."""
    min_dist = float('inf')
    nearest_id = None

    for node_id, node in nodes.items():
        dx = node['x'] - x
        dy = node['y'] - y
        dist = (dx * dx + dy * dy) ** 0.5

        if dist < min_dist:
            min_dist = dist
            nearest_id = node_id

    return nearest_id, min_dist


def find_nearest_edge_point(x, y, network, nodes):
    """
    Find the nearest point on any edge to the given point.
    Returns (edge_endpoints, distance, t_parameter, edge_length_km).
    t_parameter is 0-1 position along the edge from source to target.
    """
    min_dist = float('inf')
    best_edge = None
    best_t = 0
    best_edge_length = 0

    for edge in network['edges']:
        source = nodes[edge['source']]
        target = nodes[edge['target']]

        # Calculate distance from point to line segment and t parameter
        dist, t = point_to_segment_distance_with_t(
            x, y,
            source['x'], source['y'],
            target['x'], target['y']
        )

        if dist < min_dist:
            min_dist = dist
            best_edge = (edge['source'], edge['target'])
            best_t = t
            best_edge_length = edge['length_km']

    return best_edge, min_dist, best_t, best_edge_length


def point_to_segment_distance_with_t(px, py, x1, y1, x2, y2):
    """
    Calculate the shortest distance from point (px, py) to line segment (x1,y1)-(x2,y2).
    Returns (distance, t) where t is the parameter (0-1) along the segment.
    """
    dx = x2 - x1
    dy = y2 - y1

    if dx == 0 and dy == 0:
        # Segment is a point
        return ((px - x1) ** 2 + (py - y1) ** 2) ** 0.5, 0.0

    # Parameter t for the projection of point onto the line
    t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))

    # Nearest point on segment
    nearest_x = x1 + t * dx
    nearest_y = y1 + t * dy

    return ((px - nearest_x) ** 2 + (py - nearest_y) ** 2) ** 0.5, t


def classify_snap_quality(distance_m):
    """Classify the quality of the snap based on distance."""
    if distance_m <= ON_NETWORK_THRESHOLD:
        return "on_network"  # Settlement is on or very close to railway
    elif distance_m <= NEAR_NETWORK_THRESHOLD:
        return "near_network"  # Close enough to be a railway town
    elif distance_m <= MAX_SNAP_DISTANCE:
        return "distant"  # Far but still snappable
    else:
        return "off_network"  # Too far to reasonably snap


def main():
    print("=" * 60)
    print("Snapping Settlements to Railway Network - Step 2")
    print("=" * 60)

    # Load data
    print("\nLoading data...")
    settlements = load_settlements()
    network = load_network()

    print(f"Loaded {len(settlements)} settlements")
    print(f"Loaded {network['stats']['node_count']} network nodes")

    # Create transformer
    transformer = Transformer.from_crs('EPSG:4326', LCC_PROJ, always_xy=True)

    # Build node index
    nodes = build_node_index(network, transformer)

    # Process each settlement
    print("\nSnapping settlements to network...")

    mappings = []
    stats = defaultdict(int)

    for settlement in settlements:
        name = settlement['name']
        lat = settlement['lat']
        lon = settlement['lon']

        # Convert to projected coords
        x, y = transformer.transform(lon, lat)

        # Find nearest node
        nearest_node, node_dist = find_nearest_node(x, y, nodes)

        # Find nearest edge (for potentially better snap)
        nearest_edge, edge_dist, edge_t, edge_length_km = find_nearest_edge_point(x, y, network, nodes)

        # Use whichever is closer
        if edge_dist < node_dist:
            snap_distance = edge_dist
            snap_type = "edge"
            snap_nodes = list(nearest_edge)
            snap_edge_t = edge_t
            snap_edge_length_km = edge_length_km
        else:
            snap_distance = node_dist
            snap_type = "node"
            snap_nodes = [nearest_node]
            snap_edge_t = None
            snap_edge_length_km = None

        # Classify quality
        quality = classify_snap_quality(snap_distance)
        stats[quality] += 1

        # Get node coordinates for output
        primary_node = snap_nodes[0]
        node_data = nodes[primary_node]

        mapping = {
            'settlement': name,
            'lat': lat,
            'lon': lon,
            'snap_node': primary_node,
            'snap_nodes': snap_nodes,
            'snap_type': snap_type,
            'snap_edge_t': round(snap_edge_t, 4) if snap_edge_t is not None else None,
            'snap_edge_length_km': snap_edge_length_km,
            'snap_distance_m': round(snap_distance, 1),
            'snap_distance_km': round(snap_distance / 1000, 2),
            'snap_quality': quality,
            'node_lat': node_data['lat'],
            'node_lon': node_data['lon'],
            'railway_arrives': settlement.get('railway_arrives'),
            'first_railway': settlement.get('first_railway')
        }
        mappings.append(mapping)

    # Sort by settlement name
    mappings.sort(key=lambda m: m['settlement'])

    # Print statistics
    print("\n=== Snap Quality Statistics ===")
    for quality in ['on_network', 'near_network', 'distant', 'off_network']:
        count = stats[quality]
        pct = count / len(settlements) * 100
        print(f"  {quality}: {count} ({pct:.1f}%)")

    # Print distance statistics
    distances = [m['snap_distance_km'] for m in mappings]
    print(f"\n=== Distance Statistics ===")
    print(f"  Min: {min(distances):.2f} km")
    print(f"  Max: {max(distances):.2f} km")
    print(f"  Avg: {sum(distances)/len(distances):.2f} km")
    print(f"  Median: {sorted(distances)[len(distances)//2]:.2f} km")

    # Show some examples
    print("\n=== Sample Mappings ===")

    # Show closest snaps
    by_distance = sorted(mappings, key=lambda m: m['snap_distance_m'])
    print("\nClosest to network:")
    for m in by_distance[:5]:
        print(f"  {m['settlement']}: {m['snap_distance_km']}km to {m['snap_node']}")

    # Show furthest snaps
    print("\nFurthest from network:")
    for m in by_distance[-5:]:
        print(f"  {m['settlement']}: {m['snap_distance_km']}km to {m['snap_node']}")

    # Show major cities
    print("\nMajor cities:")
    major_cities = ['Saskatoon', 'Regina', 'Moose Jaw', 'Prince Albert', 'Swift Current']
    for city in major_cities:
        m = next((m for m in mappings if m['settlement'] == city), None)
        if m:
            print(f"  {m['settlement']}: {m['snap_distance_km']}km to {m['snap_node']} ({m['snap_quality']})")

    # Build output
    output = {
        'metadata': {
            'description': 'Settlement to railway network node mappings',
            'thresholds': {
                'on_network_m': ON_NETWORK_THRESHOLD,
                'near_network_m': NEAR_NETWORK_THRESHOLD,
                'max_snap_m': MAX_SNAP_DISTANCE
            }
        },
        'stats': {
            'total_settlements': len(settlements),
            'by_quality': dict(stats),
            'distance_km': {
                'min': round(min(distances), 2),
                'max': round(max(distances), 2),
                'avg': round(sum(distances) / len(distances), 2)
            }
        },
        'mappings': mappings
    }

    # Write output
    print(f"\nWriting output to {OUTPUT_FILE}")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Wrote {len(mappings)} settlement mappings")

    print("\n" + "=" * 60)
    print("Step 2 Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
