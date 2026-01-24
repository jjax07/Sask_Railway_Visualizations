# Railway Route Display Issues

## Overview

After implementing railway route visualization, we ran a verification script (`scripts/verify_railway_routes.py`) that checks all 1,811 unique settlement connections. The script simulates the JavaScript path-finding logic and measures how close the resulting path geometry gets to each settlement.

**Current Results (after fixes):**
| Status | Count | Percentage |
|--------|-------|------------|
| OK | 1,453 | 80.2% |
| Warnings (5-15km from path) | 289 | 16.0% |
| Errors (will show straight lines) | 69 | 3.8% |

**Progress:**
| Date | OK | Warnings | Errors | Notes |
|------|-----|----------|--------|-------|
| Initial | 1,006 | 235 | 570 | Before edge interpolation |
| Jan 24 | 1,445 | 289 | 77 | Added edge interpolation |
| Jan 24 | 1,453 | 289 | 69 | Fixed track direction bug |

## Issue Categories

### Issue 1: NO_GEOMETRY (511 connections)

**Problem:** Both settlements snap to the same network node, resulting in a single-node path with no edges and therefore no track geometry to draw.

**Example:**
```
Meota -> Vawn: Path is ['n63'] (single node, no geometry)
Ruddell -> Maymont: Path is ['n75'] (single node, no geometry)
```

**Why this happens:**
- Two settlements are geographically close to each other
- Both are near the same point on a railway line
- The snapping algorithm assigns them to the same node (or same edge endpoint)
- Pathfinding returns a path of length 1 (just the shared node)
- No edges means no track geometry

**Affected settlements (sample):**
- Meota, Vawn, Edam (all snap to n63)
- Ruddell, Maymont, Denholm, Richard, Fielding, Speers, Radisson (all snap to n75)
- Delmas, Paynton (snap to n49)
- Plus ~500 more connection pairs

**Potential fixes:**

1. **Edge interpolation for same-node cases**
   - When both settlements snap to the same edge (not just node), calculate where each settlement projects onto the edge
   - Draw the portion of the edge between those two projection points
   - Requires: Checking `snap_nodes` (the edge) and `snap_edge_t` (position along edge) from mapping data

2. **Split long edges at intermediate points**
   - Pre-process the network to split edges longer than X km
   - Would create more nodes, allowing nearby settlements to snap to different nodes
   - Requires: Regenerating `railway_network.json` and `settlement_network_mapping.json`

3. **Direct line with track styling**
   - For very close settlements (< 5km apart), a straight line may be acceptable
   - Could style it as a solid line (not dashed) to indicate it's intentional
   - Simplest solution but doesn't show actual track

**Recommended approach:** Option 1 (edge interpolation) - uses existing data without regeneration

---

### Issue 2: FAR_FROM_PATH (59 connections)

**Problem:** The path geometry doesn't get close to one or both settlements (>15km away). These are settlements that appear to be far from any railway track in the GIS data.

**Example:**
```
Penzance -> Liberty (9.1km direct): Path 24.7km from Penzance; Path 27.8km from Liberty
Liberty -> Imperial (23.1km direct): Path 28.9km from Liberty; Path 20.6km from Imperial
Salvador -> Major (33.6km direct): Path 27.8km from Major
```

**Most problematic settlements:**
| Settlement | Distance to nearest track |
|------------|--------------------------|
| Liberty | 27.8 km |
| Major | 27.8 km |
| Penzance | 24.7 km |
| Kelfield | 24.1 km |
| Bredenbury | 22.5 km |
| Imperial | 20.6 km |
| Aylesbury | 18.6 km |
| Chamberlain | 16.0 km |

**Why this happens:**
- Settlement coordinates may not align with historical railway locations
- The GIS railway data may be missing certain branch lines
- Some settlements may have been served by railways not in the dataset
- Coordinate accuracy issues in source data

**Potential fixes:**

1. **Investigate GIS data for missing tracks**
   - Check if these settlements were on railway lines not included in the shapefile
   - May require obtaining additional GIS data or manual track digitization

2. **Adjust settlement coordinates**
   - Some settlements may have moved or coordinates may be from modern census boundaries
   - Historical coordinates might align better with railway stations
   - Requires: Research into historical settlement locations

3. **Accept straight line fallback**
   - For settlements genuinely far from railways, a straight dashed line is honest
   - Could add a note/legend explaining these are approximate

4. **Increase snap distance threshold**
   - Currently snaps to nearest track even if far away
   - Could set a maximum snap distance and mark settlements as "off-network"
   - Requires: Updating `snap_settlements_to_network.py`

