# TODO: Railway Route Line Visualization

## Current Status: Complete

## What We've Done

### Goal
Replace the straight "as the crow flies" connection lines between settlements with lines that follow the actual railway routes.

### Implementation Steps Completed

1. **Added railway route drawing to visualizations**
   - `settlement_explorer.html` - Shows railway routes between selected settlement and nearby connected settlements
   - `one_hour_map.html` - Shows railway routes from Saskatoon to connected settlements

2. **Pathfinding implementation**
   - Uses Dijkstra's algorithm to find shortest path between settlement nodes
   - Loads network graph from `data/railway_network.json`
   - Loads track geometry from `data/railway_tracks.json`
   - Loads settlement-to-node mappings from `data/settlement_network_mapping.json`

3. **Path geometry assembly**
   - `getPathGeometry()` function assembles polyline coordinates from path segments
   - Handles coordinate reversal when segments need to connect end-to-end

4. **Path trimming to settlement locations**
   - Added `findClosestPointIndex()` - finds the point on a path closest to a given lat/lon
   - Added `trimPathToSettlements()` - trims the path to start and end at actual settlement coordinates
   - This prevents lines from extending past the destination settlement (e.g., Saskatoon-Osler was extending to Prince Albert)

5. **Edge extension for mid-edge snapped settlements** (Added Jan 24, 2026)
   - Added `extendPathToEdge()` function to handle settlements snapped to the middle of long edges
   - Problem: Some settlements (e.g., Dundurn) are snapped to long edges but the pathfinding stops at the edge's endpoint node, missing the track geometry that passes near the settlement
   - Solution: When a settlement is snapped to an edge, extend the path geometry to include the portion of that edge closest to the settlement
   - Example: Dundurn is snapped to the n132-n165 edge (216km long). The path used to stop at n132 (30km from Dundurn), but now extends along the edge to the point only 1.2km from Dundurn

6. **Fallback to straight lines**
   - If railway path cannot be found, falls back to dashed straight line

### Key Functions Added

```javascript
// Distance calculation
haversineDistance(lat1, lon1, lat2, lon2)

// Pathfinding
findPath(startNode, endNode)  // Dijkstra's algorithm
getPathGeometry(path)          // Convert node path to coordinates

// Path extension for mid-edge snapped settlements
extendPathToEdge(coords, mapping, settlementLat, settlementLon, atEnd)

// Path trimming
findClosestPointIndex(coords, targetLat, targetLon)
trimPathToSettlements(coords, fromLat, fromLon, toLat, toLon)

// Main drawing function
drawRailwayConnection(fromSettlement, toSettlement, color, weight, opacity)
```

### Files Modified
- `settlement_explorer.html` - Full implementation with all helper functions
- `one_hour_map.html` - Full implementation with all helper functions

### Data Files Used
- `data/railway_network.json` - Network graph (nodes and edges)
- `data/railway_tracks.json` - Track polyline geometries
- `data/settlement_network_mapping.json` - Settlement to network node mappings

## Known Limitations

### Network Data Gaps
- Some settlements may still show straight lines if:
  - The GIS track data is missing for that section
  - The settlement is too far from any track in the network
  - The pathfinding cannot find a route between the settlements

### Long Edges in Network
- The railway network contains some very long edges (e.g., n132-n165 is 216km)
- The `extendPathToEdge()` function handles this by including partial edge geometry
- Future improvement: Could split long edges at intermediate points for better snapping

---
*Last updated: January 24, 2026*
*Status: Complete*
