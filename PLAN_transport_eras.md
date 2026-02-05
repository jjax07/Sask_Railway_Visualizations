# Transport Eras — Unified Animation Page

## Status: IMPLEMENTED (2026-02-05)

## Overview

A single-page visualization (`transport_eras.html`) that smoothly animates Saskatchewan settlements through four transport eras using one slider. Based on `time_distance.html`, it replaces discrete mode buttons with a continuous 0–100 slider that interpolates positions and colors across stages.

## Implementation Summary

### Slider-to-position mapping

Single slider 0–100, mapped to 4 stages with interpolation between them:

| Slider range | Stage      | Positions                              | Map opacity | Dot color |
|-------------|------------|----------------------------------------|-------------|-----------|
| 0–25        | Geographic | Static at geo positions                | 1.0         | Grey (#9A9B9D) |
| 25–50       | Walking    | Lerp geographic → walking (1.2x expand)| 0.0         | Rust (#c75d38) |
| 50–75       | Horse      | Lerp walking → horse (1.0x)            | 0.0         | Gold (#f1c730) |
| 75–100      | Railway    | Lerp horse → railway (stress-minimized)| 0.0         | Green (#0b6a41) |

### Key design decisions

1. **No connection lines** — Lines were removed for visual clarity. The settlement positions tell the story without needing explicit connections.

2. **No stage pauses** — Auto-play runs continuously without pausing at stage boundaries. Pauses caused timing issues and were removed for smoother animation.

3. **Fast color transitions** — Colors transition over 5 slider units instead of 25, making era changes more distinct.

4. **Actual railway connections** — Uses `railway_network.json` and `settlement_network_mapping.json` to find true railway neighbors via graph traversal, not just 40km geographic neighbors. This ensures isolated settlements like Hudson Bay Jct show proper connections.

5. **USask branding** — Colors updated to University of Saskatchewan palette:
   - Primary: USask Green (#0b6a41)
   - Secondary: USask Gold (#f1c730)
   - Greys: Cool Grey 7/11 (#9A9B9D, #4D4E53)

### Fixed year

Railway positions computed for **1920** (fixed, no year slider).

### Navigation

Replaced horizontal nav bar with dropdown menu button ("Other Visualizations") to accommodate growing number of visualizations.

## Files created/modified

### New file: `transport_eras.html`

Complete visualization with:
- Era slider (0-100)
- Play/Pause/Reset controls
- Legend showing all four era colors
- Statistics panel
- Hover tooltips
- USask-branded color scheme
- Dropdown navigation menu

### Modified: `index.html`

Added card for Transport Eras visualization.

### Modified: Navigation in 8 files

Added Transport Eras link to nav bars:
- `one_hour_map.html`
- `railway_timeline.html`
- `settlement_explorer.html`
- `network_graph.html`
- `isochrone.html`
- `journey_times.html`
- `travel_race.html`
- `time_distance.html`

## Data sources

- `data/settlement_connections.json` — Settlement positions and geographic connections
- `data/railway_network.json` — Railway network graph (nodes and edges)
- `data/settlement_network_mapping.json` — Maps settlements to network nodes

## USask Color Palette Reference

From `usask_freelancers_guide.pdf`:

| Color | Hex | Usage |
|-------|-----|-------|
| USask Green | #0b6a41 | Primary accent, Railway era, buttons |
| USask Gold | #f1c730 | Secondary accent, Horse era, highlights |
| Cool Grey 7 | #9A9B9D | Geographic era, subtle text |
| Cool Grey 11 | #4D4E53 | Sidebar, nav backgrounds |
| White | #ffffff | Header text |
| Black | #000000 | Canvas background |

## USask Branding Rollout (2026-02-05)

The USask branding has been applied to the following visualizations:

| Visualization | File | Status |
|---------------|------|--------|
| Transport Eras | `transport_eras.html` | ✅ Complete |
| One Hour Corridor | `one_hour_map.html` | ✅ Complete |
| Railway Timeline | `railway_timeline.html` | ✅ Complete |
| Settlement Explorer | `settlement_explorer.html` | ✅ Complete |
| Travel Time Comparison | `isochrone.html` | ✅ Complete |
| Network Graph | `network_graph.html` | Pending |
| Journey Times | `journey_times.html` | Pending |
| Time Simulation | `travel_race.html` | Pending |
| Time-Distance | `time_distance.html` | Pending |
| Home/Index | `index.html` | Pending |

### Common branding elements applied:

1. **Dark backgrounds**: `#1a1a1e` (header/sidebar), `#252528` (panels), `#000000` (body)
2. **Dropdown navigation**: Replaced horizontal nav links with "Other Visualizations ▼" dropdown
3. **USask color palette**: Green (#0b6a41), Gold (#f1c730), Cool Grey (#9A9B9D, #4D4E53)
4. **Gold progress sliders**: Year sliders show gold progress on grey track
5. **Consistent button styling**: Green buttons with hover states

### Visualization-specific notes:

- **Railway Timeline**: Railway company colors updated (CPR=rust, QLSRSC=green, CNoR=gold, GTPR=purple)
- **Settlement Explorer**: Rust (#c75d38) used for "newly connected" to distinguish from selected (green)
- **Travel Time Comparison**: Railway radius circle removed; settlements colored by innermost travel circle

## Future work

- Complete USask branding for remaining visualizations
- Consider adding optional connection lines toggle to Transport Eras
- Potential year slider for railway era (currently fixed at 1920)
