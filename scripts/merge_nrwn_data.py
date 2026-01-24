#!/usr/bin/env python3
"""
Merge NRWN (National Railway Network) shortline data into existing railway network.

Adds tracks from:
- Last Mountain Railway (LMR) - Craik subdivision (32 segments)
- Great Western Railway (GWR) - Shaunavon subdivision (166 segments)

This reduces FAR_FROM_PATH errors by adding shortline tracks not present in the
historical GEORIA dataset.

Reads:
- KnowledgeGraph/nrwn_rfn_sk_gml_en/NRWN_SK_2_0_eng.gml (NRWN data)
- data/railway_network.json (existing network)
- data/railway_tracks.json (existing track geometries)

Outputs:
- data/railway_network.json (updated with new nodes/edges)
- data/railway_tracks.json (updated with new track geometries)
"""

import json
import os
import math
import xml.etree.ElementTree as ET
from collections import defaultdict

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
NRWN_GML_PATH = os.path.join(
    os.path.dirname(PROJECT_DIR),
    "KnowledgeGraph",
    "nrwn_rfn_sk_gml_en",
    "NRWN_SK_2_0_eng.gml"
)
NETWORK_FILE = os.path.join(PROJECT_DIR, "data", "railway_network.json")
TRACKS_FILE = os.path.join(PROJECT_DIR, "data", "railway_tracks.json")

# Target operators to extract
TARGET_OPERATORS = {'LMR', 'GWR'}

# Track classifications to include (skip sidings/yards initially)
INCLUDE_CLASSIFICATIONS = {'Main', 'Siding'}

# Junction detection tolerance (meters)
# Using 500m since historical and NRWN data have different coordinate origins
JUNCTION_TOLERANCE = 500.0

# New node IDs start at this number
NEW_NODE_START = 500

# Earth radius for haversine calculation (meters)
EARTH_RADIUS_M = 6371000


def haversine_distance(lon1, lat1, lon2, lat2):
    """Calculate distance between two points in meters using haversine formula."""
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS_M * c


def parse_poslist(poslist_text):
    """
    Parse GML posList into list of [lon, lat] coordinates.

    NRWN format: "lon1 lat1 lon2 lat2 lon3 lat3 ..."
    Output format: [[lon1, lat1], [lon2, lat2], ...]
    """
    values = poslist_text.strip().split()
    coords = []
    for i in range(0, len(values), 2):
        lon = float(values[i])
        lat = float(values[i + 1])
        coords.append([lon, lat])
    return coords


def parse_nrwn_gml(gml_path):
    """
    Parse NRWN GML file and extract tracks for target operators.

    Returns list of track dicts with:
    - operator: LMR or GWR
    - subdivision: subdivision name
    - classification: Main, Siding, etc.
    - coordinates: [[lon, lat], ...]
    """
    print(f"Parsing NRWN GML file: {gml_path}")

    # Define namespaces
    namespaces = {
        'gml': 'http://www.opengis.net/gml',
        'fme': 'http://www.safe.com/gml/fme'
    }

    tracks = []

    # Parse with iterparse for memory efficiency
    context = ET.iterparse(gml_path, events=('end',))

    for event, elem in context:
        # Check for Track elements
        if elem.tag == '{http://www.safe.com/gml/fme}Track':
            # Extract operator
            operator_elem = elem.find('fme:operatorReportingMark', namespaces)
            if operator_elem is None or operator_elem.text not in TARGET_OPERATORS:
                elem.clear()
                continue

            operator = operator_elem.text

            # Extract classification
            class_elem = elem.find('fme:trackClassification', namespaces)
            classification = class_elem.text if class_elem is not None else 'Unknown'

            if classification not in INCLUDE_CLASSIFICATIONS:
                elem.clear()
                continue

            # Extract subdivision
            subdiv_elem = elem.find('fme:subdivision1Name', namespaces)
            subdivision = subdiv_elem.text if subdiv_elem is not None else 'Unknown'

            # Extract coordinates from posList
            poslist_elem = elem.find('.//gml:posList', namespaces)
            if poslist_elem is None or not poslist_elem.text:
                elem.clear()
                continue

            coordinates = parse_poslist(poslist_elem.text)
            if len(coordinates) < 2:
                elem.clear()
                continue

            tracks.append({
                'operator': operator,
                'subdivision': subdivision,
                'classification': classification,
                'coordinates': coordinates
            })

            elem.clear()

    print(f"  Extracted {len(tracks)} tracks")

    # Count by operator
    by_operator = defaultdict(int)
    for t in tracks:
        by_operator[t['operator']] += 1
    for op, count in sorted(by_operator.items()):
        print(f"    {op}: {count} segments")

    return tracks


