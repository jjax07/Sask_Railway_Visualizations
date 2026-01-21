# Known Issues and Outstanding Tasks

## Data Issues

### 1. Missing Railway Arrival Years (28 entries)
When running `update_multi_railways.py`, approximately 28 settlement-railway pairs could not be matched to arrival years. These need historical research to determine when each railway reached these settlements.

**How to identify:** Run the script and look for "Unmatched (no year available)" count in output.

**Resolution:** Add entries to `KNOWN_RAILWAY_YEARS` dict in `scripts/update_multi_railways.py` after researching historical records.

### 2. CPR Takeover of QLSRSC Line
The QLSRSC (Qu'Appelle, Long Lake & Saskatchewan Railway) was leased by CPR from 1896-1906. Settlements on this line should potentially show both QLSRSC and CPR service during this period.

**Affected settlements:** Settlements between Regina and Prince Albert via Saskatoon (Lumsden, Craven, Bethune, Chamberlain, Craik, Davidson, Hanley, Dundurn, Saskatoon, Warman, Osler, Rosthern, Duck Lake, etc.)

**Current state:** These settlements only show QLSRSC, not the CPR lease period.

**Resolution:** Research exact CPR lease dates and add to `KNOWN_RAILWAY_YEARS`.

### 3. Post-1918 CN Consolidation
CNoR and GTPR were absorbed into CN (Canadian National) between 1918-1923. The current data ends at 1920, so this transition is partially captured.

**Current handling:** "CN" entries in spreadsheet are mapped to "Other" category.

**Consideration:** May want to extend timeline to 1923 to show full consolidation.

## Testing Checklist

### Settlement Explorer (`settlement_explorer.html`)

- [ ] **Saskatoon:** Should show same connections as `one_hour_map.html`
- [ ] **Battleford:** Should show North Battleford (5.3km) as connected
- [ ] **Remote settlements:** Select a settlement with no nearby connections, verify informative message displays
- [ ] **Time slider:** Connections should appear/disappear based on year
- [ ] **Play animation:** Should progress smoothly through years
- [ ] **Search:** Typing partial name should filter dropdown
- [ ] **Click to select:** Clicking any settlement dot should select it
- [ ] **Multi-railway rings:** Orange rings should be visible on Saskatoon, Regina, Moose Jaw, Prince Albert, Yorkton, Weyburn, Nokomis, Biggar

### Railway Timeline (`railway_timeline.html`)

- [ ] **Animation:** Year progression should be smooth
- [ ] **Railway toggles:** Each railway can be shown/hidden independently
- [ ] **Bar chart:** Should update as animation progresses

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
Only 8 settlements are currently identified as multi-railway junctions. More may exist but aren't captured in the spreadsheet data or `KNOWN_RAILWAY_YEARS`.

### 4. Railway Name Variations
The spreadsheet contains various spellings/abbreviations:
- GTPR/GTP/GPTR (all Grand Trunk Pacific)
- CNoR/CNOR (Canadian Northern)
- M&NW, SOO, M (mapped to "Other")

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

---

*Last updated: January 2026*
