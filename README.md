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
- Searchable dropdown with all 429 settlements (type to filter or click arrow to browse full list, with railway hints)
- All settlements visible on map (click any to explore)
- 40 km radius circle showing potential connections
- Connection lines drawn between railway-connected settlements using actual track routes
- Connections filtered by actual railway distance (40 km / 1 hour at 40 km/h), not just direct distance
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
1. Both are within 40 km direct distance of each other
2. Both share the same railway line
3. Both have received that railway by the selected year
4. The actual railway distance between them is ≤ 40 km (one hour at 40 km/h)

Note: Some settlements are close as the crow flies but far apart by rail (e.g., on different branch lines). These are excluded because they are not reachable within one hour by train.

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
| CPR | Rust (#c75d38) | 1882+ | Canadian Pacific - First transcontinental through southern SK |
| QLSRSC | Green (#0b6a41) | 1889-90 | Qu'Appelle, Long Lake & Saskatchewan - Regina to Prince Albert via Saskatoon |
| CNoR | Gold (#f1c730) | 1899+ | Canadian Northern - Northerly competitor through Saskatoon |
| GTPR | Purple (#6c5ce7) | 1905+ | Grand Trunk Pacific - Third transcontinental via Saskatoon |

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
- CPR: Rust (#c75d38)
- QLSRSC: Green (#0b6a41)
- CNoR: Gold (#f1c730)
- GTPR: Purple (#6c5ce7)
- Other/No railway: Gray (#888)

### 5. Journey Times (Network Routing)

Compare walking, horse & cart, and railway travel times between any origin settlement and all other settlements. Railway times use actual track routes calculated via Dijkstra's algorithm.

**Features:**
- Select any settlement as origin
- Year slider (1882-1920) shows how railway connections expanded
- Three transport modes compared side by side with animated bars
- Railway transfer tracking (shows which railways are used on each route)
- Sort destinations by distance, name, or railway time
- Play animation to watch network evolve year by year
- Statistics panel with averages for all modes

**Transport Modes:**
| Mode | Speed | Method |
|------|-------|--------|
| Walking | 5 km/h | Straight-line (haversine) distance |
| Horse & Cart | 10 km/h | Straight-line (haversine) distance |
| Railway | 40 km/h | Actual track route via Dijkstra's algorithm |

**Visual Elements:**
- **Red bars**: Walking time
- **Orange bars**: Horse & cart time
- **Green bars**: Railway time
- **Gold text**: Railway transfers (e.g., CPR → CNoR)
- Color-coded rows by distance (green=near, yellow=mid, red=far)
- Time savings column shows how much faster rail is vs walking

### 6. Travelling Time Simulation

Watch animated tokens race between two settlements to see how railways transformed travel. A walker, horse & cart, and train travel simultaneously along their routes on an interactive map.

**Features:**
- Animated race with three tokens (walker, horse & cart, train)
- Railway follows actual track geometry on the map
- Adjustable animation speed (1x, 2x, 5x, 10x, 20x)
- Progress bars and elapsed time for each mode
- Click map markers to select origin/destination
- Swap button to reverse route
- Railway advantage comparison (e.g., "8.4x faster than walking")

**Transport Modes:**
| Mode | Speed | Route |
|------|-------|-------|
| Walking | 5 km/h | Straight line |
| Horse & Cart | 10 km/h | Straight line |
| Railway | 40 km/h | Actual track geometry |

**Data Sources:**
- `settlement_connections.json` - Settlement locations and railway years
- `railway_tracks.json` - Track geometry with coordinates
- `railway_network.json` - Network graph with edges
- `settlement_network_mapping.json` - Settlement to network node mappings

### 7. Travel Time Comparison (Isochrone)

Compare how far you could travel by walking, wagon, or railway in the same amount of time. This visualization demonstrates how railways dramatically expanded the reachable world for Saskatchewan settlers.

**Features:**
- Select any settlement as the center point
- Choose travel time: 30 min, 1 hour, 2 hours, 4 hours, or 8 hours
- Toggle visibility of walking, wagon, and railway range circles
- Year slider (1882-1920) to see network expansion over time
- Full network pathfinding calculates actual railway distances to ALL settlements

**Transport Modes:**
| Mode | Speed | 1-Hour Range |
|------|-------|--------------|
| Walking | 5 km/h | 5 km |
| Horse & Wagon | 10 km/h | 10 km |
| Railway | 40 km/h | 40 km |

**Visual Elements:**
- **Gray circle (solid)**: Walking range
- **Gold circle (solid)**: Wagon range
- **Green circle (solid)**: Railway range (radius extends to furthest rail-connected settlement)
- **Green markers**: Settlements actually reachable by railway within time limit
- Markers color-coded by fastest mode of access

**Key Metrics:**
- Settlement counts by mode (walking, wagon, railway)
- Railway expansion factor (how many more settlements reachable by rail vs walking)

**Technical Implementation:**
- Uses Dijkstra's algorithm on the railway network graph
- Calculates shortest path railway distances from selected hub to all settlements
- Edge-snapped settlements: considers both edge endpoints and along-edge position (`snap_edge_t`) for accurate distance calculation
- Filters by year — only shows connections that existed by selected year
- Railway reachability based on actual track routes, not straight-line distance

### 8. Transport Eras

Scrub through four transport eras and watch settlements shift from geographic positions through walking, horse & cart, and railway time-distance layouts.

**Features:**
- Unified slider across all transport modes
- Smooth interpolation between eras
- Auto-play with stage pauses
- Railway connections colored by company

## Demo Visualizations (Experimental)

Five additional demo visualizations exploring the railway data from new analytical perspectives. These are distinct from the main visualizations in that they focus on statistical, comparative, and aggregate views rather than individual map-based exploration.

### Centrality Rankings Over Time (`demo_centrality.html`)

A D3.js bump chart showing how settlement importance shifts as railways arrive. Settlements are ranked by **degree centrality** (number of active railway connections) for each year from 1882 to 1920, with the top 15 displayed.

- Lines colored by first railway company (CPR/QLSRSC/CNoR/GTPR)
- Hover to highlight a settlement and see its rank history
- Play animation or use "Show All Years" toggle
- Info panel shows railway details for hovered settlement

### Railway Company Territory Map (`demo_territory.html`)

A Leaflet map with a Voronoi-style canvas overlay showing which railway company "serves" each area of Saskatchewan, based on the nearest railway settlement. Territory shading fades with distance (max 100 km).

- Year slider animates territory expansion from 1882 to 1920
- Statistics panel shows settlement counts and percentages per railway
- Visualizes competition and coverage gaps between companies

### Small Multiples: Network Growth (`demo_small_multiples.html`)

A filmstrip of 10 static Canvas maps (1882, 1886, 1890, 1895, 1900, 1905, 1908, 1910, 1915, 1920) displayed simultaneously in a 5x2 grid. No slider or animation required — the entire story is visible at a glance for side-by-side comparison.

- Settlements colored by railway company
- "Highlight new" toggle makes newly-added settlements glow
- Hover on a panel to enlarge it
- Summary bar shows settlement counts per year

### Connectivity Inequality Dashboard (`demo_inequality.html`)

A 2x2 grid of D3.js line charts showing aggregate network statistics over time:

1. **Railway Coverage** — % of 429 settlements connected
2. **Average Connections** — mean degree among connected settlements
3. **Connectivity Inequality (Gini)** — degree distribution inequality
4. **Network Density** — fraction of possible connections that exist

- Synchronized scrubber line follows mouse across all 4 charts
- Key railway events annotated (CPR 1882, QLSRSC 1889, CNoR 1899, GTPR 1905)
- Summary bar shows year-by-year statistics

### Settlement Accessibility Heatmap (`demo_heatmap.html`)

A Leaflet map with a rasterized canvas overlay showing the distance from any point in Saskatchewan to the nearest railway settlement. Reveals **coverage gaps and accessibility deserts** that settlement-focused maps don't emphasize.

- Color gradient from green (0 km) through yellow/orange to dark red (150+ km)
- Year slider shows coverage expanding from 1882 to 1920
- Stats panel: average distance, % within 25 km, % within 50 km
- Adjustable heatmap opacity

## Project Structure

```
Sask_Railway_Visualizations/
├── index.html                 # Home page with navigation cards
├── one_hour_map.html          # Saskatoon corridor visualization
├── settlement_explorer.html   # Settlement explorer visualization
├── railway_timeline.html      # Railway network timeline
├── network_graph.html         # Network graph visualization
├── journey_times.html         # Journey times comparison (network routing)
├── journey_times_simple.html  # Simpler journey times (earlier version)
├── travel_race.html           # Travelling time simulation (animated race)
├── isochrone.html             # Travel time comparison visualization
├── transport_eras.html        # Transport eras animation
├── demo_centrality.html      # Demo: Centrality rankings bump chart
├── demo_territory.html       # Demo: Railway company territory map
├── demo_small_multiples.html # Demo: Small multiples filmstrip
├── demo_inequality.html      # Demo: Connectivity inequality dashboard
├── demo_heatmap.html         # Demo: Settlement accessibility heatmap
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
| `railway_tracks.json` | - | Track geometry with node-to-node coordinates for map rendering |
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

## Visual Theme

All visualizations use University of Saskatchewan branding:

| Element | Color | Hex |
|---------|-------|-----|
| Page background | Black | `#000000` |
| Header/sidebar | Dark gray | `#1a1a1e` |
| Section backgrounds | Charcoal | `#252528` |
| Header border | USask Green | `#0b6a41` |
| Section headings | USask Gold | `#f1c730` |
| Buttons | USask Green | `#0b6a41` |
| Muted text | Gray | `#9A9B9D` |

Navigation uses a dropdown menu ("Other Visualizations") consistent across all pages.

## Technical Details

Built with:
- [Leaflet.js](https://leafletjs.com/) for interactive maps
- [D3.js](https://d3js.org/) for network graph visualization
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
*Last updated: February 6, 2026*

### Data Corrections (February 6, 2026)

- **Summerberry**: Changed `first_railway` from `"No information provided"` to `"CPR"` (1882) across `settlements.json`, `settlement_connections.json`, and `railway_timeline.json`. Also fixed 7 connection entries from `shared_railway: "Interchange"` to `"CPR"` (both directions), and corrected `railway_distance_km` values of 0.0 for Wolseley and Sintaluta connections
- **Lockwood**: Added null-safety checks across all demo visualizations to prevent settlements with `railway_arrives: null` from appearing erroneously (JavaScript `null <= 1882` evaluates to `true`)
- **Settlement Explorer**: Added railway distance filter (≤ 40 km) so only true one-hour rail connections are shown. Replaced browser datalist with custom searchable dropdown supporting keyboard navigation, clickable arrow to browse, and railway hints per settlement
