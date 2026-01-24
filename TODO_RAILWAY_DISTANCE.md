# TODO: Railway Distance Calculation

## Goal
Update visualizations to show **railway distance** between settlements instead of straight-line ("as the crow flies") distance.

## Current State
All distances in `data/settlement_connections.json` are haversine (straight-line) distances calculated from lat/lon coordinates.

## GIS Data Assessment (January 23, 2026)

### Data Location
`/Users/baebot/Documents/ClaudeCode/KnowledgeGraph/doi-10.5683-sp2-uccfvq/extracted/`

### Available Files
| File | Description |
|------|-------------|
| `HR_rails_NEW.shp/dbf` | Railway track polylines with geometries |
| `hr_places_all.shp/dbf` | Railway station/place locations |
| `hr_codes.dbf` | Railway company codes (645 companies) |
| `transactions.csv` | Track ownership transactions |

### Railway Track Data (HR_rails_NEW)
- **Format**: ESRI Shapefile (POLYLINE)
- **Projection**: NAD27 Lambert Conformal Conic (central meridian -95°)
- **Total records**: 3,050 track segments Canada-wide
- **Saskatchewan coverage**: 467 segments, ~30,659 km total track

**Key Fields:**
| Field | Description |
|-------|-------------|
| `LENGTH` / `Shape_Leng` | Track segment length in meters |
| `CNSTRCTD` | Construction year |
| `ABNDND` | Abandonment year (0 = still active) |
| `BLDR_CODE` | Builder company code |
| `INCRP_CODE` | Incorporated company code |

**Builder Codes (Saskatchewan-relevant):**
- `1` = Canadian Pacific Railway
- `2` = Canadian National (post-1923)
- `5` = Canadian Northern Railway
- `49` = Grand Trunk Pacific

### Feasibility: ✅ CONFIRMED

The GIS data contains actual track geometries (polylines with coordinate points) that can be used to calculate real railway distances between settlements.

## Implementation Approach

### Step 1: Build Track Network Graph ✅ COMPLETE
1. Load all Saskatchewan track segments from shapefile
2. Convert polylines to a network graph structure
3. Nodes = track junctions/endpoints
4. Edges = track segments with actual length

**Script:** `scripts/build_railway_network.py`
**Output:** `data/railway_network.json`

**Results (after junction detection fix):**
- 474 track segments loaded
- 424 nodes (includes intermediate junction points)
- 509 edges (tracks split at junctions)
- 27,218 km total track
- 5 connected components (was 13 before junction fix)
- Junction nodes properly detected where tracks meet

**By Builder:**
| Code | Name | Segments | Track Length |
|------|------|----------|--------------|
| 1 | CPR | 207 | 13,237 km |
| 5 | CNoR | 100 | 4,974 km |
| 2 | CNR | 72 | 3,852 km |
| 49/49A | GTP | 57 | 2,698 km |

### Step 2: Snap Settlements to Network ✅ COMPLETE
1. For each settlement, find nearest point on railway network
2. Handle settlements that are off-network (branch lines, etc.)
3. Create mapping: settlement → network node(s)

**Script:** `scripts/snap_settlements_to_network.py`
**Output:** `data/settlement_network_mapping.json`

**Results (429 settlements):**
| Snap Quality | Count | Percent |
|--------------|-------|---------|
| on_network (≤5km) | 380 | 88.6% |
| near_network (5-15km) | 35 | 8.2% |
| distant (15-50km) | 14 | 3.3% |
| off_network (>50km) | 0 | 0.0% |

**Major Cities:** All snap well to network
- Regina: 0.12 km
- Moosejaw: 0.05 km
- Estevan: 0.17 km
- Prince Albert: 0.67 km
- Swift Current: 0.69 km
- Saskatoon: 1.65 km

**SE Saskatchewan (Souris Line):** All snap correctly after bounds fix
- Estevan: 0.17 km, Oxbow: 3.9 km, Carnduff: 1.03 km, North Portal: 1.01 km

### Step 3: Calculate Railway Distances ✅ COMPLETE
1. Use shortest path algorithm (Dijkstra) between settlement nodes
2. Sum actual track lengths along path
3. Store railway distances alongside haversine distances

**Script:** `scripts/calculate_railway_distances.py`
**Output:** Updated `data/settlement_connections.json` with `railway_distance_km` field

**Results (after junction detection and bidirectional sync fixes):**
- 1,811 connection pairs processed
- 1,691 pairs with calculated railway distances
- 391 same-edge pairs (direct calculation using edge t-parameter)
- 1,300 via network routing (Dijkstra shortest path)
- 0 no-path pairs (all settlements now connected after junction fix)
- 120 same-node pairs (settlements at same junction)

**Sample Direct Routes (ratio ≈ 1.0x):**
- Sintaluta → Wolseley: 13.9km direct, 13.9km by rail (1.0x)
- Rosthern → Hague: 17.1km direct, 17.1km by rail (1.0x)
- Meota → Vawn: 16.7km direct, 16.6km by rail (1.0x)

**Average ratio:** 2.58x (improved from 4.99x before junction fix)

### Step 4: Update Visualizations ✅ COMPLETE
Updated visualizations to display both direct and railway distances:

**settlement_explorer.html:**
- Popup now shows "Direct: X km | By rail: Y km"
- Settlement list shows "X km direct / Y km by rail"
- Header text updated to mention railway distances

**one_hour_map.html:**
- Added railway_distance_km to data/one_hour_corridor.json
- Popup shows both direct and railway distances
- Settlement list shows both distance types

**network_graph.html:**
- No changes needed (focuses on network topology, not distances)

## Technical Requirements
```python
# Required libraries
import shapefile  # pyshp - reading shapefiles
from pyproj import Transformer  # coordinate conversion
import networkx as nx  # graph algorithms
```

## Affected Visualizations
Any visualization showing distance between settlements:
- Settlement Explorer (shows distance to nearby settlements)
- Network Graph (connection distances)
- One-Hour Corridor (40km radius concept may need adjustment)

## Questions to Resolve
1. How to handle abandoned track sections? (Use `ABNDND` field filter by year?)
2. Should we compute distances for a specific historical year?
3. How to handle settlements not directly on a railway line?

---
*Created: January 23, 2026*
*Updated: January 23, 2026 - All steps complete! Railway distances now displayed in visualizations*
