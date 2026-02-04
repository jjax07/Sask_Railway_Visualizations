# Transport Eras — Unified Animation Page

## Overview

A single-page visualization (`transport_eras.html`) that smoothly animates Saskatchewan settlements through four transport eras using one slider. Based on `time_distance.html`, it replaces discrete mode buttons with a continuous 0–100 slider that interpolates positions, colors, and map visibility across stages.

## New file: `transport_eras.html`

### Slider-to-position mapping

Single slider 0–100, mapped to 4 stages with interpolation between them:

| Slider range | Stage      | Positions                              | Map opacity | Dot color | Connections                        |
|-------------|------------|----------------------------------------|-------------|-----------|-------------------------------------|
| 0–25        | Geographic | Static at geo positions                | 1.0         | default   | All shown (dim)                     |
| 25–50       | Walking    | Lerp geographic → walking (1.2x expand)| 1.0 → 0.0  | Red       | All shown, tinted red               |
| 50–75       | Horse      | Lerp walking → horse (1.0x, contracts) | 0.0         | Orange    | All shown, tinted orange            |
| 75–100      | Railway    | Lerp horse → railway (stress-minimized)| 0.0 → 0.25 | Teal (rail) / dimmed (off-rail) | Only rail connections (colored by company) |

Each settlement's `x,y` is set directly from the slider position — no LERP animation loop. Positions are immediate. Colors and line visibility crossfade during transitions.

### Railway year

Fixed at **1920**. `computeRailwayPositions()` is called once at init.

### Auto-play

Play button advances slider via `requestAnimationFrame`. Target duration ~20 seconds total, with **2-second pauses** at positions 0, 25, 50, 75, and 100.

### Sidebar contents

- **Stage name + description** — updates as slider moves through each stage
- **Slider** + Play / Pause / Reset buttons
- **Legend** — updates per stage (shows relevant colors and line types)
- **Explanation text** — describes what the visualization shows

### Drawing

Reuses existing `draw()` logic from `time_distance.html` but determines colors/visibility from the slider position instead of a `currentMode` string. Dot colors, connection visibility, and line colors interpolate smoothly during stage transitions.

## Files to modify

### `index.html`

Add a new card for Transport Eras:

```html
<div class="card">
    <div class="card-image">🎬</div>
    <div class="card-content">
        <h2>Transport Eras</h2>
        <p>Scrub through four transport eras and watch settlements shift from geographic positions
        through walking, horse & cart, and railway time-distance layouts.</p>
        <ul class="card-features">
            <li>Unified slider across all transport modes</li>
            <li>Smooth interpolation between eras</li>
            <li>Auto-play with stage pauses</li>
            <li>Railway connections colored by company</li>
        </ul>
        <a href="transport_eras.html" class="btn">View Animation</a>
    </div>
</div>
```

### All nav bars

Add `<a href="transport_eras.html">Transport Eras</a>` to the nav bar in these 8 files:

- `one_hour_map.html`
- `railway_timeline.html`
- `settlement_explorer.html`
- `network_graph.html`
- `isochrone.html`
- `journey_times.html`
- `travel_race.html`
- `time_distance.html`

Also include the nav bar in `transport_eras.html` itself.

## Verification

1. Open `localhost:8000/transport_eras.html`
2. Scrub slider through all stages — verify smooth position interpolation
3. Verify map fades out during walking stage and partially returns during railway stage
4. Verify dot colors transition: default → red → orange → teal
5. Verify railway stage shows only rail connections colored by company
6. Hit Play — verify auto-play advances with 2-second pauses at each stage boundary (0, 25, 50, 75, 100)
7. Verify all nav bars link to the new page
8. Verify the index.html card appears and links correctly
