# Saskatchewan Railway Visualizations

Interactive visualizations exploring how railway networks shaped settlement patterns in Saskatchewan from 1882 to 1920.

**Live Site:** [https://jjax07.github.io/Sask_Railway_Visualizations/](https://jjax07.github.io/Sask_Railway_Visualizations/)

## Visualizations

### 1. One-Hour Railway Corridor from Saskatoon

An interactive map showing which settlements could be reached from Saskatoon within one hour by train (40 km at 40 km/h average speed) as the railway network expanded.

**Features:**
- Interactive time slider (1890-1920 in 5-year increments)
- 40 km radius circle showing 1-hour travel range
- Settlement markers appear as they become connected
- Play/pause animation to watch connectivity grow
- Sidebar with statistics and settlement list

**Key Findings:**
| Year | Connected Settlements |
|------|----------------------|
| 1890 | 1 (Osler via QLSRSC) |
| 1905 | 4 (added Warman, Langham, Aberdeen via CNoR) |
| 1910 | 11 (major expansion with GTPR and CPR) |

### 2. Settlement Explorer

Select any of the 429 Saskatchewan settlements to discover which neighbours were reachable within one hour by train (40 km radius). Watch connectivity evolve from 1882 to 1920.

**Features:**
- Searchable dropdown with all 429 settlements
- All settlements visible on map (click any to explore)
- 40 km radius circle showing potential connections
- Connection lines drawn between railway-connected settlements
- Time slider (1882-1920) showing connectivity evolution
- "New this year" highlighting for connections made in selected year
- Color-coded markers:
  - **Red**: Selected settlement
  - **Green**: Connected by railway (within 40km)
  - **Yellow**: Newly connected this year
  - **Gray**: Within 40km but no shared railway yet
  - **Dark gray dots**: All other settlements
  - **Orange diamond**: Multi-railway junction (served by 2+ railways)

**Connection Logic:**
Two settlements are "connected" when:
1. Both are within 40 km of each other
2. Both share the same railway line
3. Both have received that railway by the selected year

**Multi-Railway Junctions:**
Eight major settlements were served by multiple railway companies, indicated by orange diamond markers:
| Settlement | Railways |
|------------|----------|
| Saskatoon | QLSRSC (1889), CPR (1896), CNoR (1905), GTPR (1908) |
| Regina | CPR (1882), QLSRSC (1889), CNoR (1906), GTPR (1911) |
| Moose Jaw | CPR (1882), CNoR (1908), GTPR (1912) |
| Prince Albert | QLSRSC (1890), CNoR (1906) |
| Yorkton | Other/M&NW (1889), GTPR (1908), CNoR |
| Weyburn | CPR (1893), CNoR (1910) |
| Nokomis | CPR (1907), GTPR (1908) |
| Biggar | CPR (1907), GTPR (1910) |

### 3. Railway Network Timeline

Watch the four major railway companies expand across Saskatchewan year by year.

**Features:**
- Province-wide map showing all 429 settlements
- Year-by-year animation (1882-1920)
- Color-coded by railway company
- Toggle visibility of individual railways
- Bar chart showing settlements added per year

**Railway Companies:**
| Railway | Color | Period | Description |
|---------|-------|--------|-------------|
| CPR | Red | 1882+ | Canadian Pacific - First transcontinental through southern SK |
| QLSRSC | Green | 1889-90 | Qu'Appelle, Long Lake & Saskatchewan - Regina to Prince Albert via Saskatoon |
| CNoR | Yellow | 1899+ | Canadian Northern - Northerly competitor through Saskatoon |
| GTPR | Purple | 1905+ | Grand Trunk Pacific - Third transcontinental via Saskatoon |

### 4. Network Graph

Interactive network graph visualization showing all 429 Saskatchewan settlements as nodes and approximately 1,121 railway connections as edges. Toggle between Geographic and Network views to explore the data differently.

**View Modes:**
- **Geographic View**: Nodes positioned by lat/lon on a light CartoDB Voyager basemap (distinct from Railway Timeline's dark map)
- **Network View**: Force-directed layout on dark background - nodes arranged by connectivity, revealing network structure that geography obscures (hubs cluster in center, isolated nodes drift to edges)

**Features:**
- Toggle between Geographic and Network views with animated transitions
- Node size scales with degree (number of connections)
- Nodes colored by first railway (CPR=red, QLSRSC=green, CNoR=yellow, GTPR=purple)
- Multi-railway junctions shown as diamonds (e.g., Saskatoon, Regina, Moose Jaw)
- Railway connections shown as colored edges
- Time slider (1882-1920) to watch network grow
- Filter by railway company
- Network statistics panel (edges, density, connected/isolated nodes)
- Top hubs ranking by connectivity
- Play animation to watch network evolve

**Network Statistics (by 1920):**
| Metric | Value |
|--------|-------|
| Total Nodes | 429 settlements |
| Railway-Connected Edges | 1,121 |
| Connected Settlements | ~420 |
| Isolated Settlements | ~8 |

**Color Scheme:**
- CPR: Red (#e94560)
- QLSRSC: Green (#4ecca3)
- CNoR: Yellow (#ffd93d)
- GTPR: Purple (#6c5ce7)
- Other/No railway: Gray (#888)

## Project Structure

```
Sask_Railway_Visualizations/
├── index.html                 # Home page with navigation cards
├── one_hour_map.html          # Saskatoon corridor visualization
├── settlement_explorer.html   # Settlement explorer visualization
├── railway_timeline.html      # Railway network timeline
├── network_graph.html         # Network graph visualization
├── data/
│   ├── settlements.json              # 429 settlements with coordinates & railway info
│   ├── settlement_connections.json   # Pre-calculated connections with railway distances
│   ├── one_hour_corridor.json        # Saskatoon-specific corridor data
│   ├── railway_timeline.json         # Settlements by railway with years
│   ├── railway_network.json          # Track network graph (424 nodes, 509 edges)
│   └── settlement_network_mapping.json # Settlement to network node mappings
├── scripts/
│   ├── generate_connections.py       # Script to generate connection data
│   ├── update_multi_railways.py      # Cross-reference multi-railway data
│   ├── create_data_issues_doc.py     # Generate Word doc for data consultation
│   ├── build_railway_network.py      # Build network graph from GIS shapefile
│   ├── snap_settlements_to_network.py # Map settlements to network nodes
│   └── calculate_railway_distances.py # Calculate railway distances via Dijkstra
├── Historical_Railway_Data_By_Settlement.xlsx  # GIS comparison data
├── Saskatchewan_Railway_Data_Issues.docx       # Data issues for consultation
├── KNOWN_ISSUES.md            # Outstanding issues and testing checklist
└── README.md
```

## Data Files

| File | Records | Description |
|------|---------|-------------|
| `settlements.json` | 429 | All settlements with lat/lon, railway arrival year, first railway |
| `settlement_connections.json` | 429 + 1,811 pairs | Settlement data plus connections with direct & railway distances |
| `one_hour_corridor.json` | 12 | Settlements within 40 km of Saskatoon |
| `railway_timeline.json` | 392 | Settlements organized by railway company |
| `railway_network.json` | 424 nodes, 509 edges | Track network graph from GIS data |
| `settlement_network_mapping.json` | 429 | Settlement to network node mappings |

### Settlement Connections Data Structure

The `settlement_connections.json` file contains:

```json
{
  "settlements": {
    "Saskatoon": {
      "lat": 52.12,
      "lon": -106.67,
      "railway_arrives": 1889,
      "first_railway": "QLSRSC",
      "railways": [{"railway": "QLSRSC", "year": 1889}]
    }
  },
  "connections": {
    "Saskatoon": [
      {
        "to": "Osler",
        "distance_km": 28.7,
        "railway_distance_km": 132.8,
        "shared_railway": "QLSRSC",
        "connected_year": 1889,
        "all_shared_railways": null
      }
    ]
  }
}
```

The `railway_distance_km` field shows actual track distance (may be longer than direct distance due to route geometry).

## Scripts

### generate_connections.py

Generates the `settlement_connections.json` file from source data.

**Usage:**
```bash
python3 scripts/generate_connections.py
```

**Input files:**
- `data/settlements.json` - Settlement coordinates and railway info
- `data/railway_timeline.json` - Railway arrival years by settlement
- `../KnowledgeGraph/one_hour_railway_connections_complete.csv` - Pre-calculated distance pairs

**Output:**
- `data/settlement_connections.json` - Combined connection data

### update_multi_railways.py

Cross-references railway data from the UrbanSaskHist spreadsheet with `railway_timeline.json` to identify settlements served by multiple railways.

**Usage:**
```bash
python3 scripts/update_multi_railways.py
```

**Input files:**
- `../KnowledgeGraph/UrbanSaskHist_Update_Jan_2026.xlsx` - Spreadsheet with Railway_lines column
- `data/railway_timeline.json` - Existing railway timeline data

**Output:**
- Updates `data/railway_timeline.json` with multi-railway entries

**Statistics (current data):**
- Total settlements: 429
- Connection pairs within 40km: 1,811
- Railway-connected pairs: 1,691
- Settlements with nearby connections: 391
- Settlements with multiple railways: 8

### Railway Distance Scripts

Three scripts process GIS track data to calculate actual railway distances:

**1. build_railway_network.py**
Builds a network graph from the Historical Railways of Canada shapefile.

```bash
python3 scripts/build_railway_network.py
```

- Loads Saskatchewan track segments from HR_rails_NEW.shp
- Detects junction points where multiple tracks meet
- Splits tracks at junctions for accurate routing
- Output: `data/railway_network.json` (424 nodes, 509 edges)

**2. snap_settlements_to_network.py**
Maps each settlement to the nearest point on the railway network.

```bash
python3 scripts/snap_settlements_to_network.py
```

- Finds nearest network node or edge for each settlement
- 88.6% of settlements are within 5km of the network
- Output: `data/settlement_network_mapping.json`

**3. calculate_railway_distances.py**
Calculates shortest path railway distances between connected settlements.

```bash
python3 scripts/calculate_railway_distances.py
```

- Uses Dijkstra's algorithm for shortest path routing
- Handles same-edge cases using edge interpolation
- Updates `data/settlement_connections.json` with `railway_distance_km`

## Methodology

### Distance Calculation

**Direct Distance (Haversine):**
- Great-circle distance between settlement coordinates
- 40 km threshold = approximately 1 hour travel at 40 km/h average speed

**Railway Distance:**
- Actual track distance calculated from GIS shapefile geometries
- Built from Historical Railways of Canada dataset (HR_rails_NEW.shp)
- Uses Dijkstra's shortest path algorithm on network graph
- Average railway/direct distance ratio: 2.58x (some routes are indirect)

Both distances are displayed in Settlement Explorer and Saskatoon Corridor visualizations.

### Connection Logic
A settlement pair is considered "railway connected" when:
1. Distance between them is ≤ 40 km
2. Both settlements share the same railway line
3. `connected_year` = max(railway_arrives_settlement_1, railway_arrives_settlement_2)

### Saskatoon Railway Connections
| Railway | Year | Notes |
|---------|------|-------|
| QLSRSC | 1889 | First railway to Saskatoon |
| CPR | 1896 | Took over QLSRSC line |
| CNoR | 1905 | Canadian Northern expansion |
| GTPR | 1908 | Grand Trunk Pacific main line |

## Railway Absorption History

The QLSRSC line (Regina-Saskatoon-Prince Albert) changed hands multiple times:
1. **1889-1890**: QLSRSC builds the line
2. **1896-1906**: CPR leases/operates the line
3. **1906+**: CNoR takes over from CPR
4. **1918-1923**: CN absorbs CNoR

This explains why the same settlements appear on different railway company maps at different times.

## Running Locally

Due to browser security restrictions, you need to serve the files via HTTP:

```bash
# Navigate to project directory
cd Sask_Railway_Visualizations

# Start a local server
python3 -m http.server 8080

# Open in browser
open http://localhost:8080
```

## Data Sources

- **UrbanSaskHist - Final.xlsx**: Master settlement data with railway arrival dates
- **UrbanSaskHist_Update_Jan_2026.xlsx**: Updated spreadsheet with Railway_lines column for multi-railway data (cleaned January 2026)
- **Historical GIS Railway Data (doi-10.5683-sp2-uccfvq)**: Canadian Historical GIS Partnership railway network data, used to cross-reference and correct arrival dates
- **Historical_Railway_Data_By_Settlement.xlsx**: Comparison spreadsheet showing GIS vs. original data with discrepancies
- **settlement_coordinates.csv**: Geographic coordinates from 1921 census boundaries
- **one_hour_railway_connections_complete.csv**: Pre-calculated settlement pairs within 40km
- **CPR_map_1941_with_original_names.pdf**: CPR system map showing absorbed railways
- **CNoR_Map_1906.pdf**: Canadian Northern Railway system map

## Technical Details

Built with:
- [Leaflet.js](https://leafletjs.com/) for interactive maps
- [CARTO Dark Matter](https://carto.com/basemaps/) basemap tiles
- Vanilla JavaScript (no frameworks)
- Python 3 for data processing
- GitHub Pages for hosting

## Related Projects

This visualization is part of the larger Saskatchewan Knowledge Graph project examining historical urban settlements.

## Author

Jessica Jack, University of Saskatchewan

## License

This project is for academic research purposes.

---

*Created January 2026*
*Last updated: January 23, 2026*
