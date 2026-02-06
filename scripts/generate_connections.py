#!/usr/bin/env python3
"""
Generate settlement connection data for the Settlement Explorer visualization.

Reads:
- data/settlements.json - 429 settlements with coordinates and railway info
- data/railway_timeline.json - Settlements by railway with arrival years
- KnowledgeGraph/one_hour_railway_connections_complete.csv - Pre-calculated pairs

Outputs:
- data/settlement_connections.json - Connection data for visualization
"""

import json
import csv
import os
import math

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
SETTLEMENTS_FILE = os.path.join(PROJECT_DIR, "data", "settlements.json")
TIMELINE_FILE = os.path.join(PROJECT_DIR, "data", "railway_timeline.json")
CSV_FILE = os.path.join(os.path.dirname(PROJECT_DIR), "KnowledgeGraph", "one_hour_railway_connections_complete.csv")
OUTPUT_FILE = os.path.join(PROJECT_DIR, "data", "settlement_connections.json")


def load_settlements():
    """Load settlements from JSON file."""
    with open(SETTLEMENTS_FILE, 'r') as f:
        settlements_list = json.load(f)

    # Convert to dict keyed by name
    settlements = {}
    for s in settlements_list:
        settlements[s['name']] = {
            'lat': s['lat'],
            'lon': s['lon'],
            'railway_arrives': s.get('railway_arrives'),
            'first_railway': s.get('first_railway')
        }
    return settlements


def load_railway_timeline():
    """Load railway timeline to map settlements to railways."""
    with open(TIMELINE_FILE, 'r') as f:
        timeline = json.load(f)

    # Create mapping: settlement name -> list of (railway, year)
    settlement_railways = {}
    for railway, stops in timeline.items():
        for stop in stops:
            name = stop['name']
            year = stop['year']
            if name not in settlement_railways:
                settlement_railways[name] = []
            settlement_railways[name].append({
                'railway': railway,
                'year': year
            })

    return settlement_railways


