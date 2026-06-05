# World Cup Rosters Project - Current State

**Last Updated:** June 4, 2026

## Dataset Status

### Final Statistics
- **Total Players:** 6,462 across 8 World Cups (1998-2026)
- **Transfermarkt IDs:** 6,382 (98.76%)
- **Market Values:** 4,896 (75.77%)

### By Year

| Year | Players | IDs      | ID %   | Market Values | MV %   |
|------|---------|----------|--------|---------------|--------|
| 1998 | 705     | 693      | 98.3%  | 0             | 0.0%   |
| 2002 | 736     | 717      | 97.4%  | 0             | 0.0%   |
| 2006 | 736     | 722      | 98.1%  | 673           | 91.4%  |
| 2010 | 736     | 723      | 98.2%  | 716           | 97.3%  |
| 2014 | 736     | 726      | 98.6%  | 721           | 98.0%  |
| 2018 | 736     | 728      | 98.9%  | 722           | 98.1%  |
| 2022 | 831     | 827      | 99.5%  | 827           | 99.5%  |
| 2026 | 1,246   | 1,246    | 100.0% | 1,237         | 99.3%  |

### 2026 World Cup - Special Achievement
- ✓✓ **100% Transfermarkt ID coverage** (only year with perfect ID coverage)
- ✓✓ **99.3% market value coverage** (1,237/1,246)
- 9 players missing market values (legitimately have no valuation history)

## Project Structure (After Cleanup)

### Core Scripts (6 files in `src/scrapers/`)
1. `wikipedia_scraper.py` - Scrape World Cup rosters from Wikipedia
2. `transfermarkt_api_scraper.py` - Fetch market values via Transfermarkt API
3. `fix_korean_ids.py` - Verify/correct IDs using national team rosters
4. `identify_wrong_ids.py` - Identify players with wrong IDs (read-only)
5. `utils.py` - Shared utility functions
6. `__init__.py` - Package initialization

### Archived Scripts (49 files moved to `archive/`)
- `archive/tests/` - 9 test scripts
- `archive/fixes/` - 32 one-off fix scripts
- `archive/deprecated/` - 8 deprecated versions

### Data Files
- `data/processed/rosters_with_market_values.csv` - Primary dataset
- `data/processed/player_ids.csv` - Transfermarkt ID mappings
- `data/raw/market_values_raw.json` - Raw market value history
- `dashboard/data/processed/rosters_with_market_values.csv` - Dashboard copy (updated)

### Documentation
- `WORKFLOW.md` - Complete data pipeline workflow
- `CURRENT_STATE.md` - This file
- `PROJECT_PLAN.md` - Original project plan
- `METHODOLOGY.md` - Data collection methodology
- `README.md` - Project overview
- `cleanup_project.sh` - Cleanup script used

## Data Quality

### 2026 Players Missing Market Values (9)
These players have correct IDs but no market value history in Transfermarkt:

1. Mohamed Manai (Qatar) - ID: 432210 - Al-Shamal
2. Miloš Degenek (Australia) - ID: 181853 - APOEL
3. Ángelo Preciado (Ecuador) - ID: 339301 - Atlético Mineiro
4. Tommy Smith (New Zealand) - ID: 176056 - Braintree Town
5. Roberto Lopes (Cape Verde) - ID: 229681 - Shamrock Rovers
6. João Paulo (Cape Verde) - ID: 33318 - FCSB
7. Yacine Titraoui (Algeria) - ID: 1043534 - Charleroi
8. Azizbek Amonov (Uzbekistan) - ID: 1043535 - Dinamo Samarqand
9. Alberto Quintero (Panama) - ID: 96172 - Plaza Amador

### Historical Years
- **1998-2002:** No market values available (Transfermarkt didn't track values that far back)
- **2006-2022:** Some players missing values due to lower-tier leagues or retired before tracking began

## Recent Work (June 2026)

### 2026 Roster Update
- Re-scraped all 2026 rosters after finalization (June 1, 2026)
- Corrected Mexico roster (was 51 players, now 26)
- Recovered 1,194 IDs from git history using merge strategy
- Fixed 23 Korean player IDs using name reversal logic

### ID Corrections (6 players)
1. Lawrence Ati-Zigi (Ghana): 294680 → 254285 (€1.5M)
2. Benjamin Asare (Ghana): 263160 → 837368 (€100K)
3. José Sá (Portugal): 137457 → 249994 (€3.5M)
4. Cho Wi-je (South Korea): 1007088 → 550978 (€550K)
5. Yasser Ibrahim (Egypt): 106256 → 237425 (€275K)
6. José Luis Rodríguez (Panama): 253946 → 425028 (€2.5M)

### Project Cleanup
- Reduced from 57 scripts to 6 core scripts
- Archived 49 one-off/test scripts
- Created comprehensive workflow documentation
- Updated dashboard with latest data

## Dashboard

### Location
- `dashboard/index.html` - Main interactive visualization
- `dashboard/data/processed/` - Data files (updated June 4, 2026)
- `dashboard/js/` - D3.js visualization code

### Features
- Interactive timeline of World Cup years
- Country selection and filtering
- Player market value distributions
- Age and position analysis
- Club country diversity metrics

## How to Replicate

See [`WORKFLOW.md`](WORKFLOW.md) for complete step-by-step instructions to rebuild the dataset from scratch.

Quick start:
```bash
# 1. Scrape rosters
uv run python src/scrapers/wikipedia_scraper.py

# 2. Search for player IDs
# (see WORKFLOW.md Step 2)

# 3. Verify IDs
uv run python src/scrapers/fix_korean_ids.py --verify --all

# 4. Fetch market values
uv run python src/scrapers/transfermarkt_api_scraper.py

# 5. Update dashboard
cp data/processed/rosters_with_market_values.csv dashboard/data/processed/
```

## Next Steps

1. ✅ Update dashboard data (COMPLETED)
2. ✅ Clean up scraper scripts (COMPLETED - 57 → 6 files)
3. ✅ Document workflow (COMPLETED - WORKFLOW.md)
4. ⏳ Set up deployment (GitHub Pages/Vercel)
5. ⏳ Update main README.md with new structure