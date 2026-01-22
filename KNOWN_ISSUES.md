# Known Issues and Outstanding Tasks

## Data Cleanup Completed (January 2026)

The following data cleanup work was completed by cross-referencing the original UrbanSaskHist spreadsheet with historical GIS railway data from the Canadian Historical GIS Partnership (doi-10.5683-sp2-uccfvq):

### Cleanup Summary
- **Starting discrepancies:** 272
- **Resolved discrepancies:** 261
- **Remaining discrepancies:** 11 (requiring further historical research)

### Changes Made to UrbanSaskHist_Update_Jan_2026.xlsx
1. **SOO → CPR:** 4 entries corrected (SOO Line was a CPR subsidiary)
2. **Date corrections (≤2 year difference):** 129 entries updated with GIS dates
3. **Missing railways added:** 114 settlements received additional railway data from GIS
4. **Missing data filled:** 35 entries with no original data received GIS year and railway
5. **Typo fixes:** GPTR → GTPR corrections
6. **GIS-based corrections:** 15 additional settlements corrected based on likelihood analysis
7. **M&NW settlements confirmed:** 6 settlements with M&NW as first railway confirmed correct
8. **No GIS coverage settlements:** 20 settlements confirmed using original data

### New Data File Created
- `Historical_Railway_Data_By_Settlement.xlsx` - Comparison spreadsheet showing:
  - GIS railway data (year and railway lines)
  - Original spreadsheet data
  - Discrepancy column
  - 20km search radius data (for comparison)

## Remaining Data Issues

### 1. Remaining Discrepancies (11 entries)
After cleanup, 11 discrepancies remain that require further historical research:

**Year differences needing research:**
- Lebret, Macoun, Morse, Hudson Bay Jct, Sutherland

**Railway verification needed:**
- Rosthern (operator history - CPR/CNoR on QLSRSC line)
- Weyburn, Warman, Pangman, Mazenod (CPR/CNoR verification)
- Lockwood (no data in either source)

**Resolution:** Review `Historical_Railway_Data_By_Settlement.xlsx` - entries marked with `Further_research_needed` column.

### 2. CPR Takeover of QLSRSC Line
The QLSRSC (Qu'Appelle, Long Lake & Saskatchewan Railway) was leased by CPR from 1896-1906. Settlements on this line should potentially show both QLSRSC and CPR service during this period.

**Affected settlements:** Settlements between Regina and Prince Albert via Saskatoon (Lumsden, Craven, Bethune, Chamberlain, Craik, Davidson, Hanley, Dundurn, Saskatoon, Warman, Osler, Rosthern, Duck Lake, etc.)

**Current state:** These settlements only show QLSRSC, not the CPR lease period.

**Resolution:** Research exact CPR lease dates and add to `KNOWN_RAILWAY_YEARS`.

### 3. Post-1918 CN Consolidation
CNoR and GTPR were absorbed into CN (Canadian National) between 1918-1923. The current data ends at 1920, so this transition is partially captured.

**Current handling:** "CN" entries in spreadsheet are mapped to "Other" category.

**Consideration:** May want to extend timeline to 1923 to show full consolidation.

### 4. GIS Data Limitations
The historical GIS railway data (doi-10.5683-sp2-uccfvq) does not include:
- M&NW (Manitoba & North Western Railway)
- Some branch lines that may have been in the original research

Settlements showing "Missing in GIS" discrepancies may have correct original data from other sources.

## Testing Checklist

### Settlement Explorer (`settlement_explorer.html`)

- [x] **Saskatoon:** Verified connections match `one_hour_map.html` (after fixing CPR data)
- [x] **Battleford:** North Battleford (5.3km) connected via CNoR (1905) ✓
- [x] **Remote settlements:** Verified - settlements with no shared railway show "no shared railway" message ✓
- [x] **Time slider:** Connections appear/disappear correctly based on year ✓
- [x] **Play animation:** Progresses smoothly through years ✓
- [x] **Search:** Typing partial name filters dropdown correctly ✓
- [x] **Click to select:** Fixed - clicking any settlement dot now works (was blocked by multi-railway ring overlay)
- [x] **Multi-railway markers:** Changed from orange rings to orange diamond-shaped markers for better click interaction

### Railway Timeline (`railway_timeline.html`)

- [x] **Animation:** Year progression smooth, stops at 1920 (no loop) ✓
- [x] **Railway toggles:** Each railway can be shown/hidden independently ✓
- [x] **Bar chart:** Updates as animation progresses ✓
- [x] **Marker size:** Reduced to radius 3 for cleaner visualization ✓

### One-Hour Map (`one_hour_map.html`)

- [ ] **Saskatoon-centered:** 40km radius should show correct settlements
- [ ] **Time slider:** 5-year increments from 1890-1920

## Known Limitations

### 1. Connection Logic Simplification
The visualization assumes two settlements are "connected" if they share the same railway and are within 40km. In reality, railway connections depended on:
- Actual track routing (not straight-line distance)
- Train schedules and stopping patterns
- Whether the line was continuous or required transfers

### 2. Distance as Proxy for Travel Time
40km = 1 hour assumes 40 km/h average speed, which was typical for branch lines with stops. Main line express trains were faster; some branch lines were slower.

### 3. Multi-Railway Detection
Currently 7 settlements are identified as multi-railway junctions in the visualization. More may exist but aren't captured in the `KNOWN_RAILWAY_YEARS` dictionary in `update_multi_railways.py`.

### 4. Railway Name Variations
The spreadsheet contains various spellings/abbreviations:
- GTPR/GTP (all Grand Trunk Pacific) - *GPTR typos have been corrected*
- CNoR/CNOR (Canadian Northern)
- M&NW, M (mapped to "Other") - *SOO entries have been corrected to CPR*

Some entries may be missed if they use unexpected abbreviations.

## Future Enhancements

### Data Quality
1. Research and add missing railway arrival years
2. Add CPR lease period for QLSRSC settlements
3. Verify arrival years against primary sources (railway company records, newspaper archives)

### Visualization Features
1. Show actual railway routes on map (not just settlement points)
2. Add popup information when clicking settlements
3. Show all railways serving a settlement in the info panel
4. Add filtering by railway company in Settlement Explorer

### Documentation
1. Add methodology notes about data sources and limitations
2. Create data dictionary for JSON file structures

## Bug Fixes Completed (January 2026)

### 1. Multi-Railway Marker Click Issue
**Problem:** Clicking on multi-railway settlements (like Saskatoon) after selecting another settlement did nothing.

**Cause:** The orange ring overlay was intercepting click events before they reached the marker.

**Fix:** Changed multi-railway indicators from orange rings to orange diamond-shaped markers using Leaflet `divIcon`.

### 2. Saskatoon Missing CPR Connection
**Problem:** Nearby settlements like Sutherland and Warman showed "no shared railway" with Saskatoon despite being on CPR.

**Cause:** Saskatoon was missing CPR (1896) in the `KNOWN_RAILWAY_YEARS` dictionary.

**Fix:** Added `('Saskatoon', 'CPR'): 1896` to `scripts/update_multi_railways.py`.

---

*Last updated: January 22, 2026*