def load_existing_network():
    """Load existing railway network and track geometries."""
    print(f"Loading existing network from {NETWORK_FILE}")
    with open(NETWORK_FILE, 'r') as f:
        network = json.load(f)

    print(f"Loading existing tracks from {TRACKS_FILE}")
    with open(TRACKS_FILE, 'r') as f:
        tracks = json.load(f)

    print(f"  Existing nodes: {len(network['nodes'])}")
    print(f"  Existing edges: {len(network['edges'])}")
    print(f"  Existing tracks: {tracks['track_count']}")

    return network, tracks


def find_junction_node(lon, lat, existing_nodes, tolerance=JUNCTION_TOLERANCE):
    """
    Find an existing node within tolerance of the given point.

    Returns (node_id, distance) or (None, None) if no match.
    """
    for node in existing_nodes:
        dist = haversine_distance(lon, lat, node['lon'], node['lat'])
        if dist < tolerance:
            return node['id'], dist
    return None, None


def calculate_track_length(coordinates):
    """Calculate total length of a track in km from its coordinates."""
    total = 0
    for i in range(len(coordinates) - 1):
        lon1, lat1 = coordinates[i]
        lon2, lat2 = coordinates[i + 1]
        total += haversine_distance(lon1, lat1, lon2, lat2)
    return total / 1000  # Convert to km


def find_nearby_endpoint(lon, lat, tracks, used, tolerance_m=50):
    """Find a track with an endpoint within tolerance of the given point."""
    for i, track in enumerate(tracks):
        if used[i]:
            continue

        # Check start point
        start_lon, start_lat = track['coordinates'][0]
        dist = haversine_distance(lon, lat, start_lon, start_lat)
        if dist < tolerance_m:
            return i, 'start', dist

        # Check end point
        end_lon, end_lat = track['coordinates'][-1]
        dist = haversine_distance(lon, lat, end_lon, end_lat)
        if dist < tolerance_m:
            return i, 'end', dist

    return None, None, None


