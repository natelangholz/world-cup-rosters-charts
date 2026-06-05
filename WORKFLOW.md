# World Cup Rosters Data Pipeline Workflow

## Overview

This document describes the complete data pipeline for building the World Cup rosters dataset from scratch.

## Prerequisites

```bash
# Install dependencies
uv sync

# Install Playwright browsers (for ID verification)
uv run playwright install chromium
```

## Complete Workflow

### Step 1: Scrape Wikipedia Rosters

Scrape World Cup squad lists from Wikipedia for all years (1998-2026).

```bash
uv run python src/scrapers/wikipedia_scraper.py
```

**Output:** `data/processed/rosters_combined.csv`

**What it does:**
- Scrapes roster tables from Wikipedia pages like `https://en.wikipedia.org/wiki/2022_FIFA_World_Cup_squads`
- Extracts: Country, Number, Position, Player, DOB, Age, Caps, Club, Club_Country
- Adds Home_Country_Flag column (True if Club_Country matches Country)
- Combines all years into single CSV

### Step 2: Search for Transfermarkt Player IDs

Search Transfermarkt API to find player IDs for all players.

```bash
uv run python -c "
from src.scrapers.transfermarkt_api_scraper import search_player_ids
search_player_ids(
    'data/processed/rosters_combined.csv',
    'data/processed/player_ids.json'
)
"
```

**Output:** `data/processed/player_ids.json`

**What it does:**
- Uses Transfermarkt search API: `https://tmapi-alpha.transfermarkt.technology/search`
- Searches by player name and matches by DOB
- Stores player_id, name, birth_date, nationality, match_type, url

### Step 3: Verify and Correct IDs

Verify IDs by checking against national team rosters on Transfermarkt.

```bash
# Verify all players with IDs but no market values
uv run python src/scrapers/fix_korean_ids.py --verify --all

# Or verify specific year
uv run python src/scrapers/fix_korean_ids.py --verify --year 2026

# Or verify specific country
uv run python src/scrapers/fix_korean_ids.py --verify --country "South Korea"
```

**What it does:**
- Scrapes national team roster pages using Playwright
- Uses fuzzy name matching (threshold: 0.60) with Korean name reversal logic
- Corrects wrong IDs by matching against official rosters
- Updates `rosters_with_market_values.csv` with corrected IDs

### Step 4: Fetch Market Values

Fetch historical market values from Transfermarkt API.

```bash
uv run python src/scrapers/transfermarkt_api_scraper.py
```

**Output:** 
- `data/raw/market_values_raw.json` - Raw market value history
- `data/processed/rosters_with_market_values.csv` - Final dataset

**What it does:**
- Fetches market value history: `https://tmapi-alpha.transfermarkt.technology/player/{id}/market-value-history`
- Finds closest market value to World Cup start date
- Adds columns: Market_Value_EUR, Market_Value_Date, Market_Value_Age

### Step 5: Identify Remaining Issues

Check for players with IDs but no market values (potential wrong IDs).

```bash
uv run python src/scrapers/identify_wrong_ids.py
```

**Output:** `data/cache/id_corrections_proposed.csv`

**What it does:**
- Tests each ID to see if it has market value data
- Searches for alternative IDs if current one has no data
- Generates report of proposed corrections (does NOT modify dataset)

## Core Scripts

### `wikipedia_scraper.py`
- **Purpose:** Scrape World Cup rosters from Wikipedia
- **Key Functions:**
  - `scrape_year(year)` - Scrape single year
  - `scrape_all_years()` - Scrape all years 1998-2026
- **Output:** `data/processed/rosters_combined.csv`

### `transfermarkt_api_scraper.py`
- **Purpose:** Fetch market values from Transfermarkt API
- **Key Functions:**
  - `scrape_market_values()` - Fetch market value history
  - `process_market_values()` - Match values to World Cup dates
