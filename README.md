# World Cup Rosters Interactive Dashboard

An interactive data visualization dashboard displaying FIFA World Cup rosters from 1998-2026, enriched with player market valuations. Built with Python for data collection and D3.js for stunning visualizations.

## Project Overview

This project scrapes and visualizes comprehensive World Cup roster data including:
- Player demographics (age, position, nationality)
- Club affiliations and international diversity
- Market valuations from Transfermarkt
- Historical trends across 8 World Cup tournaments

## Data Coverage

- **Years**: 1998, 2002, 2006, 2010, 2014, 2018, 2022, 2026*
- **Countries**: All participating nations (~32 per tournament)
- **Players**: ~5,888 total players across all tournaments
- **Data Points**: Name, DOB, Age, Position, Caps, Club, Market Value

*2026 data will be updated as rosters are announced

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ (for dashboard development)
- Git

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
```

3. **Run data collection**
```bash
# Scrape Wikipedia rosters
python -m src.scrapers.wikipedia_scraper

# Scrape Transfermarkt market values
python -m src.scrapers.transfermarkt_scraper

# Process and merge data
python -m src.processing.data_merger
```

4. **Launch dashboard**
```bash
cd dashboard
python -m http.server 8000
# Open http://localhost:8000 in your browser
```

## Project Structure

```
world-cup-rosters-charts/
├── data/                       # Data storage
│   ├── raw/                    # Raw scraped data
│   ├── processed/              # Cleaned datasets
│   └── cache/                  # Scraping cache
├── src/                        # Python source code
│   ├── scrapers/               # Web scraping modules
│   ├── processing/             # Data processing
│   └── validation/             # Data quality checks
├── notebooks/                  # Jupyter notebooks
├── dashboard/                  # D3.js visualization
│   ├── js/                     # JavaScript modules
│   ├── css/                    # Stylesheets
│   └── data/                   # Dashboard data files
├── tests/                      # Test suite
└── docs/                       # Documentation
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black src/
ruff check src/
```

### Jupyter Notebooks
```bash
jupyter lab notebooks/
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

- [PROJECT_PLAN.md](PROJECT_PLAN.md) - Comprehensive project plan
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture and data flow
- [METHODOLOGY.md](METHODOLOGY.md) - Detailed scraping methodology
- [VISUALIZATIONS.md](VISUALIZATIONS.md) - Visualization specifications

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

### Areas for Contribution
- Additional data sources
- New visualizations
- Performance optimizations
- Bug fixes and improvements
- Documentation enhancements

## Data Sources

- **Roster Data**: [Wikipedia World Cup Squad Pages](https://en.wikipedia.org/wiki/FIFA_World_Cup_squads)
- **Market Values**: [Transfermarkt](https://www.transfermarkt.com)

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
- [ ] Wikipedia scraping implementation
- [ ] Transfermarkt scraping implementation
- [ ] Data processing pipeline
- [ ] Exploratory data analysis
- [ ] D3.js dashboard development
- [ ] Deployment setup
- [ ] 2026 World Cup data updates (as rosters announced)
- [ ] Additional data sources (injuries, performance stats)
- [ ] Mobile-responsive design
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