def merge_consecutive_segments(nrwn_tracks):
    """
    Merge consecutive NRWN segments that share endpoints.

    Uses tolerance-based matching to handle coordinate gaps.
    Returns list of merged tracks with combined coordinates.
    """
    print("Merging consecutive segments...")

    # Tolerance for matching endpoints (meters)
    MERGE_TOLERANCE = 100.0

    # Group by operator
    by_operator = defaultdict(list)
    for track in nrwn_tracks:
        by_operator[track['operator']].append(track)

    merged_all = []

    for operator, tracks in by_operator.items():
        print(f"  Processing {operator}: {len(tracks)} segments")

        # Track which segments have been used
        used = [False] * len(tracks)

        # Build chains
        chains = []
        for i, track in enumerate(tracks):
            if used[i]:
                continue

            # Start a new chain
            chain_coords = list(track['coordinates'])
            chain_subdivisions = {track['subdivision']}
            chain_classifications = {track['classification']}
            used[i] = True

            # Extend forward (from end)
            changed = True
            while changed:
                changed = False
                end_lon, end_lat = chain_coords[-1]

                # Find a track with an endpoint near our end
                j, endpoint_type, dist = find_nearby_endpoint(
                    end_lon, end_lat, tracks, used, MERGE_TOLERANCE
                )

                if j is not None:
                    if endpoint_type == 'start':
                        # Append this segment (skip first point to avoid duplicate)
                        chain_coords.extend(tracks[j]['coordinates'][1:])
                    else:
                        # Append reversed segment (skip first point)
                        reversed_coords = list(reversed(tracks[j]['coordinates']))
                        chain_coords.extend(reversed_coords[1:])

                    chain_subdivisions.add(tracks[j]['subdivision'])
                    chain_classifications.add(tracks[j]['classification'])
                    used[j] = True
                    changed = True

            # Extend backward (from start)
            changed = True
            while changed:
                changed = False
                start_lon, start_lat = chain_coords[0]

                # Find a track with an endpoint near our start
                j, endpoint_type, dist = find_nearby_endpoint(
                    start_lon, start_lat, tracks, used, MERGE_TOLERANCE
                )

                if j is not None:
                    if endpoint_type == 'end':
                        # Prepend this segment (skip last point)
                        chain_coords = tracks[j]['coordinates'][:-1] + chain_coords
                    else:
                        # Prepend reversed segment (skip last point)
                        reversed_coords = list(reversed(tracks[j]['coordinates']))
                        chain_coords = reversed_coords[:-1] + chain_coords

                    chain_subdivisions.add(tracks[j]['subdivision'])
                    chain_classifications.add(tracks[j]['classification'])
                    used[j] = True
                    changed = True

            chains.append({
                'operator': operator,
                'subdivision': ', '.join(sorted(chain_subdivisions)),
                'classification': 'Main' if 'Main' in chain_classifications else list(chain_classifications)[0],
                'coordinates': chain_coords
            })

        # Second pass: merge chains that have nearby endpoints
        print(f"    Initial chains: {len(chains)}")

        chain_used = [False] * len(chains)
        final_chains = []

        for i, chain in enumerate(chains):
            if chain_used[i]:
                continue

            merged_coords = list(chain['coordinates'])
            merged_subdivs = set(chain['subdivision'].split(', '))
            merged_class = chain['classification']
            chain_used[i] = True

            # Try to extend this chain by connecting to other chains
            changed = True
            while changed:
                changed = False
                start_lon, start_lat = merged_coords[0]
                end_lon, end_lat = merged_coords[-1]

                for j, other_chain in enumerate(chains):
                    if chain_used[j]:
                        continue

                    other_start = other_chain['coordinates'][0]
                    other_end = other_chain['coordinates'][-1]

                    # Check all 4 connection possibilities
                    # Our end to their start
                    dist = haversine_distance(end_lon, end_lat, other_start[0], other_start[1])
                    if dist < MERGE_TOLERANCE:
                        merged_coords.extend(other_chain['coordinates'][1:])
                        merged_subdivs.update(other_chain['subdivision'].split(', '))
                        chain_used[j] = True
                        changed = True
                        break

                    # Our end to their end (reverse other)
                    dist = haversine_distance(end_lon, end_lat, other_end[0], other_end[1])
                    if dist < MERGE_TOLERANCE:
                        reversed_coords = list(reversed(other_chain['coordinates']))
                        merged_coords.extend(reversed_coords[1:])
                        merged_subdivs.update(other_chain['subdivision'].split(', '))
                        chain_used[j] = True
                        changed = True
                        break

                    # Our start to their end
                    dist = haversine_distance(start_lon, start_lat, other_end[0], other_end[1])
                    if dist < MERGE_TOLERANCE:
                        merged_coords = other_chain['coordinates'][:-1] + merged_coords
                        merged_subdivs.update(other_chain['subdivision'].split(', '))
                        chain_used[j] = True
                        changed = True
                        break

                    # Our start to their start (reverse other)
                    dist = haversine_distance(start_lon, start_lat, other_start[0], other_start[1])
                    if dist < MERGE_TOLERANCE:
                        reversed_coords = list(reversed(other_chain['coordinates']))
                        merged_coords = reversed_coords[:-1] + merged_coords
                        merged_subdivs.update(other_chain['subdivision'].split(', '))
                        chain_used[j] = True
                        changed = True
                        break

            final_chains.append({
                'operator': operator,
                'subdivision': ', '.join(sorted(merged_subdivs)),
                'classification': merged_class,
                'coordinates': merged_coords
            })

        print(f"    Merged into {len(final_chains)} chains")
        merged_all.extend(final_chains)

    return merged_all


