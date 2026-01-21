# Saskatchewan Railway Network Graph (Future Visualization)

An interactive network visualization showing all one-hour railway connections across Saskatchewan simultaneously.

## Concept

Unlike the settlement-focused corridor visualizations that show connections from a single settlement's perspective, this visualization displays the entire provincial railway network as an interconnected graph, revealing the overall structure of connectivity.

## Proposed Features

### Core Functionality
- All 429 settlements displayed as nodes on a map
- Lines (edges) connecting settlements within 1 hour of train travel (40 km)
- Time slider (1882-1920) to animate network growth
- Color-coded edges by railway company

### Interactive Elements
- Play/pause animation to watch connectivity evolve
- Toggle individual railway companies on/off
- Hover over settlements to highlight their connections
- Click settlement to see connection details

### Analytics Panel
- Total connections count by year
- Most connected settlements (highest degree nodes)
- Isolated settlements (no connections)
- Network density statistics
- Clusters/components count

## Technical Approach

### Data Requirements

**Pre-calculated connection data:**
```json
{
  "connections": [
    {
      "settlement_a": "Saskatoon",
      "settlement_b": "Warman",
      "distance_km": 12.5,
      "railway": "QLSRSC",
      "year_connected": 1890
    }
  ]
}
```

### Distance Calculation
- Haversine formula for all settlement pairs
- Filter pairs where distance <= 40 km
- Approximately 92,000 potential pairs to evaluate
- Expected ~500-1000 connections within threshold

### Connectivity Logic
Two settlements are connected when:
1. Distance between them <= 40 km
2. Both settlements have the same railway
3. Both settlements have that railway by the given year

### Performance Considerations
- Pre-calculate all connections (don't compute in browser)
- Use canvas rendering for edges if > 500 connections
- Consider edge bundling for visual clarity
- Lazy load connection details on hover

## Visualization Insights

This network view could reveal:
- **Hub settlements**: High-degree nodes that connected many communities
- **Railway corridors**: Dense linear clusters along main lines
- **Regional isolation**: Areas with sparse connectivity
- **Network evolution**: How connectivity spread over time
- **Company territories**: Geographic clustering by railway

## UI Mockup

```
+--------------------------------------------------+
|  Saskatchewan Railway Network 1882-1920          |
+--------------------------------------------------+
|                                      | Stats     |
|    [MAP WITH NODES AND EDGES]        | --------- |
|                                      | Year: 1905|
|                                      | Nodes: 429|
|                                      | Edges: 234|
|                                      | Clusters:5|
|                                      |           |
|                                      | Top Hubs: |
|                                      | 1. Stoon  |
|                                      | 2. Regina |
|                                      | 3. Moose J|
+--------------------------------------------------+
|  [|< ] [<] [ 1882 ====|==== 1920 ] [>] [>|]     |
+--------------------------------------------------+
|  [x] CPR  [x] QLSRSC  [x] CNoR  [x] GTPR        |
+--------------------------------------------------+
```

## Dependencies

- Leaflet.js for base map
- Potential additions:
  - D3.js for network analysis/force layout option
  - Turf.js for geographic calculations (if needed client-side)

## Related Files

- `data/settlements.json` - Settlement coordinates
- `data/railway_timeline.json` - Railway arrival dates
- `data/network_connections.json` - To be generated

## Status

**Planned** - Documented for future implementation after Settlement Explorer visualization is complete.

---

*Documented January 2026*