- **API Endpoints:**
  - Search: `https://tmapi-alpha.transfermarkt.technology/search`
  - Market Values: `https://tmapi-alpha.transfermarkt.technology/player/{id}/market-value-history`

### `fix_korean_ids.py`
- **Purpose:** Verify and correct player IDs using national team rosters
- **Usage:**
  ```bash
  # Add missing IDs
  python fix_korean_ids.py --country "South Korea" --year 2026
  
  # Verify and correct wrong IDs
  python fix_korean_ids.py --verify --year 2026
  ```
- **Features:**
  - Playwright-based roster scraping
  - Fuzzy name matching with Korean name reversal
  - Supports multiple countries (see COUNTRY_TEAM_IDS mapping)

### `identify_wrong_ids.py`
- **Purpose:** Identify players with wrong IDs (read-only analysis)
- **Output:** Report of proposed corrections
- **Does NOT modify dataset** - only generates recommendations

## Data Files

### Input
- Wikipedia pages: `https://en.wikipedia.org/wiki/{YEAR}_FIFA_World_Cup_squads`

### Intermediate
- `data/processed/rosters_combined.csv` - Rosters without IDs/values
- `data/processed/player_ids.json` - Player ID mappings
- `data/raw/market_values_raw.json` - Raw market value history

### Output
- `data/processed/rosters_with_market_values.csv` - Final dataset
- `dashboard/data/processed/rosters_with_market_values.csv` - Dashboard copy

## World Cup Dates

Market values are matched to these dates:

```python
WORLD_CUP_DATES = {
    1998: "1998-06-10",
    2002: "2002-05-31",
    2006: "2006-06-09",
    2010: "2010-06-11",
    2014: "2014-06-12",
    2018: "2018-06-14",
    2022: "2022-11-20",
    2026: "2026-06-11",
}
```

## Common Issues & Solutions

### Issue: Player has ID but no market value

**Cause:** Wrong player ID or player never had professional valuation

**Solution:**
1. Run `identify_wrong_ids.py` to check if ID has data
2. If no data, run `fix_korean_ids.py --verify` to find correct ID
3. Manually verify on Transfermarkt national team page if needed

### Issue: Name doesn't match in roster verification

**Cause:** Transliteration differences, name order (Korean), prefixes (Arabic)

**Solution:**
- Script uses fuzzy matching (60% threshold)
- Handles Korean name reversal automatically
- Normalizes prefixes (al-, el-, de, etc.)
- May need manual correction for extreme variations

### Issue: Country not found in roster scraping

**Cause:** Missing COUNTRY_TEAM_IDS mapping

**Solution:**
Add country to `fix_korean_ids.py`:
```python
COUNTRY_TEAM_IDS = {
    'Country Name': 'team_id',  # Find ID from Transfermarkt URL
}
```

## Updating for New World Cup

When a new World Cup occurs:

1. **Update Wikipedia scraper:**
   ```python
   # Add new year to WORLD_CUP_YEARS
   WORLD_CUP_YEARS = [1998, 2002, ..., 2030]
   ```

2. **Update World Cup dates:**
   ```python
   # Add to WORLD_CUP_DATES
   2030: "2030-06-XX"
   ```

3. **Run complete pipeline:**
   ```bash
   # Scrape new rosters
   uv run python src/scrapers/wikipedia_scraper.py
   
   # Search for IDs
   # (run Step 2 from workflow)
   
   # Verify IDs
   uv run python src/scrapers/fix_korean_ids.py --verify --year 2030
   
   # Fetch market values
   uv run python src/scrapers/transfermarkt_api_scraper.py
   
   # Update dashboard
   cp data/processed/rosters_with_market_values.csv dashboard/data/processed/
   ```

## Archive

Old scripts have been moved to `archive/`:
- `archive/tests/` - Test scripts (9 files)
- `archive/fixes/` - One-off fix scripts (32 files)
- `archive/deprecated/` - Deprecated versions (8 files)

These are kept for reference but are not part of the core workflow.