def integrate_nrwn_tracks(nrwn_tracks, network, tracks_data):
    """
    Integrate NRWN tracks into existing network.

    - Finds junctions with existing network (reuse node IDs)
    - Creates new nodes for non-junction endpoints
    - Adds edges and track geometries
    """
    print("Integrating NRWN tracks into network...")

    existing_nodes = network['nodes']
    existing_edges = network['edges']
    existing_tracks = tracks_data['tracks']

    # Find the highest existing node number
    max_node_num = 0
    for node in existing_nodes:
        if node['id'].startswith('n'):
            try:
                num = int(node['id'][1:])
                max_node_num = max(max_node_num, num)
            except ValueError:
                pass

    next_node_num = max(max_node_num + 1, NEW_NODE_START)
    print(f"  New nodes will start at n{next_node_num}")

    # Track new nodes and edges
    new_nodes = []
    new_edges = []
    new_tracks = []

    # Map coordinates to node IDs (for reusing endpoints)
    coord_to_node = {}

    # Index existing nodes by coordinate for junction detection
    for node in existing_nodes:
        key = (round(node['lon'], 5), round(node['lat'], 5))
        coord_to_node[key] = node['id']

    junction_count = 0

    for track in nrwn_tracks:
        coords = track['coordinates']
        if len(coords) < 2:
            continue

        # Get or create source node
        start_lon, start_lat = coords[0]
        start_key = (round(start_lon, 5), round(start_lat, 5))

        if start_key in coord_to_node:
            source_id = coord_to_node[start_key]
        else:
            # Check for junction with existing network
            junction_id, junction_dist = find_junction_node(start_lon, start_lat, existing_nodes)
            if junction_id:
                source_id = junction_id
                junction_count += 1
                print(f"    Junction found: {track['operator']} start -> {junction_id} ({junction_dist:.0f}m)")
            else:
                source_id = f"n{next_node_num}"
                new_nodes.append({
                    'id': source_id,
                    'lat': start_lat,
                    'lon': start_lon,
                    'x': 0,  # Will be filled if needed
                    'y': 0
                })
                coord_to_node[start_key] = source_id
                next_node_num += 1

        # Get or create target node
        end_lon, end_lat = coords[-1]
        end_key = (round(end_lon, 5), round(end_lat, 5))

        if end_key in coord_to_node:
            target_id = coord_to_node[end_key]
        else:
            # Check for junction with existing network
            junction_id, junction_dist = find_junction_node(end_lon, end_lat, existing_nodes)
            if junction_id:
                target_id = junction_id
                junction_count += 1
                print(f"    Junction found: {track['operator']} end -> {junction_id} ({junction_dist:.0f}m)")
            else:
                target_id = f"n{next_node_num}"
                new_nodes.append({
                    'id': target_id,
                    'lat': end_lat,
                    'lon': end_lon,
                    'x': 0,
                    'y': 0
                })
                coord_to_node[end_key] = target_id
                next_node_num += 1

        # Skip self-loops
        if source_id == target_id:
            continue

        # Check if edge already exists
        edge_exists = False
        for edge in existing_edges + new_edges:
            if ((edge['source'] == source_id and edge['target'] == target_id) or
                (edge['source'] == target_id and edge['target'] == source_id)):
                edge_exists = True
                break

        if edge_exists:
            continue

        # Calculate track length
        length_km = calculate_track_length(coords)
        length_m = length_km * 1000

        # Determine builder name
        if track['operator'] == 'LMR':
            builder_name = 'LMR'
            builder_code = 'LMR'
        else:
            builder_name = 'GWR'
            builder_code = 'GWR'

        # Add edge
        new_edges.append({
            'source': source_id,
            'target': target_id,
            'length_m': round(length_m, 1),
            'length_km': round(length_km, 2),
            'built_year': 0,
            'abandoned_year': 0,
            'builder_code': builder_code,
            'builder_name': builder_name
        })

        # Add track geometry
        new_tracks.append({
            'source': source_id,
            'target': target_id,
            'coordinates': coords,
            'built_year': 0,
            'abandoned_year': 0,
            'builder_name': builder_name,
            'length_km': round(length_km, 2)
        })

    print(f"  Junctions with existing network: {junction_count}")
    print(f"  New nodes: {len(new_nodes)}")
    print(f"  New edges: {len(new_edges)}")
    print(f"  New tracks: {len(new_tracks)}")

    return new_nodes, new_edges, new_tracks


