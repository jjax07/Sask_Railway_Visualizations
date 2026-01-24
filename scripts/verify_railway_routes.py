#!/usr/bin/env python3
"""
Verify that railway route connections display correctly.

This script simulates what the JavaScript does and checks:
1. Can a path be found between settlements?
2. Does the path geometry get close to both settlements?
3. Are there any problematic connections that would fall back to straight lines?
"""

import json
import math
from collections import defaultdict
import heapq

def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in km."""
    R = 6371  # Earth's radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

def load_data():
    """Load all required data files."""
    with open('data/settlement_connections.json') as f:
        connections = json.load(f)
    with open('data/railway_network.json') as f:
        network = json.load(f)
    with open('data/railway_tracks.json') as f:
        tracks = json.load(f)
    with open('data/settlement_network_mapping.json') as f:
        mappings = json.load(f)
    return connections, network, tracks, mappings

def build_adjacency(network):
    """Build adjacency list from network."""
    adj = defaultdict(list)
    for e in network['edges']:
        adj[e['source']].append({'node': e['target'], 'weight': e['length_m']})
        adj[e['target']].append({'node': e['source'], 'weight': e['length_m']})
    return adj

def build_track_lookup(tracks):
    """Build track lookup by edge key."""
    lookup = {}
    for t in tracks['tracks']:
        lookup[f"{t['source']}|{t['target']}"] = t
        lookup[f"{t['target']}|{t['source']}"] = t
    return lookup

def build_mapping_lookup(mappings):
    """Build mapping lookup by settlement name."""
    return {m['settlement']: m for m in mappings['mappings']}

def find_path(start, end, adj):
    """Find shortest path using Dijkstra."""
    if start == end:
        return [start]

    dist = {start: 0}
    prev = {}
    visited = set()
    heap = [(0, start)]

    while heap:
        d, current = heapq.heappop(heap)
        if current in visited:
            continue
        visited.add(current)

        if current == end:
            break

        for neighbor_info in adj.get(current, []):
            neighbor = neighbor_info['node']
            weight = neighbor_info['weight']
            if neighbor in visited:
                continue
            new_dist = dist[current] + weight
            if neighbor not in dist or new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                prev[neighbor] = current
                heapq.heappush(heap, (new_dist, neighbor))

    if end not in prev and start != end:
        return None

    path = []
    current = end
    while current is not None:
        path.append(current)
        current = prev.get(current)
    path.reverse()
    return path

def get_path_geometry(path, track_lookup):
    """Get coordinates for a path."""
    if not path or len(path) < 2:
        return None

    all_coords = []
    for i in range(len(path) - 1):
        key = f"{path[i]}|{path[i+1]}"
        track = track_lookup.get(key)
        if track and track.get('coordinates'):
            coords = [[c[1], c[0]] for c in track['coordinates']]  # [lat, lon]

            if all_coords:
                last_point = all_coords[-1]
                first_point = coords[0]
                last_point_reversed = coords[-1]

                dist_to_first = abs(last_point[0] - first_point[0]) + abs(last_point[1] - first_point[1])
                dist_to_last = abs(last_point[0] - last_point_reversed[0]) + abs(last_point[1] - last_point_reversed[1])

                if dist_to_last < dist_to_first:
                    coords = coords[::-1]

            all_coords.extend(coords)

    return all_coords if all_coords else None

def extend_path_to_edge(coords, mapping, settlement_lat, settlement_lon, track_lookup, at_end):
    """Extend path to include partial edge geometry."""
    if not mapping.get('snap_nodes') or len(mapping['snap_nodes']) != 2:
        return coords

    node1, node2 = mapping['snap_nodes']
    edge_key = f"{node1}|{node2}"
    track = track_lookup.get(edge_key) or track_lookup.get(f"{node2}|{node1}")

    if not track or not track.get('coordinates'):
        return coords

    track_coords = [[c[1], c[0]] for c in track['coordinates']]

    # Find closest point on track to settlement
    min_dist = float('inf')
    closest_idx = 0
    for i, tc in enumerate(track_coords):
        dist = haversine(tc[0], tc[1], settlement_lat, settlement_lon)
        if dist < min_dist:
            min_dist = dist
            closest_idx = i

    # Check if extension would help
    current_endpoint = coords[-1] if at_end else coords[0]
    current_dist = haversine(current_endpoint[0], current_endpoint[1], settlement_lat, settlement_lon)

    if min_dist >= current_dist:
        return coords

    # Determine which end of track connects to path
    path_endpoint = coords[-1] if at_end else coords[0]
    dist_to_track_start = abs(path_endpoint[0] - track_coords[0][0]) + abs(path_endpoint[1] - track_coords[0][1])
    dist_to_track_end = abs(path_endpoint[0] - track_coords[-1][0]) + abs(path_endpoint[1] - track_coords[-1][1])

    if dist_to_track_start < dist_to_track_end:
        extension_coords = track_coords[:closest_idx + 1]
    else:
        extension_coords = track_coords[closest_idx:][::-1]

    if at_end:
        return coords + extension_coords[1:]
    else:
        return extension_coords[:-1] + coords

def find_closest_point_distance(coords, target_lat, target_lon):
    """Find minimum distance from any point on path to target."""
    min_dist = float('inf')
    for c in coords:
        dist = haversine(c[0], c[1], target_lat, target_lon)
        if dist < min_dist:
            min_dist = dist
    return min_dist

def verify_connection(from_name, to_name, from_data, to_data, mapping_lookup, adj, track_lookup):
    """Verify a single connection. Returns (success, issue_description, details)."""

    from_mapping = mapping_lookup.get(from_name)
    to_mapping = mapping_lookup.get(to_name)

    if not from_mapping:
        return False, "NO_MAPPING", f"{from_name} not in mapping data"
    if not to_mapping:
        return False, "NO_MAPPING", f"{to_name} not in mapping data"

    from_node = from_mapping['snap_node']
    to_node = to_mapping['snap_node']

    # Find path
    path = find_path(from_node, to_node, adj)
    if not path:
        return False, "NO_PATH", f"No path from {from_node} to {to_node}"

    # Get geometry
    coords = get_path_geometry(path, track_lookup)
    if not coords or len(coords) < 2:
        return False, "NO_GEOMETRY", f"No track geometry for path {path}"

    # Extend path for edge-snapped settlements
    coords = extend_path_to_edge(coords, from_mapping, from_data['lat'], from_data['lon'], track_lookup, False)
    coords = extend_path_to_edge(coords, to_mapping, to_data['lat'], to_data['lon'], track_lookup, True)

    # Check how close the path gets to each settlement
    from_dist = find_closest_point_distance(coords, from_data['lat'], from_data['lon'])
    to_dist = find_closest_point_distance(coords, to_data['lat'], to_data['lon'])

    # Thresholds for warnings
    WARN_THRESHOLD = 5  # km - warn if path doesn't get within 5km
    ERROR_THRESHOLD = 15  # km - error if path doesn't get within 15km

    issues = []
    if from_dist > ERROR_THRESHOLD:
        issues.append(f"Path {from_dist:.1f}km from {from_name}")
    elif from_dist > WARN_THRESHOLD:
        issues.append(f"Path {from_dist:.1f}km from {from_name} (warn)")

    if to_dist > ERROR_THRESHOLD:
        issues.append(f"Path {to_dist:.1f}km from {to_name}")
    elif to_dist > WARN_THRESHOLD:
        issues.append(f"Path {to_dist:.1f}km from {to_name} (warn)")

    if issues:
        max_dist = max(from_dist, to_dist)
        if max_dist > ERROR_THRESHOLD:
            return False, "FAR_FROM_PATH", "; ".join(issues)
        else:
            return True, "WARNING", "; ".join(issues)

    return True, "OK", f"Path within {max(from_dist, to_dist):.1f}km of both settlements"

def main():
    print("Loading data...")
    connections, network, tracks, mappings = load_data()

    adj = build_adjacency(network)
    track_lookup = build_track_lookup(tracks)
    mapping_lookup = build_mapping_lookup(mappings)

    settlements = connections['settlements']
    all_connections = connections['connections']

    print(f"Verifying {sum(len(v) for v in all_connections.values())} connections...\n")

    results = {
        'OK': [],
        'WARNING': [],
        'NO_MAPPING': [],
        'NO_PATH': [],
        'NO_GEOMETRY': [],
        'FAR_FROM_PATH': []
    }

    checked = set()  # Avoid checking A->B and B->A

    for from_name, conns in all_connections.items():
        from_data = settlements.get(from_name)
        if not from_data:
            continue

        for conn in conns:
            to_name = conn['to']

            # Skip if already checked reverse direction
            pair = tuple(sorted([from_name, to_name]))
            if pair in checked:
                continue
            checked.add(pair)

            to_data = settlements.get(to_name)
            if not to_data:
                continue

            success, issue_type, details = verify_connection(
                from_name, to_name, from_data, to_data,
                mapping_lookup, adj, track_lookup
            )

            results[issue_type].append({
                'from': from_name,
                'to': to_name,
                'details': details,
                'direct_distance': conn.get('distance_km', 0)
            })

    # Print summary
    print("=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"Total unique connections checked: {len(checked)}")
    print(f"  OK: {len(results['OK'])}")
    print(f"  Warnings: {len(results['WARNING'])}")
    print(f"  Errors: {len(results['NO_MAPPING']) + len(results['NO_PATH']) + len(results['NO_GEOMETRY']) + len(results['FAR_FROM_PATH'])}")
    print()

    # Print errors
    if results['NO_MAPPING']:
        print(f"\n--- NO MAPPING ({len(results['NO_MAPPING'])}) ---")
        for r in results['NO_MAPPING'][:10]:
            print(f"  {r['from']} -> {r['to']}: {r['details']}")
        if len(results['NO_MAPPING']) > 10:
            print(f"  ... and {len(results['NO_MAPPING']) - 10} more")

    if results['NO_PATH']:
        print(f"\n--- NO PATH ({len(results['NO_PATH'])}) ---")
        for r in results['NO_PATH'][:10]:
            print(f"  {r['from']} -> {r['to']}: {r['details']}")
        if len(results['NO_PATH']) > 10:
            print(f"  ... and {len(results['NO_PATH']) - 10} more")

    if results['NO_GEOMETRY']:
        print(f"\n--- NO GEOMETRY ({len(results['NO_GEOMETRY'])}) ---")
        for r in results['NO_GEOMETRY'][:10]:
            print(f"  {r['from']} -> {r['to']}: {r['details']}")
        if len(results['NO_GEOMETRY']) > 10:
            print(f"  ... and {len(results['NO_GEOMETRY']) - 10} more")

    if results['FAR_FROM_PATH']:
        print(f"\n--- FAR FROM PATH ({len(results['FAR_FROM_PATH'])}) ---")
        # Sort by how far the path is from settlements
        for r in sorted(results['FAR_FROM_PATH'], key=lambda x: x['details'], reverse=True)[:20]:
            print(f"  {r['from']} -> {r['to']} ({r['direct_distance']}km direct): {r['details']}")
        if len(results['FAR_FROM_PATH']) > 20:
            print(f"  ... and {len(results['FAR_FROM_PATH']) - 20} more")

    if results['WARNING']:
        print(f"\n--- WARNINGS ({len(results['WARNING'])}) ---")
        for r in results['WARNING'][:20]:
            print(f"  {r['from']} -> {r['to']}: {r['details']}")
        if len(results['WARNING']) > 20:
            print(f"  ... and {len(results['WARNING']) - 20} more")

    # Overall assessment
    print("\n" + "=" * 60)
    error_count = len(results['NO_MAPPING']) + len(results['NO_PATH']) + len(results['NO_GEOMETRY']) + len(results['FAR_FROM_PATH'])
    if error_count == 0 and len(results['WARNING']) == 0:
        print("All connections verified successfully!")
    elif error_count == 0:
        print(f"All connections OK, but {len(results['WARNING'])} have minor warnings.")
    else:
        print(f"{error_count} connections have issues that will show as straight lines.")
        print(f"{len(results['WARNING'])} connections have minor warnings.")

if __name__ == '__main__':
    main()
