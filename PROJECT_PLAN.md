# World Cup Rosters Interactive Dashboard - Project Plan

## Project Overview
An interactive data visualization dashboard displaying FIFA World Cup rosters from 1998-2026, enriched with player market valuations from Transfermarkt. Built with Python for data scraping/processing and D3.js for interactive visualizations.

## Technology Stack

### Data Collection & Processing
- **Python 3.11+** with `uv` for package management
- **BeautifulSoup4** / **lxml** - Wikipedia scraping
- **Selenium** / **Playwright** - Transfermarkt scraping (dynamic content)
- **Pandas** - Data manipulation and cleaning
- **Jupyter Notebooks** - Exploratory data analysis

### Visualization & Frontend
- **D3.js** - Interactive data visualizations
- **HTML/CSS/JavaScript** - Dashboard interface
- **Vite** or **Parcel** - Build tooling (optional)

### Deployment
- **GitHub Pages** or **Vercel** - Recommended for static D3.js dashboards
- **GitHub Actions** - CI/CD for automated data updates

## Project Structure

```
world-cup-rosters-charts/
├── .venv/                          # Python virtual environment (uv)
├── data/
│   ├── raw/                        # Raw scraped data
│   │   ├── rosters/                # Wikipedia roster data by year
│   │   └── market_values/          # Transfermarkt data by year
│   ├── processed/                  # Cleaned and merged datasets
│   │   ├── rosters_combined.csv
│   │   └── rosters_with_values.csv
│   └── metadata/                   # Country codes, flags, etc.
├── notebooks/
│   ├── 01_scrape_wikipedia.ipynb   # Wikipedia scraping
│   ├── 02_scrape_transfermarkt.ipynb # Market value scraping
│   ├── 03_data_cleaning.ipynb      # Data processing
│   └── 04_exploratory_analysis.ipynb # EDA and insights
├── src/
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── wikipedia_scraper.py    # Wikipedia roster scraper
│   │   ├── transfermarkt_scraper.py # Market value scraper
│   │   └── utils.py                # Helper functions
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── data_cleaner.py         # Data cleaning logic
│   │   └── data_merger.py          # Merge rosters + values
│   └── validation/
│       ├── __init__.py
│       └── validators.py           # Data quality checks
├── dashboard/
│   ├── index.html                  # Main dashboard page
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   ├── main.js                 # Dashboard initialization
│   │   ├── visualizations/
│   │   │   ├── age-distribution.js
│   │   │   ├── market-value-trends.js
│   │   │   ├── club-country-map.js
│   │   │   └── roster-comparison.js
│   │   └── utils/
│   │       ├── data-loader.js
│   │       └── helpers.js
│   └── data/                       # Processed data for dashboard
│       └── rosters_with_values.json
├── tests/
│   ├── test_scrapers.py
│   └── test_processing.py
├── .gitignore
├── pyproject.toml                  # uv project configuration
├── README.md
├── METHODOLOGY.md                  # Detailed scraping methodology
└── PROJECT_PLAN.md                 # This file
```

## Data Schema

### Roster Data Fields
Each roster CSV will contain:
- `Country` - National team name
- `Number` - Jersey number
- `Position` - Player position (GK, DF, MF, FW)
- `Player` - Player full name
- `DOB` - Date of birth (YYYY-MM-DD)
- `Age` - Age at tournament start
- `Caps` - International caps at time of tournament
- `Club` - Club team name
- `Club_Country` - Country of club team
- `Home_Country_Flag` - Boolean (True if Club_Country matches Country)
- `Year` - World Cup year

### Market Value Data Fields
- `Player` - Player full name (for matching)
- `Country` - National team
- `Year` - World Cup year
- `Market_Value_EUR` - Market value in Euros
- `Market_Value_Date` - Date of valuation
- `Source_URL` - Transfermarkt URL

## Implementation Phases

### Phase 1: Environment Setup
1. Initialize Git repository
2. Set up Python virtual environment with `uv`
3. Install core dependencies
4. Create project structure
5. Set up `.gitignore` for Python and data files

### Phase 2: Wikipedia Scraping
1. Analyze Wikipedia squad page structure
2. Build robust HTML parser for roster tables
3. Handle variations across different years
4. Extract all required fields
5. Save raw data as CSV per year
6. Implement error handling and logging

**Key Challenges:**
- Table structure variations between years
- Player name formatting inconsistencies
- Missing data handling (caps, DOB)
- Club country extraction