def find_connected_components(edges):
    """Find connected components using union-find."""
    parent = {}

    def find(x):
        if x not in parent:
            parent[x] = x
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py

    for edge in edges:
        union(edge['source'], edge['target'])

    # Group nodes by component root
    components = defaultdict(set)
    for node in parent:
        components[find(node)].add(node)

    return list(components.values())


def connect_floating_subgraphs(network, new_nodes, new_edges, new_tracks):
    """
    Connect any NRWN subgraphs that are not connected to the main network.

    For each floating subgraph, finds the closest main network node and adds
    a virtual edge to connect them.
    """
    print("Connecting floating subgraphs to main network...")

    existing_nodes = network['nodes']
    existing_edges = network['edges']

    # Get original node IDs (before NRWN merge)
    original_node_ids = {n['id'] for n in existing_nodes}

    # Build a node lookup by ID
    all_nodes = {n['id']: n for n in existing_nodes}
    for n in new_nodes:
        all_nodes[n['id']] = n

    # Find connected components including both existing and new edges
    all_edges = existing_edges + new_edges
    components = find_connected_components(all_edges)
    print(f"  Found {len(components)} connected components")

    # Identify the main component (should be the largest and contain original nodes)
    main_component = None
    floating_components = []
    for comp in components:
        overlap = comp & original_node_ids
        if overlap:
            # This component overlaps with original nodes
            if main_component is None or len(comp) > len(main_component):
                if main_component is not None:
                    # Previous main was smaller, treat as floating
                    floating_components.append(main_component)
                main_component = comp
            else:
                floating_components.append(comp)
        else:
            floating_components.append(comp)

    if not main_component:
        print("  Warning: No main component found")
        return [], []

    print(f"  Main component has {len(main_component)} nodes")
    print(f"  {len(floating_components)} floating components to connect")

    virtual_edges = []
    virtual_tracks = []

    for comp in floating_components:
        # Find the closest pair (main_node, floating_node)
        min_dist = float('inf')
        best_pair = None

        for floating_id in comp:
            floating_node = all_nodes.get(floating_id)
            if not floating_node:
                continue

            for main_id in main_component:
                main_node = all_nodes.get(main_id)
                if not main_node:
                    continue

                dist = haversine_distance(
                    floating_node['lon'], floating_node['lat'],
                    main_node['lon'], main_node['lat']
                )
                if dist < min_dist:
                    min_dist = dist
                    best_pair = (main_id, floating_id)

        if best_pair:
            main_id, floating_id = best_pair
            print(f"    Connecting {floating_id} -> {main_id} ({min_dist/1000:.1f}km)")

            # Add virtual edge (with very short length to not affect routing much)
            virtual_edges.append({
                'source': main_id,
                'target': floating_id,
                'length_m': round(min_dist, 1),
                'length_km': round(min_dist / 1000, 2),
                'built_year': 0,
                'abandoned_year': 0,
                'builder_code': 'VIRTUAL',
                'builder_name': 'Virtual Connection'
            })

            # Add straight-line track geometry for the virtual connection
            main_node = all_nodes[main_id]
            floating_node = all_nodes[floating_id]
            virtual_tracks.append({
                'source': main_id,
                'target': floating_id,
                'coordinates': [
                    [main_node['lon'], main_node['lat']],
                    [floating_node['lon'], floating_node['lat']]
                ],
                'built_year': 0,
                'abandoned_year': 0,
                'builder_name': 'Virtual Connection',
                'length_km': round(min_dist / 1000, 2)
            })

            # Add floating component to main component
            main_component.update(comp)

    print(f"  Added {len(virtual_edges)} virtual edges")
    return virtual_edges, virtual_tracks


