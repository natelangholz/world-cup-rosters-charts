# World Cup Rosters Interactive Dashboard

An interactive data visualization dashboard displaying FIFA World Cup rosters from 1998-2026, enriched with player market valuations. Built with Python for data collection and D3.js for stunning visualizations.

## Project Overview

This project scrapes and visualizes comprehensive World Cup roster data including:
- Player demographics (age, position, nationality)
- Club affiliations and international diversity
- Market valuations from Transfermarkt
- Historical trends across 8 World Cup tournaments

## Data Coverage

### Overall Statistics
- **Years**: 1998, 2002, 2006, 2010, 2014, 2018, 2022, 2026
- **Total Players**: 6,462
- **Transfermarkt ID Coverage**: 98.76% (6,382/6,462)
- **Market Value Coverage**: 75.76% (4,895/6,462)

### By Tournament
| Year | Players | ID Coverage | Market Value Coverage |
|------|---------|-------------|----------------------|
| 1998 | 704 | 98.01% | 54.12% |
| 2002 | 736 | 98.37% | 60.60% |
| 2006 | 736 | 98.64% | 68.07% |
| 2010 | 736 | 98.64% | 75.68% |
| 2014 | 736 | 98.64% | 82.88% |
| 2018 | 736 | 98.64% | 88.18% |
| 2022 | 832 | 98.92% | 90.87% |
| 2026 | 1,246 | 100.00% | 99.28% |

*Market value coverage is limited by historical data availability on Transfermarkt. Recent tournaments have significantly better coverage.*

## Quick Start

### Prerequisites
- Python 3.11+
- Git
- Modern web browser

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
python serve.py
# Open http://localhost:8000 in your browser
```

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
python -m src.scrapers.wikipedia_scraper --year 2026

# Fetch market values for new players
python -m src.scrapers.transfermarkt_api_scraper

# Verify and fix any wrong IDs
python -m src.scrapers.fix_korean_ids --verify --year 2026
```

## Project Structure

```
world-cup-rosters-charts/
├── data/                       # Data storage
│   ├── raw/                    # Raw scraped rosters (by year)
│   ├── processed/              # Cleaned and merged datasets
│   │   ├── rosters_with_market_values.csv  # Main dataset
│   │   └── player_ids.csv      # Transfermarkt ID mappings
│   └── cache/                  # Scraping cache
├── src/                        # Python source code
│   ├── scrapers/               # 6 core scraping scripts
│   └── processing/             # Data processing utilities
├── archive/                    # Archived scripts
│   ├── tests/                  # Test scripts (9 files)
│   ├── fixes/                  # One-off fix scripts (32 files)
│   └── deprecated/             # Deprecated versions (8 files)
├── notebooks/                  # Jupyter notebooks for EDA
├── dashboard/                  # D3.js interactive visualization
│   ├── js/                     # JavaScript modules
│   ├── css/                    # Stylesheets
│   ├── data/                   # Dashboard data files
│   └── serve.py                # Local development server
├── docs/                       # Additional documentation
├── WORKFLOW.md                 # Complete data pipeline guide
└── CURRENT_STATE.md            # Project status and metrics
```

## Visualizations

The dashboard includes interactive visualizations for:

1. **Age Distribution Analysis** - Heatmaps showing age trends over time
2. **Market Value Evolution** - Line charts tracking valuation changes
3. **Club Country Diversity** - Geographic maps of player origins
4. **Position Analysis** - Sunburst charts of squad composition
5. **Squad Comparisons** - Interactive scatter plots and rankings
6. **Home vs Foreign Players** - Stacked bar charts of league diversity

See [VISUALIZATIONS.md](VISUALIZATIONS.md) for detailed descriptions.

## Documentation

- **[WORKFLOW.md](WORKFLOW.md)** - Complete data collection workflow
- **[CURRENT_STATE.md](CURRENT_STATE.md)** - Current project status and metrics
- **[PROJECT_PLAN.md](PROJECT_PLAN.md)** - Original project plan
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and data flow
- **[METHODOLOGY.md](METHODOLOGY.md)** - Detailed scraping methodology
- **[VISUALIZATIONS.md](VISUALIZATIONS.md)** - Visualization specifications

## Development

### Running Jupyter Notebooks
```bash
jupyter lab notebooks/
```

### Code Formatting
```bash
black src/
ruff check src/
```

### Data Quality Checks
```bash
# Identify players with potentially wrong IDs
python -m src.scrapers.identify_wrong_ids

# Verify IDs against national team rosters
python -m src.scrapers.fix_korean_ids --verify --year 2026
```

## Key Features

### Robust Data Collection
- **Playwright-based scraping** for reliable Wikipedia data extraction
- **Transfermarkt API integration** for market valuations
- **Fuzzy name matching** with Korean name handling
- **ID verification system** to ensure data accuracy

### High Data Quality
- 98.76% Transfermarkt ID coverage overall
- 100% ID coverage for 2026 World Cup
- Comprehensive error handling and logging
- Git-based data recovery capabilities

### Clean Architecture
- Streamlined to 6 core scripts (from 57)
- Archived test and one-off scripts for reference
- Clear separation of concerns
- Well-documented workflow

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

### Areas for Contribution
- Additional data sources (injuries, performance stats)
- New visualizations
- Performance optimizations
- Bug fixes and improvements
- Documentation enhancements

## Data Sources

- **Roster Data**: [Wikipedia World Cup Squad Pages](https://en.wikipedia.org/wiki/FIFA_World_Cup_squads)
- **Market Values**: [Transfermarkt](https://www.transfermarkt.com)

## Known Limitations

1. **Market Value Coverage**: Historical data (1998-2010) has lower coverage due to Transfermarkt's data availability
2. **Missing Valuations**: 9 players in 2026 have no market value history on Transfermarkt
3. **Data Freshness**: 2026 rosters will need updates as final squads are announced

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Wikipedia for comprehensive roster data
- Transfermarkt for market valuation data
- D3.js community for visualization tools
- FIFA for World Cup data

## Contact

For questions or feedback, please open an issue on GitHub.

## Roadmap

- [x] Project planning and architecture
- [x] Wikipedia scraping implementation
- [x] Transfermarkt scraping implementation
- [x] Data processing pipeline
- [x] Exploratory data analysis
- [x] D3.js dashboard development
- [x] Project cleanup and documentation
- [ ] Deployment setup (GitHub Pages/Vercel)
- [ ] 2026 World Cup final roster updates
- [ ] Additional data sources (injuries, performance stats)
- [ ] Mobile-responsive design improvements
- [ ] API endpoint for data access

## Citation

If you use this data or visualizations in your research, please cite:

```bibtex
@misc{worldcuprosters2024,
  title={World Cup Rosters Interactive Dashboard},
  author={Your Name},
  year={2024},
  publisher={GitHub},
  url={https://github.com/yourusername/world-cup-rosters-charts}
}
```

## Disclaimer

This project is for educational and research purposes. All data is publicly available and properly attributed to original sources. Market values are estimates from Transfermarkt and should not be considered official valuations.

---

**Last Updated**: June 2024 | **Status**: Production Ready
