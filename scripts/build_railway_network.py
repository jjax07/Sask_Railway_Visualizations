#!/usr/bin/env python3
"""
Build a railway network graph from GIS shapefile data.

Step 1 of railway distance calculation:
- Load Saskatchewan track segments from HR_rails_NEW shapefile
- Convert polylines to a network graph structure
- Nodes = track junctions/endpoints
- Edges = track segments with actual length in meters

Reads:
- KnowledgeGraph/doi-10.5683-sp2-uccfvq/extracted/HR_rails_NEW.shp

Outputs:
- data/railway_network.json - Network graph for distance calculations
"""

import json
import os
import shapefile
from pyproj import Transformer
import networkx as nx
from collections import defaultdict

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
SHAPEFILE_PATH = os.path.join(
    os.path.dirname(PROJECT_DIR),
    "KnowledgeGraph",
    "doi-10.5683-sp2-uccfvq",
    "extracted",
    "HR_rails_NEW.shp"
)
OUTPUT_FILE = os.path.join(PROJECT_DIR, "data", "railway_network.json")

# Saskatchewan bounding box (lat/lon)
# Note: Eastern boundary is -101.36 but we use -101.0 to catch border tracks
SK_BOUNDS = {
    'min_lon': -110.0,
    'max_lon': -101.0,
    'min_lat': 49.0,
    'max_lat': 60.0
}

# Lambert Conformal Conic projection used by the shapefile
LCC_PROJ = '+proj=lcc +lat_1=49 +lat_2=77 +lat_0=49 +lon_0=-95 +x_0=0 +y_0=0 +datum=NAD27 +units=m +no_defs'

# Tolerance for snapping nearby nodes (meters)
# Set to 500m to merge track endpoints at the same junction
# (original data has endpoints that can be 100-400m apart at junctions)
SNAP_TOLERANCE = 500.0


def is_in_saskatchewan(bbox, inverse_transformer):
    """
    Check if a track segment's bounding box intersects Saskatchewan.

    Uses lat/lon comparison since the LCC projection curves latitude lines,
    making simple rectangular bounds checks in projected coords unreliable.
    """
    if not bbox:
        return False

    # Convert bbox corners to lat/lon
    sw_lon, sw_lat = inverse_transformer.transform(bbox[0], bbox[1])
    ne_lon, ne_lat = inverse_transformer.transform(bbox[2], bbox[3])

    # Check intersection with Saskatchewan bounds
    return (sw_lon < SK_BOUNDS['max_lon'] and ne_lon > SK_BOUNDS['min_lon'] and
            sw_lat < SK_BOUNDS['max_lat'] and ne_lat > SK_BOUNDS['min_lat'])


def round_coord(x, y, precision=1):
    """Round coordinates for node identification (snap to grid)."""
    return (round(x, precision), round(y, precision))


def find_or_create_node(graph, x, y, node_index, tolerance=SNAP_TOLERANCE):
    """
    Find an existing node near (x, y) or create a new one.
    Returns node_id.
    """
    # Check if there's an existing node within tolerance
    for node_id, data in graph.nodes(data=True):
        dx = data['x'] - x
        dy = data['y'] - y
        dist = (dx * dx + dy * dy) ** 0.5
        if dist < tolerance:
            return node_id, node_index

    # Create new node
    new_id = f"n{node_index}"
    graph.add_node(new_id, x=x, y=y)
    return new_id, node_index + 1


def round_point(x, y, precision=10):
    """Round point coordinates to create grid for junction detection."""
    return (round(x / precision) * precision, round(y / precision) * precision)


def find_junction_points(shapes, records, inverse_transformer):
    """
    Find all junction points where multiple tracks meet.
    Returns a set of (x, y) points that should become nodes.
    """
    # Collect all points from all tracks, rounded to detect matches
    point_counts = {}
    point_to_original = {}  # Map rounded point to original coordinates

    for shape, rec in zip(shapes, records):
        if not hasattr(shape, 'bbox') or not shape.bbox:
            continue
        if not is_in_saskatchewan(shape.bbox, inverse_transformer):
            continue

        for pt in shape.points:
            rounded = round_point(pt[0], pt[1])
            point_counts[rounded] = point_counts.get(rounded, 0) + 1
            # Keep first original point for this rounded location
            if rounded not in point_to_original:
                point_to_original[rounded] = (pt[0], pt[1])

    # Junction points are those appearing in multiple tracks
    junctions = set()
    for rounded, count in point_counts.items():
        if count > 1:
            junctions.add(point_to_original[rounded])

    return junctions


def calculate_polyline_length(points):
    """Calculate the length of a polyline from its points."""
    length = 0.0
    for i in range(len(points) - 1):
        dx = points[i + 1][0] - points[i][0]
        dy = points[i + 1][1] - points[i][1]
        length += (dx * dx + dy * dy) ** 0.5
    return length