**Recommended approach:** First investigate the GIS data to understand if tracks are missing; if data is correct, accept straight line fallback

---

### Issue 3: WARNINGS (235 connections)

**Problem:** Path gets within 5-15km of settlements - not ideal but may be acceptable depending on the context.

**Example:**
```
Waldheim -> Blaine Lake: Path 14.4km from Waldheim
Qu'Appelle -> Odessa: Path 7.6km from Odessa
Edenwold -> Markinch: Path 8.2km from Edenwold
```

**Commonly affected settlements:**
| Settlement | Distance to path | Connections affected |
|------------|-----------------|---------------------|
| Waldheim | 14.4 km | 8 connections |
| Edenwold | 8.2 km | 4 connections |
| Sintaluta | 7.2 km | 4 connections |
| Odessa | 7.6 km | 3 connections |
| Marcelin | 5.6 km | 2 connections |

**Why this happens:**
- Similar to FAR_FROM_PATH but less severe
- Settlement-to-track alignment issues
- Long edges where the closest point is still several km away

**Potential fixes:**
- Same approaches as FAR_FROM_PATH
- For warnings (5-15km), the current visualization may be acceptable
- The `extendPathToEdge()` function already helps with this

**Recommended approach:** Monitor but likely acceptable; focus on NO_GEOMETRY and FAR_FROM_PATH first

---

## Data Files Involved

| File | Description | Regeneration needed? |
|------|-------------|---------------------|
| `data/railway_network.json` | Network graph (424 nodes, 509 edges) | Maybe (if splitting edges) |
| `data/railway_tracks.json` | Track polyline geometries (509 tracks) | No |
| `data/settlement_network_mapping.json` | Settlement to node mappings | Maybe (if re-snapping) |
| `data/settlement_connections.json` | Connection pairs with distances | No |

## Bugs Fixed

### Bug 1: Edge Interpolation for Same-Node Settlements (Jan 24, 2026)

**Problem:** When two settlements snapped to the same network node, the pathfinding returned a single-node path with no edges, resulting in no track geometry (511 connections affected).

**Solution:** Added `getSameEdgeGeometry()` and `getSharedNodeGeometry()` functions to handle:
- Two settlements on the same edge: extract the portion of track between them
- Two settlements on different edges meeting at a shared node: combine portions from each edge

**Result:** NO_GEOMETRY errors reduced from 511 to 7

### Bug 2: Track Coordinate Direction Mismatch (Jan 24, 2026)

**Problem:** The `getSharedNodeGeometry()` function assumed that `snap_nodes[0]` corresponded to the start of the track coordinates, but track geometry can be stored in either direction. This caused routes to take incorrect paths (e.g., Ruddell→Dalmeny was routing via Denholm instead of directly along the CNoR line).

**Example:**
- Track stored as `n75 -> n102` in the data
- But actual coordinates went from n102 to n75 (opposite direction)
- Code incorrectly assumed n75 was at coordinate index 0

**Solution:** Changed the logic to determine which end of the track is the shared node by comparing actual coordinate distances to the node's lat/lon, rather than assuming based on `snap_nodes` array order.

**Files modified:**
- `settlement_explorer.html`
- `one_hour_map.html`
- `scripts/verify_railway_routes.py`

**Result:** Additional 8 connections fixed (NO_GEOMETRY: 7→5, FAR_FROM_PATH: 70→64)

---

## Remaining Issues

### Current Error Count: 69 connections (3.8%)

**5 NO_GEOMETRY:**
- Qu'Appelle ↔ Indian Head (node n328)
- Indian Head ↔ McLean (node n328)
- Holdfast ↔ Aylesbury (node n422)
- Imperial ↔ Simpson (node n409)
- Drake ↔ Lockwood (node n114)

**64 FAR_FROM_PATH:** Settlements far from GIS track data (Liberty, Major, Imperial, etc.)

### Implementation Priority

1. **Investigate remaining NO_GEOMETRY (5 connections)**
   - These are on different edges meeting at a node, but one edge has no track geometry
   - May need to check if track data is missing

2. **Investigate FAR_FROM_PATH (64 connections)**
   - Requires investigation into GIS data quality
   - May require obtaining additional data
   - Some cases may be acceptable as-is

3. **WARNINGS (289 connections)**
   - Current visualization is reasonable
   - May improve naturally when fixing other issues

## Verification Script

The verification script can be run anytime to check the current state:

```bash
python3 scripts/verify_railway_routes.py
```

It outputs:
- Summary counts by category
- Specific problematic connections
- Settlement names and distances

---

*Created: January 24, 2026*
*Last updated: January 24, 2026*
*Status: In progress - 69 remaining issues*
