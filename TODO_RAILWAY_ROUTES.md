# TODO: Railway Route Line Visualization

## Current Status: In Progress - Needs Troubleshooting

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

5. **Fallback to straight lines**
   - If railway path cannot be found, falls back to dashed straight line

### Key Functions Added

```javascript
// Distance calculation
haversineDistance(lat1, lon1, lat2, lon2)

// Pathfinding
findPath(startNode, endNode)  // Dijkstra's algorithm
getPathGeometry(path)          // Convert node path to coordinates

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

## Still Needs Work

### Known Issues to Troubleshoot
- Some railway route lines may still not display correctly
- Need to verify routes for various settlement pairs
- May need to investigate specific problematic connections (user mentioned Saskatoon-Osler as an example that needed fixing)

### Testing Needed
- Test multiple settlement pairs to verify routes look correct
- Check edge cases:
  - Settlements that are very close together
  - Settlements on different railway lines
  - Settlements at railway junctions

### Potential Improvements
- Visual debugging: temporarily show network nodes to verify snapping
- Add console logging to help debug specific routes
- Consider whether some settlements might be snapped to wrong nodes

---
*Last updated: January 23, 2026*
*Status: Awaiting further troubleshooting*
