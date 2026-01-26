#!/usr/bin/env python3
"""
Fix Ogema (n557) connectivity issue.

The NRWN merge created node n557 for Ogema but didn't connect it to the
existing network. Node n577 is 570m away and is connected. This script
adds an edge to bridge the gap.
"""

import json
import math

def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in meters."""
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

def main():
    # Load network
    print("Loading railway_network.json...")
    with open('data/railway_network.json') as f:
        network = json.load(f)

    # Find nodes
    nodes = {n['id']: n for n in network['nodes']}
    n557 = nodes['n557']
    n577 = nodes['n577']

    # Calculate distance
    dist_m = haversine(n557['lat'], n557['lon'], n577['lat'], n577['lon'])
    dist_km = dist_m / 1000

    print(f"n557 (Ogema): ({n557['lat']}, {n557['lon']})")
    print(f"n577: ({n577['lat']}, {n577['lon']})")
    print(f"Distance: {dist_m:.1f}m ({dist_km:.2f}km)")

    # Check if edge already exists
    for e in network['edges']:
        if (e['source'] == 'n557' and e['target'] == 'n577') or \
           (e['source'] == 'n577' and e['target'] == 'n557'):
            print("Edge already exists!")
            return

    # Add new edge to network
    new_edge = {
        "source": "n557",
        "target": "n577",
        "length_m": round(dist_m, 1),
        "length_km": round(dist_km, 2),
        "built_year": 1911,  # Ogema got railway in 1911
        "abandoned_year": 0,
        "builder_code": "2",  # CPR
        "builder_name": "CPR"
    }

    network['edges'].append(new_edge)
    network['stats']['edge_count'] = len(network['edges'])

    print(f"\nAdding edge: {new_edge}")

    # Save network
    with open('data/railway_network.json', 'w') as f:
        json.dump(network, f, indent=2)
    print("Saved railway_network.json")

    # Load and update tracks
    print("\nLoading railway_tracks.json...")
    with open('data/railway_tracks.json') as f:
        tracks = json.load(f)

    # Add new track with simple 2-point geometry
    new_track = {
        "source": "n557",
        "target": "n577",
        "coordinates": [
            [n557['lon'], n557['lat']],
            [n577['lon'], n577['lat']]
        ],
        "built_year": 1911,
        "abandoned_year": 0,
        "builder_name": "CPR",
        "length_km": round(dist_km, 2)
    }

    tracks['tracks'].append(new_track)

    print(f"Adding track: n557 -> n577 ({dist_km:.2f}km)")

    # Save tracks
    with open('data/railway_tracks.json', 'w') as f:
        json.dump(tracks, f, indent=2)
    print("Saved railway_tracks.json")

    print("\n✓ Ogema connectivity fixed!")

if __name__ == '__main__':
    main()
