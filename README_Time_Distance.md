# Time-Distance Map Visualization

## Concept
Settlements reposition based on travel time rather than geography. Slower transport = settlements further apart, faster transport = settlements contract together. The dramatic effect is in railway mode, where rail-connected settlements collapse toward each other while isolated ones stay at walking-equivalent distances.

## Transport Modes
| Mode | Speed | Distance Method | Layout Effect |
|------|-------|-----------------|---------------|
| Geographic | - | Real lat/lon | Leaflet map visible, true positions |
| Walking | 5 km/h | Straight-line | Expand 1.5x from center (things feel "far") |
| Horse & Cart | 10 km/h | Straight-line | Reference scale (1.0x) |
| Railway | 40 km/h | Track routes | Stress-minimized layout: rail pairs collapse together |

Walking and horse are uniform scalings of geographic positions (same relative layout). Railway is where the layout actually distorts — computed via iterative stress minimization on the ~1,811 connection pairs.

## Technical Approach

### Layout Algorithm: Iterative Stress Minimization
- Use the ~1,811 connection pairs from `settlement_connections.json` as springs
- Each spring has a target length = travel time × pixel scale factor
- For rail-connected pairs (filtered by year): `railway_distance_km / 40 * scale`
- For non-rail pairs: `distance_km / 5 * scale`
- Run ~300 iterations from geographic starting positions, with decaying step size
- Add gentle centering force to prevent drift
- ~543,000 simple arithmetic operations — completes in <100ms

### Animation: LERP Between Modes
- Each settlement stores target positions per mode (`geoX/geoY`, `railX/railY`)
- Walking/horse targets = geographic positions scaled radially from center
- On mode switch, update targets and LERP: `s.x += (targetX - s.x) * 0.04`
- Map opacity fades with the same LERP rate
- Canvas draws dark background as map fades: `rgba(26, 26, 46, 1 - mapOpacity)`

### Map + Canvas Overlay
- Leaflet map (CartoDB dark tiles) underneath, all interaction disabled
- Canvas overlay on top (`z-index: 2`, `pointer-events: none`)
- Mouse events on the view-container, find nearest settlement for hover labels
- Geographic positions computed via `map.latLngToContainerPoint()`

## File: `time_distance.html`

### Structure
```
header (title + description)
nav (same links as other visualizations)
container (flex)
  ├── view-container (position: relative)
  │   ├── #map (Leaflet, z-index: 1)
  │   └── canvas (overlay, z-index: 2)
  └── sidebar (280px)
      ├── Transport Mode (4 mode buttons)
      ├── Year (slider + play/reset)
      ├── Statistics (settlement counts, rail pairs, avg displacement)
      ├── Legend (rail-connected, isolated, connection lines)
      └── Explanation
```

### Data
- Loads only `data/settlement_connections.json` (429 settlements, ~1,811 connection pairs)
- Reuses `buildRailwayGraph()` pattern from `journey_times.html` for year-filtered connections
- Railway layout recomputed when year changes

### Visual Elements
- **Settlement dots**: Color-coded by transport mode — red (#e94560) for walking, orange (#e09530) for horse & cart, teal (#4ecca3) for geographic/railway. Isolated settlements always gray (#666).
- **Connection lines**: Rail connections use the same mode color at low alpha, walking connections in faint gray
- **Scale bar**: Bottom-left, shows "1 hour" at current mode's speed
- **Hover labels**: Settlement name + railway info on mouseover
- **Legend**: Updates dynamically to match current mode color

### Controls
- 4 mode buttons in 2x2 grid, each color-coded to match its mode (teal, red, orange, teal)
- Year slider (1882–1920) with play/reset — recomputes railway layout on change
- Follows existing site styling (#1a1a2e, #e94560, #4ecca3)
- Color scheme matches Journey Times visualization (walking=red, horse & cart=orange, railway=teal)

## Other File Changes

### `index.html`
- Add a card for the new visualization after the existing cards

### Navigation
- Add "Time-Distance" link to nav bars in all visualization pages

## Verification
1. Open `time_distance.html` locally via `python3 -m http.server`
2. Confirm geographic mode shows settlements at correct map positions
3. Switch to Walking — settlements expand outward, map fades
4. Switch to Horse & Cart — settlements contract slightly
5. Switch to Railway — rail-connected settlements collapse together dramatically
6. Move year slider from 1882 to 1920 — railway layout progressively distorts as more connections form
7. Hover over settlements — labels appear
8. Confirm nav links work across all pages
