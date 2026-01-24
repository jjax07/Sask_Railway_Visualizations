# TODO: Space-Time Compression Visualization

## Concept
Railways compressed space-time by dramatically reducing travel times. Before railways, people walked (5 km/h) or took wagons (10 km/h). Railways at 40 km/h expanded the reachable world 4-8x.

This visualization will show settlement relationships through this new space-time relationship - how railways restructured the perceived geography of Saskatchewan.

## Demo Prototypes

Four demo concepts have been created for evaluation:

### 1. Time-Warped Cartogram (`demo_cartogram.html`)
- **Concept**: Distort map based on travel time rather than geographic distance
- **Features**:
  - Toggle between geographic and time-distance views
  - Animated transition showing settlements "pulling in" toward railway hubs
  - Select different hub centers (Saskatoon, Regina, etc.)
  - Year slider to see how connectivity evolved
- **Key insight**: Railway-connected settlements cluster together; isolated ones remain at "walking distance"

### 2. Isochrone Comparison (`demo_isochrone.html`)
- **Concept**: Nested circles showing equal travel time by different modes
- **Features**:
  - Walking (5 km/h), wagon (10 km/h), railway (40 km/h) circles
  - Toggle time periods (30 min to 8 hours)
  - Shows settlements within each travel range
  - Calculates expansion factor (typically 8x)
- **Key insight**: The "reachable world" expands dramatically with railways

### 3. Journey Time Matrix (`demo_matrix.html`)
- **Concept**: Heatmap grid showing travel times between major settlements
- **Features**:
  - Side-by-side comparison: walking vs railway
  - Color scale from green (hours) to red (days)
  - Hover for detailed distance/time info
  - Statistics: average times, compression factor
- **Key insight**: Multi-day journeys became same-day trips

### 4. Gravitational Pull (`demo_gravity.html`)
- **Concept**: Railway hubs act as "gravity wells" pulling connected settlements closer
- **Features**:
  - Physics-based animation with settlements as particles
  - Major junctions (Saskatoon, Regina, etc.) as gravity sources
  - Connected settlements pulled in; isolated ones drift outward
  - Adjustable gravity strength
- **Key insight**: Railways restructured perceived geography around hub cities

## To View Demos

```bash
cd Sask_Railway_Visualizations
python3 -m http.server 8080
# Then open http://localhost:8080/demo_cartogram.html (etc.)
```

## Next Steps

1. **Evaluate demos** - Decide which concept(s) to develop further
2. **Refine chosen approach** - Polish UI, improve animations
3. **Add to main navigation** - Integrate with existing visualizations
4. **Historical accuracy** - Ensure travel time assumptions are realistic
5. **Combine concepts?** - Could merge isochrone + cartogram for richer viz

## Research Questions

- What was realistic wagon speed on prairie trails? (5-10 km/h assumed)
- Did railway speeds vary by line type? (mainline vs branch)
- How did winter affect pre-railway travel times?
- What about river crossings, terrain obstacles?

## Technical Notes

- Uses existing `settlement_connections.json` with `railway_distance_km` field
- Canvas-based rendering for cartogram and gravity demos
- Leaflet maps for isochrone demo
- All demos load settlement data dynamically

---
*Created: January 23, 2026*