### Phase 3: Data Cleaning & Processing
1. Standardize player names
2. Parse and validate dates
3. Calculate ages consistently
4. Standardize country names
5. Add country codes and flag indicators
6. Validate data completeness
7. Create combined dataset

### Phase 4: Transfermarkt Scraping
1. Research Transfermarkt URL patterns
2. Handle dynamic content loading
3. Match players between datasets
4. Extract market values at specific dates
5. Handle currency conversions
6. Implement rate limiting and respectful scraping

**Key Challenges:**
- Dynamic JavaScript content
- Player name matching between sources
- Historical market value data availability
- Rate limiting and anti-scraping measures

### Phase 5: Data Merging & Validation
1. Fuzzy matching for player names
2. Merge roster and market value data
3. Handle missing market values
4. Data quality validation
5. Generate summary statistics
6. Export final datasets (CSV and JSON)

### Phase 6: Exploratory Analysis
1. Age distribution analysis by year/position
2. Market value trends over time
3. Club country diversity analysis
4. Position-specific insights
5. Generate visualization recommendations

### Phase 7: D3.js Dashboard Development
1. Design dashboard layout and UX
2. Implement data loading utilities
3. Create core visualizations (based on user requirements)
4. Add interactivity and filters
5. Implement responsive design
6. Optimize performance

### Phase 8: Deployment & Documentation
1. Prepare static assets for deployment
2. Configure GitHub Pages or Vercel
3. Set up automated data updates (optional)
4. Write comprehensive README
5. Document scraping methodology
6. Add usage examples

## Recommended Visualizations

Based on the data structure, here are suggested visualizations:

### 1. **Age Distribution Heatmap**
- X-axis: World Cup years (1998-2026)
- Y-axis: Age ranges (18-20, 21-25, 26-30, 31-35, 36+)
- Color: Number of players
- Interactive: Filter by country, position

### 2. **Market Value Evolution**
- Line chart showing average/median market values over time
- Multiple lines for different positions
- Interactive: Select countries to compare

### 3. **Club Country Diversity Map**
- World map showing club countries for each national team
- Size: Number of players from each club country
- Interactive: Select year and country

### 4. **Position Distribution Sunburst**
- Inner ring: Countries
- Outer ring: Positions
- Size: Number of players or total market value

### 5. **Player Comparison Matrix**
- Scatter plot: Age vs Market Value
- Color: Position
- Size: Caps
- Interactive: Brush selection, tooltips

### 6. **Home vs Foreign Players**
- Stacked bar chart by country
- Show percentage of players in domestic vs foreign leagues
- Trend over years

### 7. **Top Clubs Contribution**
- Bar chart of clubs contributing most players
- Grouped by World Cup year
- Interactive: Filter by country

### 8. **Squad Value Rankings**
- Horizontal bar chart of total squad values
- Animated transitions between years
- Show top 10-15 countries

## Data Quality Considerations

### Validation Checks
- [ ] All required fields present
- [ ] Date formats consistent
- [ ] Age calculations accurate
- [ ] Country names standardized
- [ ] No duplicate players per roster
- [ ] Market values in reasonable ranges
- [ ] Club countries valid

### Data Completeness
- Track missing data percentages
- Document data availability by year
- Handle 2026 partial data appropriately

## Deployment Strategy

### Recommended: GitHub Pages + Vercel
- **GitHub Pages**: Host static dashboard
- **Vercel**: Alternative with better build tools
- **Advantages**: Free, automatic deployments, custom domains

### Deployment Steps
1. Build optimized dashboard assets
2. Configure deployment settings
3. Set up custom domain (optional)
4. Enable HTTPS
5. Configure caching headers

## Timeline Estimate

- **Phase 1-2**: 2-3 days (Setup + Wikipedia scraping)
- **Phase 3**: 1-2 days (Data cleaning)
- **Phase 4**: 2-3 days (Transfermarkt scraping - most complex)
- **Phase 5**: 1 day (Merging and validation)
- **Phase 6**: 1 day (EDA)
- **Phase 7**: 3-5 days (Dashboard development)
- **Phase 8**: 1 day (Deployment and docs)

**Total**: ~12-17 days of development time

## Next Steps

1. Review and approve this plan
2. Clarify specific visualization requirements
3. Begin Phase 1: Environment setup
4. Start Wikipedia scraping implementation

## Notes

- 2026 World Cup data will be partial until rosters are announced
- Transfermarkt scraping may require careful rate limiting
- Consider caching scraped data to avoid repeated requests
- Market value data availability may vary by player/year
- Plan for data updates as 2026 rosters are announced