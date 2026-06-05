# World Cup Rosters Interactive Dashboard

An interactive data visualization dashboard displaying FIFA World Cup rosters from 1998-2026, enriched with player market valuations. Built with Python for data collection and D3.js for interactive visualizations.

![Dashboard Screenshot](https://via.placeholder.com/1400x900/1a1a1a/ffffff?text=Dashboard+Screenshot+Coming+Soon)

> **Note**: Replace the placeholder above with an actual screenshot by uploading an image to the repository

## Project Overview

This project scrapes and visualizes comprehensive World Cup roster data including:
- Player demographics (age, caps, position, nationality)
- Club affiliations and league diversity
- Market valuations from Transfermarkt (historical data from tournament dates)
- Tournament results and finish positions
- Historical trends across 8 World Cup tournaments (1998-2026)

## Data Coverage

### Overall Statistics
- **Years**: 1998, 2002, 2006, 2010, 2014, 2018, 2022, 2026
- **Total Players**: 6,462
- **Transfermarkt ID Coverage**: 98.76% (6,382/6,462)
- **Market Value Coverage**: 75.77% (4,896/6,462)

### By Tournament
| Year | Players | ID Coverage | Market Value Coverage |
|------|---------|-------------|----------------------|
| 1998 | 705 | 98.30% | 0.00% |
| 2002 | 736 | 97.42% | 0.00% |
| 2006 | 736 | 98.10% | 91.44% |
| 2010 | 736 | 98.23% | 97.28% |
| 2014 | 736 | 98.64% | 97.96% |
| 2018 | 736 | 98.91% | 98.10% |
| 2022 | 831 | 99.52% | 99.52% |
| 2026 | 1,246 | 100.00% | 99.28% |

*Market value coverage is limited by historical data availability on Transfermarkt. 1998 and 2002 have no market value data available for the tournament dates. Coverage improves significantly from 2006 onwards.*

## Quick Start

### Prerequisites
- Python 3.11+
- Git
- Modern web browser
- uv (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/world-cup-rosters-charts.git
cd world-cup-rosters-charts
```

2. **Set up Python environment with uv**
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# Install Playwright browsers (required for scraping)
playwright install chromium
```

3. **View the dashboard** (data already included)
```bash
cd dashboard
uv run python serve.py
# Open http://localhost:8002 in your browser
```

## Interactive Dashboard

The dashboard features a D3.js-powered scatter plot visualization with the following capabilities:

### Features
- **Country Flag Visualization**: Each country is represented by its flag, positioned across all tournament years
- **Multiple Metrics**: Switch between different metrics using the dropdown:
  - Average Caps (default)
  - Average Age
  - Home League Percentage
  - Total Market Value
  - Relative Market Value (z-score normalized)
- **Interactive Elements**:
  - **Hover**: Tooltip shows country, year, and metric value; flags enlarge across all years
  - **Click**: Displays detailed country statistics in the sidebar panel
  - **Zoom & Pan**: Navigate the visualization with mouse controls
- **Country Details Panel**: Shows comprehensive statistics for selected country:
  - Year-by-year breakdown
  - Player count, average caps, average age
  - Home league percentage
  - Total and average market values
  - Relative market value (z-score)
  - Tournament finish position (🏆 for winners, 2nd/3rd/4th, QF, R16, GRP)
- **Tournament Logos**: Visual timeline with official World Cup logos (1998-2026)
- **Metric Descriptions**: Contextual information about each metric

### Data Accuracy
- All market values are fetched from dates **before or on** the World Cup start date
- Home league percentages calculated using comprehensive 71-association mapping
- Tournament results included for all years 1998-2022 (2026 marked as TBD)

## Data Collection Workflow

The project includes a streamlined data collection pipeline. See [WORKFLOW.md](WORKFLOW.md) for complete step-by-step instructions.

### Core Scripts (6 total)

Located in `src/scrapers/`:

1. **`wikipedia_scraper.py`** - Scrape World Cup rosters from Wikipedia
2. **`transfermarkt_api_scraper.py`** - Fetch market values via Transfermarkt API
3. **`fix_korean_ids.py`** - Verify and correct player IDs using national team rosters
4. **`identify_wrong_ids.py`** - Identify players with potentially wrong IDs (read-only)
5. **`utils.py`** - Shared utilities for name normalization and matching
6. **`__init__.py`** - Package initialization

### Quick Data Update

```bash
# Update rosters for a specific year
uv run python -m src.scrapers.wikipedia_scraper --year 2026

# Fetch market values for new players
uv run python -m src.scrapers.transfermarkt_api_scraper

# Verify and fix any wrong IDs
uv run python -m src.scrapers.fix_korean_ids --verify --year 2026
```

## Project Structure

```
world-cup-rosters-charts/
├── data/                       # Data storage
│   ├── raw/                    # Raw scraped rosters (by year)
│   │   └── rosters/            # YYYY_rosters.csv files
│   ├── processed/              # Cleaned and merged datasets
│   │   ├── rosters_with_market_values.csv  # Main dataset
│   │   ├── player_ids.csv      # Transfermarkt ID mappings
│   │   └── tournament_results.csv  # Tournament finish positions
│   └── cache/                  # Scraping cache
├── src/                        # Python source code
│   ├── scrapers/               # 6 core scraping scripts
│   └── processing/             # Data processing utilities
├── dashboard/                  # D3.js interactive visualization
│   ├── dashboard.js            # Main visualization logic
│   ├── index.html              # Dashboard HTML
│   ├── data/                   # Dashboard data files
│   ├── logos/                  # World Cup tournament logos
│   └── serve.py                # Local development server
├── notebooks/                  # Jupyter notebooks for EDA
│   └── 01_exploratory_analysis.ipynb
├── WORKFLOW.md                 # Complete data pipeline guide
├── CURRENT_STATE.md            # Project status and metrics
├── DEPLOYMENT.md               # GitHub Pages deployment guide
└── README.md                   # This file
```

**Note**: The `archive/` directory contains 49 archived scripts (tests, one-off fixes, deprecated versions) that are excluded from version control but available locally for reference.

## Documentation

- **[WORKFLOW.md](WORKFLOW.md)** - Complete data collection workflow with step-by-step instructions
- **[CURRENT_STATE.md](CURRENT_STATE.md)** - Current project status, metrics, and data quality
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - GitHub Pages deployment instructions
- **[PROJECT_PLAN.md](PROJECT_PLAN.md)** - Original project plan and requirements
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and data flow
- **[METHODOLOGY.md](METHODOLOGY.md)** - Detailed scraping methodology
- **[VISUALIZATIONS.md](VISUALIZATIONS.md)** - Visualization specifications and design

## Development

### Running Jupyter Notebooks
```bash
uv run jupyter lab notebooks/
```

### Code Formatting
```bash
uv run black src/
uv run ruff check src/
```

### Data Quality Checks
```bash
# Identify players with potentially wrong IDs
uv run python -m src.scrapers.identify_wrong_ids

# Verify IDs against national team rosters
uv run python -m src.scrapers.fix_korean_ids --verify --year 2026
```

## Data Sources

- **Roster Data**: [Wikipedia World Cup Squad Pages](https://en.wikipedia.org/wiki/FIFA_World_Cup_squads)
- **Market Values**: [Transfermarkt API](https://www.transfermarkt.com)
- **Tournament Results**: Compiled from official FIFA records

## Known Limitations

1. **Market Value Coverage**: 1998 and 2002 have no market value data available on Transfermarkt for those tournament dates
2. **Historical Data**: Older tournaments have lower ID coverage due to player database limitations
3. **Data Freshness**: 2026 rosters will need updates as final squads are announced closer to the tournament
4. **Valuation Accuracy**: Market values are estimates from Transfermarkt and should not be considered official

## Deployment

The dashboard can be deployed to GitHub Pages. See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

Quick deployment:
```bash
# Enable GitHub Pages in repository settings
# Set source to: Deploy from a branch
# Select branch: main
# Select folder: /dashboard
```

## Contributing

Contributions are welcome! Areas for contribution include:
- Additional data sources (injuries, performance stats, player positions)
- New visualization types (heatmaps, network graphs, etc.)
- Performance optimizations
- Mobile-responsive design improvements
- Bug fixes and documentation enhancements

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Disclaimer

This project is for educational and research purposes. All data is publicly available and properly attributed to original sources. Market values are estimates from Transfermarkt and should not be considered official valuations.

---

**Last Updated**: June 2024 | **Status**: Production Ready | **Dashboard**: Fully Functional