def load_connections_csv():
    """Load pre-calculated connection pairs from CSV."""
    connections = []
    with open(CSV_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            connections.append({
                'settlement_1': row['Settlement_1'],
                'settlement_2': row['Settlement_2'],
                'distance_km': float(row['Distance_km'])
            })
    return connections


def get_all_shared_railways(s1_railways, s2_railways):
    """Find all railways shared between two settlements with connection years."""
    if not s1_railways or not s2_railways:
        return []

    s1_railway_names = {r['railway'] for r in s1_railways}
    s2_railway_names = {r['railway'] for r in s2_railways}

    shared = s1_railway_names & s2_railway_names

    result = []
    for railway in shared:
        # Get year for each settlement on this railway
        s1_year = next((r['year'] for r in s1_railways if r['railway'] == railway), None)
        s2_year = next((r['year'] for r in s2_railways if r['railway'] == railway), None)

        if s1_year and s2_year:
            connected_year = max(s1_year, s2_year)
            result.append({
                'railway': railway,
                'connected_year': connected_year
            })

    # Sort by connection year (earliest first)
    result.sort(key=lambda x: x['connected_year'])
    return result


def haversine_km(lat1, lon1, lat2, lon2):
    """Calculate great-circle distance in km between two points."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))


def main():
    print("Loading data...")
    settlements = load_settlements()
    settlement_railways = load_railway_timeline()
    csv_connections = load_connections_csv()

    # Backfill settlement_railways with settlements.json data for settlements
    # not in railway_timeline.json
    backfilled = 0
    for name, sdata in settlements.items():
        if name not in settlement_railways:
            first_rw = sdata.get('first_railway')
            rw_arrives = sdata.get('railway_arrives')
            if first_rw and first_rw not in ['No', 'Missing', None] and rw_arrives:
                settlement_railways[name] = [{'railway': first_rw, 'year': rw_arrives}]
                backfilled += 1

    print(f"Loaded {len(settlements)} settlements")
    print(f"Loaded {len(settlement_railways)} settlements with railway info ({backfilled} backfilled from settlements.json)")
    print(f"Loaded {len(csv_connections)} connection pairs from CSV")

    # Build output structure
    output = {
        'settlements': {},
        'connections': {}
    }

    # Add all settlements to output with ALL their railways
    for name, data in settlements.items():
        railways = settlement_railways.get(name, [])

        # Sort railways by year
        sorted_railways = sorted(railways, key=lambda r: r['year']) if railways else []

        # Get first railway info
        first_railway = None
        railway_arrives = None
        if sorted_railways:
            first_railway = sorted_railways[0]['railway']
            railway_arrives = sorted_railways[0]['year']
        elif data.get('first_railway') and data['first_railway'] not in ['No', 'Missing', None]:
            first_railway = data.get('first_railway')
            railway_arrives = data.get('railway_arrives')

        output['settlements'][name] = {
            'lat': data['lat'],
            'lon': data['lon'],
            'railway_arrives': railway_arrives,
            'first_railway': first_railway,
            # Include ALL railways for this settlement
            'railways': sorted_railways if sorted_railways else None
        }
        output['connections'][name] = []

    # Process CSV connections to build bidirectional connection lists
    connection_count = 0
    multi_railway_connections = 0

    for conn in csv_connections:
        s1 = conn['settlement_1']
        s2 = conn['settlement_2']
        distance = conn['distance_km']

        # Skip if settlement not in our list
        if s1 not in settlements or s2 not in settlements:
            continue

        # Get railways for each settlement
        s1_railways = settlement_railways.get(s1, [])
        s2_railways = settlement_railways.get(s2, [])

        # Find ALL shared railways
        shared = get_all_shared_railways(s1_railways, s2_railways)

        if shared:
            # Use earliest shared railway connection for primary display
            earliest = shared[0]

            if len(shared) > 1:
                multi_railway_connections += 1

            # Add connection from s1 to s2
            output['connections'][s1].append({
                'to': s2,
                'distance_km': round(distance, 1),
                'shared_railway': earliest['railway'],
                'connected_year': earliest['connected_year'],
                'connection_type': 'same_railway',
                # Include all shared railways
                'all_shared_railways': shared if len(shared) > 1 else None
            })

            # Add connection from s2 to s1
            output['connections'][s2].append({
                'to': s1,
                'distance_km': round(distance, 1),
                'shared_railway': earliest['railway'],
                'connected_year': earliest['connected_year'],
                'connection_type': 'same_railway',
                'all_shared_railways': shared if len(shared) > 1 else None
            })

            connection_count += 1
        else:
            # No shared railway - check if both have rail service (interchange)
            s1_has_rail = len(s1_railways) > 0
            s2_has_rail = len(s2_railways) > 0

            if s1_has_rail and s2_has_rail:
                # Both have rail but on different railways - interchange connection
                s1_earliest_year = min(r['year'] for r in s1_railways)
                s2_earliest_year = min(r['year'] for r in s2_railways)
                connected_year = max(s1_earliest_year, s2_earliest_year)

                output['connections'][s1].append({
                    'to': s2,
                    'distance_km': round(distance, 1),
                    'shared_railway': 'Interchange',
                    'connected_year': connected_year,
                    'connection_type': 'interchange',
                    'all_shared_railways': None
                })
                output['connections'][s2].append({
                    'to': s1,
                    'distance_km': round(distance, 1),
                    'shared_railway': 'Interchange',
                    'connected_year': connected_year,
                    'connection_type': 'interchange',
                    'all_shared_railways': None
                })
            else:
                # One or both lack rail service - keep as pending
                output['connections'][s1].append({
                    'to': s2,
                    'distance_km': round(distance, 1),
                    'shared_railway': None,
                    'connected_year': None,
                    'connection_type': None,
                    'all_shared_railways': None
                })
                output['connections'][s2].append({
                    'to': s1,
                    'distance_km': round(distance, 1),
                    'shared_railway': None,
                    'connected_year': None,
                    'connection_type': None,
                    'all_shared_railways': None
                })

    # Fill gaps: settlements with railway data but missing from CSV
    # Find their nearest neighbors and create connections
    gap_count = 0
    for name, sdata in output['settlements'].items():
        if not sdata.get('railway_arrives'):
            continue
        # Check if this settlement has any valid connections
        has_valid = any(c.get('connected_year') for c in output['connections'][name])
        if has_valid:
            continue

        # Find nearest settlements by haversine distance
        s_lat, s_lon = sdata['lat'], sdata['lon']
        neighbors = []
        for other_name, other_data in output['settlements'].items():
            if other_name == name:
                continue
            dist = haversine_km(s_lat, s_lon, other_data['lat'], other_data['lon'])
            if dist <= 120:  # Generous threshold to catch remote settlements
                neighbors.append((other_name, dist))
        neighbors.sort(key=lambda x: x[1])

        # Take nearest neighbors (up to 5, or all within 40km)
        selected = []
        for nb_name, nb_dist in neighbors:
            if len(selected) >= 5 and nb_dist > 40:
                break
            selected.append((nb_name, nb_dist))
            if len(selected) >= 10:
                break

        s_railways = settlement_railways.get(name, [])
        for nb_name, nb_dist in selected:
            nb_railways = settlement_railways.get(nb_name, [])
            shared = get_all_shared_railways(s_railways, nb_railways)

            if shared:
                earliest = shared[0]
                output['connections'][name].append({
                    'to': nb_name,
                    'distance_km': round(nb_dist, 1),
                    'shared_railway': earliest['railway'],
                    'connected_year': earliest['connected_year'],
                    'connection_type': 'same_railway',
                    'all_shared_railways': shared if len(shared) > 1 else None
                })
                output['connections'][nb_name].append({
                    'to': name,
                    'distance_km': round(nb_dist, 1),
                    'shared_railway': earliest['railway'],
                    'connected_year': earliest['connected_year'],
                    'connection_type': 'same_railway',
                    'all_shared_railways': shared if len(shared) > 1 else None
                })
            elif s_railways and nb_railways:
                s_earliest = min(r['year'] for r in s_railways)
                nb_earliest = min(r['year'] for r in nb_railways)
                connected_year = max(s_earliest, nb_earliest)
                output['connections'][name].append({
                    'to': nb_name,
                    'distance_km': round(nb_dist, 1),
                    'shared_railway': 'Interchange',
                    'connected_year': connected_year,
                    'connection_type': 'interchange',
                    'all_shared_railways': None
                })
                output['connections'][nb_name].append({
                    'to': name,
                    'distance_km': round(nb_dist, 1),
                    'shared_railway': 'Interchange',
                    'connected_year': connected_year,
                    'connection_type': 'interchange',
                    'all_shared_railways': None
                })

        if any(c.get('connected_year') for c in output['connections'][name]):
            gap_count += 1

    print(f"Gap-filled {gap_count} settlements missing from CSV")

    # Sort connections by distance for each settlement
    for name in output['connections']:
        output['connections'][name].sort(key=lambda x: x['distance_km'])

    # Write output
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nOutput written to {OUTPUT_FILE}")
    print(f"Total railway-connected pairs: {connection_count}")
    print(f"Pairs with multiple shared railways: {multi_railway_connections}")

    # Print some stats
    settlements_with_connections = sum(1 for s in output['connections'] if output['connections'][s])
    print(f"Settlements with nearby connections: {settlements_with_connections}")

    # Count settlements with multiple railways
    multi_railway_settlements = sum(1 for s in output['settlements'].values()
                                    if s['railways'] and len(s['railways']) > 1)
    print(f"Settlements with multiple railways: {multi_railway_settlements}")

    # Show sample
    print(f"\nSample - Saskatoon:")
    saskatoon = output['settlements'].get('Saskatoon')
    if saskatoon:
        print(f"  Railways: {saskatoon['railways']}")
        print(f"  Connections:")
        for conn in output['connections']['Saskatoon'][:5]:
            print(f"    -> {conn['to']}: {conn['distance_km']}km, {conn['shared_railway']} ({conn['connected_year']})")


if __name__ == "__main__":
    main()