def update_network_files(network, tracks_data, new_nodes, new_edges, new_tracks):
    """Update network and tracks files with merged data."""
    print("Updating network files...")

    # Add new nodes
    network['nodes'].extend(new_nodes)

    # Add new edges
    network['edges'].extend(new_edges)

    # Update stats
    network['stats']['node_count'] = len(network['nodes'])
    network['stats']['edge_count'] = len(network['edges'])

    # Add NRWN builder stats
    lmr_count = sum(1 for e in new_edges if e['builder_code'] == 'LMR')
    gwr_count = sum(1 for e in new_edges if e['builder_code'] == 'GWR')
    lmr_length = sum(e['length_km'] for e in new_edges if e['builder_code'] == 'LMR')
    gwr_length = sum(e['length_km'] for e in new_edges if e['builder_code'] == 'GWR')

    network['stats']['by_builder']['LMR'] = {'count': lmr_count, 'length_km': round(lmr_length, 1)}
    network['stats']['by_builder']['GWR'] = {'count': gwr_count, 'length_km': round(gwr_length, 1)}

    # Update metadata
    if 'source' in network['metadata']:
        network['metadata']['source'] += ' + NRWN (LMR, GWR)'

    # Add new tracks
    tracks_data['tracks'].extend(new_tracks)
    tracks_data['track_count'] = len(tracks_data['tracks'])

    # Update metadata
    if 'source' in tracks_data['metadata']:
        tracks_data['metadata']['source'] += ' + NRWN'

    # Write updated files
    print(f"  Writing {NETWORK_FILE}")
    with open(NETWORK_FILE, 'w') as f:
        json.dump(network, f, indent=2)

    print(f"  Writing {TRACKS_FILE}")
    with open(TRACKS_FILE, 'w') as f:
        json.dump(tracks_data, f, indent=2)

    print(f"  Updated network: {network['stats']['node_count']} nodes, {network['stats']['edge_count']} edges")
    print(f"  Updated tracks: {tracks_data['track_count']} tracks")


def main():
    """Main entry point."""
    print("=" * 60)
    print("NRWN Data Merge")
    print("=" * 60)

    # Check if GML file exists
    if not os.path.exists(NRWN_GML_PATH):
        print(f"ERROR: NRWN GML file not found: {NRWN_GML_PATH}")
        return 1

    # Parse NRWN GML
    nrwn_tracks = parse_nrwn_gml(NRWN_GML_PATH)

    if not nrwn_tracks:
        print("No tracks extracted from NRWN data")
        return 1

    # Merge consecutive segments
    merged_tracks = merge_consecutive_segments(nrwn_tracks)

    # Load existing network
    network, tracks_data = load_existing_network()

    # Integrate NRWN tracks
    new_nodes, new_edges, new_tracks = integrate_nrwn_tracks(
        merged_tracks, network, tracks_data
    )

    if not new_edges:
        print("No new edges to add")
        return 0

    # Connect floating subgraphs to main network
    virtual_edges, virtual_tracks = connect_floating_subgraphs(
        network, new_nodes, new_edges, new_tracks
    )
    new_edges.extend(virtual_edges)
    new_tracks.extend(virtual_tracks)

    # Update files
    update_network_files(network, tracks_data, new_nodes, new_edges, new_tracks)

    print("=" * 60)
    print("Merge complete!")
    print()
    print("Next steps:")
    print("  1. Run: python3 scripts/snap_settlements_to_network.py")
    print("  2. Run: python3 scripts/verify_railway_routes.py")
    print("=" * 60)

    return 0


if __name__ == '__main__':
    exit(main())