def is_junction_point(pt, junctions, tolerance=SNAP_TOLERANCE):
    """Check if a point is near any junction point."""
    for jx, jy in junctions:
        dx = pt[0] - jx
        dy = pt[1] - jy
        if (dx * dx + dy * dy) ** 0.5 < tolerance:
            return (jx, jy)
    return None


def split_track_at_junctions(points, junctions, tolerance=SNAP_TOLERANCE):
    """
    Split a track's points at junction locations.
    Returns list of (sub_points, sub_length) for each segment.
    """
    if len(points) < 2:
        return []

    segments = []
    current_segment = [points[0]]

    for i in range(1, len(points)):
        pt = points[i]
        current_segment.append(pt)

        # Check if this intermediate point is a junction (not endpoints)
        if i < len(points) - 1:  # Not the last point
            junction_pt = is_junction_point(pt, junctions, tolerance)
            if junction_pt:
                # End current segment at this junction
                seg_length = calculate_polyline_length(current_segment)
                segments.append((current_segment, seg_length))
                # Start new segment from junction
                current_segment = [pt]

    # Add final segment
    if len(current_segment) >= 2:
        seg_length = calculate_polyline_length(current_segment)
        segments.append((current_segment, seg_length))

    return segments


def load_railway_tracks():
    """Load railway track segments from shapefile."""
    print(f"Loading shapefile: {SHAPEFILE_PATH}")

    # Create coordinate transformer
    transformer = Transformer.from_crs('EPSG:4326', LCC_PROJ, always_xy=True)
    inverse_transformer = Transformer.from_crs(LCC_PROJ, 'EPSG:4326', always_xy=True)

    print(f"Saskatchewan bounds (lat/lon): lat {SK_BOUNDS['min_lat']}-{SK_BOUNDS['max_lat']}, "
          f"lon {SK_BOUNDS['min_lon']} to {SK_BOUNDS['max_lon']}")

    # Read shapefile
    sf = shapefile.Reader(SHAPEFILE_PATH)
    shapes = list(sf.shapes())
    records = list(sf.records())
    print(f"Total records in shapefile: {len(shapes)}")

    # First pass: find all junction points
    print("Finding junction points...")
    junctions = find_junction_points(shapes, records, inverse_transformer)
    print(f"Found {len(junctions)} junction points")

    # Create network graph
    graph = nx.Graph()
    node_index = 0

    # Track statistics
    stats = {
        'total_segments': 0,
        'sk_segments': 0,
        'total_length_m': 0,
        'by_builder': defaultdict(lambda: {'count': 0, 'length': 0}),
        'by_decade': defaultdict(lambda: {'count': 0, 'length': 0})
    }

    # Railway company codes
    builder_names = {
        '1': 'CPR',
        '2': 'CNR',
        '5': 'CNoR',
        '49': 'GTP',
        '49A': 'GTP Branch',
        '49B': 'GTP Sask',
        '53R': 'CNoR Sask',
    }

    # Second pass: process each track segment, splitting at junctions
    print("Processing tracks and splitting at junctions...")
    edges_added = 0

    for shape, rec in zip(shapes, records):
        stats['total_segments'] += 1

        # Skip null shapes
        if not hasattr(shape, 'bbox') or not shape.bbox:
            continue

        # Check if in Saskatchewan
        if not is_in_saskatchewan(shape.bbox, inverse_transformer):
            continue

        stats['sk_segments'] += 1

        # Extract attributes
        original_length_m = rec['LENGTH'] or rec['Shape_Leng'] or 0
        built_year = rec['CNSTRCTD'] or 0
        abandoned_year = rec['ABNDND'] or 0
        builder_code = str(rec['BLDR_CODE']).strip()

        # Track stats (using original length)
        stats['total_length_m'] += original_length_m
        stats['by_builder'][builder_code]['count'] += 1
        stats['by_builder'][builder_code]['length'] += original_length_m

        if built_year:
            decade = (built_year // 10) * 10
            stats['by_decade'][decade]['count'] += 1
            stats['by_decade'][decade]['length'] += original_length_m

        # Get polyline points
        points = shape.points

        if len(points) < 2:
            continue

        # Split track at junction points
        segments = split_track_at_junctions(points, junctions, SNAP_TOLERANCE)

        if not segments:
            # No split needed, use original endpoints
            segments = [(points, calculate_polyline_length(points))]

        # Process each segment
        for seg_points, seg_length in segments:
            if len(seg_points) < 2:
                continue

            start_pt = seg_points[0]
            end_pt = seg_points[-1]

            # Find or create nodes for endpoints
            start_node, node_index = find_or_create_node(graph, start_pt[0], start_pt[1], node_index)
            end_node, node_index = find_or_create_node(graph, end_pt[0], end_pt[1], node_index)

            # Skip self-loops
            if start_node == end_node:
                continue

            # Add edge (or update if shorter path found)
            edge_data = {
                'length_m': seg_length,
                'built_year': built_year,
                'abandoned_year': abandoned_year,
                'builder_code': builder_code,
                'builder_name': builder_names.get(builder_code, builder_code),
                'points': seg_points
            }

            if graph.has_edge(start_node, end_node):
                # Keep shorter segment if duplicate
                existing = graph[start_node][end_node]
                if seg_length < existing['length_m']:
                    graph[start_node][end_node].update(edge_data)
            else:
                graph.add_edge(start_node, end_node, **edge_data)
                edges_added += 1

    return graph, stats, inverse_transformer


def analyze_network(graph):
    """Analyze the network structure."""
    print("\n=== Network Analysis ===")

    # Basic stats
    print(f"Nodes: {graph.number_of_nodes()}")
    print(f"Edges: {graph.number_of_edges()}")

    # Total track length
    total_length = sum(d['length_m'] for _, _, d in graph.edges(data=True))
    print(f"Total track length: {total_length / 1000:.1f} km")

    # Connected components
    components = list(nx.connected_components(graph))
    print(f"Connected components: {len(components)}")

    # Size of largest component
    largest = max(components, key=len)
    print(f"Largest component: {len(largest)} nodes")

    # Degree distribution
    degrees = [d for n, d in graph.degree()]
    print(f"Node degrees: min={min(degrees)}, max={max(degrees)}, avg={sum(degrees)/len(degrees):.1f}")

    # Junction nodes (degree > 2)
    junctions = [n for n, d in graph.degree() if d > 2]
    print(f"Junction nodes (degree > 2): {len(junctions)}")

    return {
        'nodes': graph.number_of_nodes(),
        'edges': graph.number_of_edges(),
        'total_length_km': total_length / 1000,
        'connected_components': len(components),
        'largest_component_nodes': len(largest),
        'junction_count': len(junctions)
    }


def export_network(graph, stats, inverse_transformer):
    """Export network to JSON format."""
    print(f"\nExporting network to {OUTPUT_FILE}")

    # Convert nodes to list with lat/lon
    nodes = []
    for node_id, data in graph.nodes(data=True):
        # Convert projected coords back to lat/lon
        lon, lat = inverse_transformer.transform(data['x'], data['y'])
        nodes.append({
            'id': node_id,
            'x': data['x'],
            'y': data['y'],
            'lat': round(lat, 6),
            'lon': round(lon, 6)
        })

    # Convert edges to list (without full geometry to save space)
    edges = []
    for u, v, data in graph.edges(data=True):
        edges.append({
            'source': u,
            'target': v,
            'length_m': round(data['length_m'], 1),
            'length_km': round(data['length_m'] / 1000, 2),
            'built_year': data['built_year'],
            'abandoned_year': data['abandoned_year'],
            'builder_code': data['builder_code'],
            'builder_name': data['builder_name']
        })

    # Build output structure
    output = {
        'metadata': {
            'description': 'Saskatchewan railway network graph',
            'source': 'HR_rails_NEW.shp (Historical Railways of Canada)',
            'projection': 'NAD27 Lambert Conformal Conic',
            'units': 'meters',
            'snap_tolerance_m': SNAP_TOLERANCE
        },
        'stats': {
            'sk_segments': stats['sk_segments'],
            'total_length_km': round(stats['total_length_m'] / 1000, 1),
            'node_count': len(nodes),
            'edge_count': len(edges),
            'by_builder': {
                k: {'count': v['count'], 'length_km': round(v['length'] / 1000, 1)}
                for k, v in sorted(stats['by_builder'].items())
            },
            'by_decade': {
                str(k): {'count': v['count'], 'length_km': round(v['length'] / 1000, 1)}
                for k, v in sorted(stats['by_decade'].items())
            }
        },
        'nodes': nodes,
        'edges': edges
    }

    # Write output
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Wrote {len(nodes)} nodes and {len(edges)} edges")


def main():
    print("=" * 60)
    print("Building Railway Network Graph - Step 1")
    print("=" * 60)

    # Load tracks and build graph
    graph, stats, inverse_transformer = load_railway_tracks()

    # Print loading stats
    print(f"\n=== Loading Statistics ===")
    print(f"Total segments in shapefile: {stats['total_segments']}")
    print(f"Saskatchewan segments: {stats['sk_segments']}")
    print(f"Total track length: {stats['total_length_m'] / 1000:.1f} km")

    print(f"\nBy Builder:")
    for code, data in sorted(stats['by_builder'].items(), key=lambda x: -x[1]['length']):
        print(f"  {code}: {data['count']} segments, {data['length'] / 1000:.1f} km")

    print(f"\nBy Decade Built:")
    for decade, data in sorted(stats['by_decade'].items()):
        print(f"  {decade}s: {data['count']} segments, {data['length'] / 1000:.1f} km")

    # Analyze network
    analysis = analyze_network(graph)

    # Export to JSON
    export_network(graph, stats, inverse_transformer)

    print("\n" + "=" * 60)
    print("Step 1 Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
