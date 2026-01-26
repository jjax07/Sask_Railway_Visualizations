# Remaining Railway Route Errors - Analysis and Solutions

*Created: January 26, 2026*

## Summary

After all fixes to date, **51 connections** (2.8%) still show as straight dashed lines instead of actual railway routes. These are all FAR_FROM_PATH errors where settlements are >15km from any track in our GIS datasets.

**Root cause:** These settlements were served by railway branch lines that have been completely abandoned and are not present in either:
- GEORIA Historical Railways dataset (HR_rails_NEW.shp)
- NRWN National Railway Network dataset

## Error Analysis

### Affected Settlements

| Settlement | Distance to Nearest Track | Railway | Year | Notes |
|------------|--------------------------|---------|------|-------|
| Liberty | 18.9 km | CPR | 1911 | Central SK branch |
| Imperial | 20.6 km | CPR | 1911 | Central SK branch |
| Penzance | 9.7 km | CPR | 1911 | Central SK branch |
| Major | 27.8 km | CPR | 1914 | West SK |
| Kelfield | 24.1 km | CPR | 1912 | West SK |
| Bredenbury | 22.5 km | M&NW | 1888 | East SK |
| Waldheim | 14.4 km | CNoR | 1905 | Near Saskatoon |
| Hanley | 21.5 km | QLSRSC | 1889 | Near Saskatoon |
| Dundurn | 12.9 km | QLSRSC | 1889 | Near Saskatoon |
| Kenaston | 20.5 km | CPR | 1908 | Central SK |
| Bladworth | 20.4 km | CPR | 1908 | Central SK |
| Hawarden | 14.3 km | CPR | 1912 | Central SK |

### Geographic Clusters

**Cluster 1: Central Saskatchewan CPR Branch (1911)**
- Settlements: Liberty, Imperial, Penzance, Simpson
- Location: Around longitude -105.44, running north-south
- Pattern: All served by CPR starting 1911
- Likely a single abandoned branch line

```
                 Imperial (51.35, -105.44)
                     |
                     |  (missing CPR branch)
                     |
                 Simpson (51.45, -105.44)
                     |
                     |
                 Liberty (51.14, -105.44)
                     |
                     |
                 Penzance (51.06, -105.44)
                     |
                     v
              [Existing CPR mainline]
```

**Cluster 2: West Saskatchewan CPR Branches**
- Major (CPR 1914): 27.8km from nearest track
- Kelfield (CPR 1912): 24.1km from nearest track
- These may be on separate abandoned spurs

**Cluster 3: East Saskatchewan M&NW**
- Bredenbury (M&NW 1888): 22.5km from nearest track
- Manitoba & North Western Railway not well represented in GIS data

**Cluster 4: Near Saskatoon (QLSRSC/CNoR)**
- Waldheim, Hanley, Dundurn, Kenaston, Bladworth
- These are on or near the QLSRSC line but track geometry doesn't reach them

## Connection Count by Settlement

Settlements causing the most FAR_FROM_PATH errors:

| Settlement | Affected Connections |
|------------|---------------------|
| Liberty | 12 connections |
| Imperial | 10 connections |
| Major | 6 connections |
| Bredenbury | 5 connections |
| Kelfield | 4 connections |
| Waldheim | 8 connections |

## Solution Options

### Option 1: Synthesize Missing Branch Lines (Recommended)

**Approach:** Create approximate track geometry for abandoned railways based on settlement locations and historical data.

**What we know:**
- Exact settlement coordinates
- Which railway company served them
- Year railway arrived
- Location of nearest existing tracks (connection points)

**Implementation:**
1. Create `scripts/synthesize_missing_branches.py`
2. For each cluster of affected settlements:
   - Find nearest node on existing network
   - Create synthetic nodes at each settlement location
   - Connect with edges following logical routing (north-south or east-west)
   - Add track geometry as straight lines between points
3. Regenerate mappings with `snap_settlements_to_network.py`
4. Verify with `verify_railway_routes.py`

**Pros:**
- Fully automated
- Connections will show actual settlement locations
- Historically accurate (settlements were connected)

**Cons:**
- Track geometry is approximate (straight lines between settlements)
- Doesn't reflect actual historical route curvature
- May not match true junction points

**Estimated impact:** Would fix 40-45 of 51 errors

### Option 2: Find Historical Maps and Digitize

**Approach:** Locate historical railway maps from 1910-1920 and manually trace the abandoned branch lines.

**Potential sources:**
- Library and Archives Canada
- Saskatchewan Archives
- CPR corporate archives
- University of Saskatchewan map collection
- David Rumsey Map Collection (online)

**Implementation:**
1. Find high-resolution historical railway maps
2. Georeference maps in GIS software (QGIS)
3. Digitize the missing branch lines as polylines
4. Export to GeoJSON and merge with existing data
5. Regenerate network and mappings

**Pros:**
- Historically accurate track geometry
- Would show actual curves and junction points

**Cons:**
- Time-intensive manual work
- Requires finding suitable historical maps
- Maps may not be detailed enough for precise digitization

**Estimated impact:** Would fix all 51 errors if maps are found

### Option 3: Use Satellite/Aerial Imagery

**Approach:** Trace abandoned railway beds visible in modern satellite imagery.

**How it works:**
- Abandoned railways often leave visible traces:
  - Straight lines through agricultural land
  - Slightly different vegetation color
  - Old rail beds converted to roads or trails

**Implementation:**
1. Use Google Earth or similar to identify old rail beds
2. Trace visible alignments manually
3. Create GeoJSON track data
4. Merge with existing network

**Pros:**
- Can be done without historical maps
- Shows actual physical route

**Cons:**
- Not all abandoned lines are visible
- Very time-intensive
- May miss lines completely removed

### Option 4: Accept Straight Line Fallback

**Approach:** Document these connections as having approximate routes and accept the dashed line visualization.

**Implementation:**
1. Add a legend note explaining dashed lines = approximate route
2. Document affected settlements in visualization UI
3. No data changes needed

**Pros:**
- No additional work required
- Honest representation of data limitations

**Cons:**
- 51 connections (2.8%) show as straight lines
- Less visually appealing
- May confuse users

## Recommendation

**Start with Option 1 (Synthesize Missing Branches)** for quick wins:
- Automatically generate approximate routes for the main clusters
- Will fix ~80% of remaining errors with minimal effort

**Follow up with Option 2 (Historical Maps)** for accuracy:
- Research available historical railway maps
- Prioritize the Central SK CPR branch (Liberty/Imperial cluster)
- Digitize if good maps are found

**Fall back to Option 4** for any remaining unfixable cases.

## Data Files That Would Change

| File | Changes |
|------|---------|
| `data/railway_network.json` | Add synthetic nodes and edges |
| `data/railway_tracks.json` | Add synthetic track geometry |
| `data/settlement_network_mapping.json` | Regenerate after network changes |

## Verification

After any changes, run:
```bash
python3 scripts/verify_railway_routes.py
```

Current baseline: 51 FAR_FROM_PATH errors

## Historical Context

The missing branch lines were likely:
- **Built:** 1908-1914 during the railway boom
- **Abandoned:** 1930s-1960s as branch lines became unprofitable
- **Removed:** Rails torn up for scrap, especially during WWII
- **Not surveyed:** Modern GIS datasets focus on active railways

The GEORIA historical dataset ends coverage around 1930, and NRWN only includes currently active railways, leaving a gap for lines abandoned between 1930-present.

---

*This document will be updated as solutions are implemented.*
