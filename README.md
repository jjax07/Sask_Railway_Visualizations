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
| 1890 | 2 (Osler, Dundurn) |
| 1905 | 5 (added Warman, Langham, Aberdeen) |
| 1910 | 11 (major expansion with GTPR) |

### 2. Railway Network Timeline

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

## Data

The `data/` folder contains JSON files extracted from the Urban Saskatchewan History project:

| File | Description |
|------|-------------|
| `settlements.json` | All 429 settlements with coordinates, railway info, and distances from Saskatoon |
| `one_hour_corridor.json` | 12 settlements within 40 km of Saskatoon with connection timeline |
| `railway_timeline.json` | Settlements organized by railway company with arrival years |

## Methodology

### Distance Calculation
- Haversine formula for great-circle distance between settlement coordinates
- 40 km threshold = approximately 1 hour travel at 40 km/h average speed (typical for branch lines with stops)

### Connection Logic
A settlement is considered connected to Saskatoon by rail when:
1. Railway has arrived at that settlement
2. The railway line physically connects to Saskatoon
3. Saskatoon has that railway connection

### Saskatoon Railway Connections
| Railway | Year | Notes |
|---------|------|-------|
| QLSRSC | 1890 | First railway to Saskatoon |
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

## Data Sources

- **UrbanSaskHist - Final.xlsx**: Master settlement data with railway arrival dates
- **settlement_coordinates.csv**: Geographic coordinates from 1921 census boundaries
- **CPR_map_1941_with_original_names.pdf**: CPR system map showing absorbed railways
- **CNoR_Map_1906.pdf**: Canadian Northern Railway system map

## Technical Details

Built with:
- [Leaflet.js](https://leafletjs.com/) for interactive maps
- [CARTO Dark Matter](https://carto.com/basemaps/) basemap tiles
- Vanilla JavaScript (no frameworks)
- GitHub Pages for hosting

## Related Projects

This visualization is part of the larger Saskatchewan Knowledge Graph project examining historical urban settlements.

## Author

Jessica Jack, University of Saskatchewan

## License

This project is for academic research purposes.

---

*Created January 2026*
