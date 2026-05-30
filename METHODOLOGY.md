# Data Collection Methodology

## Overview
This document details the technical methodology for scraping FIFA World Cup roster data from Wikipedia and player market valuations from Transfermarkt.

## Wikipedia Scraping Methodology

### Target URLs
World Cup squad pages follow a consistent pattern:
- 1998: `https://en.wikipedia.org/wiki/1998_FIFA_World_Cup_squads`
- 2002: `https://en.wikipedia.org/wiki/2002_FIFA_World_Cup_squads`
- 2006: `https://en.wikipedia.org/wiki/2006_FIFA_World_Cup_squads`
- 2010: `https://en.wikipedia.org/wiki/2010_FIFA_World_Cup_squads`
- 2014: `https://en.wikipedia.org/wiki/2014_FIFA_World_Cup_squads`
- 2018: `https://en.wikipedia.org/wiki/2018_FIFA_World_Cup_squads`
- 2022: `https://en.wikipedia.org/wiki/2022_FIFA_World_Cup_squads`
- 2026: `https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_squads` (partial data)

### Page Structure Analysis

#### HTML Structure
Wikipedia squad pages typically contain:
1. **Country Headers** - `<h2>` or `<h3>` tags with country names
2. **Squad Tables** - `<table>` elements with class `wikitable`
3. **Player Rows** - `<tr>` elements containing player data
4. **Data Cells** - `<td>` elements with specific information

#### Table Columns (Typical Structure)
| Column | Content | Extraction Method |
|--------|---------|-------------------|
| No. | Jersey number | Direct text |
| Pos. | Position (GK/DF/MF/FW) | Direct text, standardize |
| Player | Player name | Link text or cell text |
| Date of birth (age) | DOB and age | Parse date format |
| Caps | International caps | Extract number |
| Club | Club team | Link text or cell text |

### Extraction Strategy

#### Step 1: Page Retrieval
```python
import requests
from bs4 import BeautifulSoup

def fetch_wikipedia_page(year):
    url = f"https://en.wikipedia.org/wiki/{year}_FIFA_World_Cup_squads"
    headers = {
        'User-Agent': 'WorldCupRosterProject/1.0 (Educational/Research)'
    }
    response = requests.get(url, headers=headers)
    return BeautifulSoup(response.content, 'lxml')
```

#### Step 2: Country Identification
```python
def extract_countries(soup):
    # Find all h2/h3 headers that contain country names
    # Typically preceded by flag images
    countries = []
    for header in soup.find_all(['h2', 'h3']):
        # Check for country indicators
        if header.find('span', class_='mw-headline'):
            country_name = header.get_text().strip()
            countries.append(country_name)
    return countries
```

#### Step 3: Table Parsing
```python
def parse_squad_table(table, country, year):
    rows = table.find_all('tr')[1:]  # Skip header row
    players = []
    
    for row in rows:
        cells = row.find_all(['td', 'th'])
        if len(cells) >= 6:  # Minimum expected columns
            player_data = {
                'Country': country,
                'Year': year,
                'Number': extract_number(cells[0]),
                'Position': extract_position(cells[1]),
                'Player': extract_player_name(cells[2]),
                'DOB': extract_dob(cells[3]),
                'Age': extract_age(cells[3]),
                'Caps': extract_caps(cells[4]),
                'Club': extract_club(cells[5]),
                'Club_Country': extract_club_country(cells[5])
            }
            players.append(player_data)
    
    return players
```

#### Step 4: Field Extraction Functions

**Jersey Number**
```python
def extract_number(cell):
    text = cell.get_text().strip()
    # Handle cases like "1", "12", or missing numbers
    return int(text) if text.isdigit() else None
```

**Position**
```python
def extract_position(cell):
    text = cell.get_text().strip().upper()
    # Standardize position codes
    position_map = {
        'GK': 'GK',
        'DF': 'DF', 'DEF': 'DF',
        'MF': 'MF', 'MID': 'MF',
        'FW': 'FW', 'FOR': 'FW', 'ATT': 'FW'
    }
    return position_map.get(text, text)
```

**Player Name**
```python
def extract_player_name(cell):
    # Try to get from link first (more reliable)
    link = cell.find('a')
    if link:
        return link.get_text().strip()
    return cell.get_text().strip()
```

**Date of Birth and Age**
```python
import re
from datetime import datetime

def extract_dob(cell):
    text = cell.get_text()
    # Pattern: (1990-05-15) or similar
    date_pattern = r'\((\d{4}-\d{2}-\d{2})\)'
    match = re.search(date_pattern, text)
    if match:
        return match.group(1)
    
    # Alternative pattern: "15 May 1990"
    # Implement additional parsing logic
    return None

def extract_age(cell):
    text = cell.get_text()
    # Pattern: "age 32" or "(aged 32)"
    age_pattern = r'age[d]?\s+(\d+)'
    match = re.search(age_pattern, text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None
```

**Caps**
```python
def extract_caps(cell):
    text = cell.get_text().strip()
    # Extract number, handle cases like "45" or "45 (3)"
    numbers = re.findall(r'\d+', text)
    return int(numbers[0]) if numbers else None
```

**Club and Club Country**
```python
def extract_club(cell):
    link = cell.find('a')
    if link:
        return link.get_text().strip()
    return cell.get_text().strip()

def extract_club_country(cell):
    # Look for flag image or country indicator
    img = cell.find('img')
    if img and 'alt' in img.attrs:
        return img['alt'].strip()
    
    # Alternative: parse from text
    # May need country code mapping
    return None
```

### Handling Variations Across Years

#### Known Variations
1. **Table Structure**: Column order may vary
2. **Date Formats**: Different date representations
3. **Missing Data**: Some years have incomplete information
4. **Encoding Issues**: Special characters in names

#### Adaptive Parsing Strategy
```python
def identify_column_indices(header_row):
    """Dynamically identify column positions"""
    columns = {}
    headers = header_row.find_all(['th', 'td'])
    
    for idx, header in enumerate(headers):
        text = header.get_text().strip().lower()
        if 'no' in text or '#' in text:
            columns['number'] = idx
        elif 'pos' in text:
            columns['position'] = idx
        elif 'player' in text or 'name' in text:
            columns['player'] = idx
        elif 'birth' in text or 'dob' in text:
            columns['dob'] = idx
        elif 'cap' in text:
            columns['caps'] = idx
        elif 'club' in text:
            columns['club'] = idx
    
    return columns
```

### Data Quality Checks

#### Validation Rules
1. **Required Fields**: Country, Player, Position must be present
2. **Number Range**: Jersey numbers 1-99
3. **Position Values**: Must be GK, DF, MF, or FW
4. **Age Range**: Reasonable age range (16-45)
5. **Date Format**: Valid ISO date format
6. **Caps**: Non-negative integer

#### Error Handling
```python
def validate_player_data(player):
    errors = []
    
    if not player.get('Player'):
        errors.append("Missing player name")
    
    if not player.get('Position') in ['GK', 'DF', 'MF', 'FW']:
        errors.append(f"Invalid position: {player.get('Position')}")
    
    age = player.get('Age')
    if age and (age < 16 or age > 45):
        errors.append(f"Unusual age: {age}")
    
    return errors
```

## Transfermarkt Scraping Methodology

### Challenge: Dynamic Content
Transfermarkt uses JavaScript to load content dynamically, requiring browser automation.

### Technology Choice: Playwright
- More modern than Selenium
- Better performance
- Built-in waiting mechanisms
- Easier to maintain

### URL Pattern Analysis

#### Player Search
```
https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={player_name}
```

#### Player Profile
```
https://www.transfermarkt.com/{player_slug}/profil/spieler/{player_id}
```

#### Market Value History
```
https://www.transfermarkt.com/{player_slug}/marktwertverlauf/spieler/{player_id}
```

### Extraction Strategy

#### Step 1: Player Matching
```python
from playwright.sync_api import sync_playwright

def search_player(player_name, country):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Search for player
        search_url = f"https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={player_name}"
        page.goto(search_url)
        
        # Find matching player by country
        results = page.query_selector_all('.items tbody tr')
        for result in results:
            # Check if country matches
            country_cell = result.query_selector('.flaggenrahmen')
            if country_cell and country in country_cell.get_attribute('title'):
                player_link = result.query_selector('a.spielprofil_tooltip')
                return player_link.get_attribute('href')
        
        browser.close()
        return None
```

#### Step 2: Market Value Extraction
```python
def get_market_value_at_date(player_url, target_date):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Navigate to market value history
        page.goto(player_url + '/marktwertverlauf')
        
        # Wait for chart to load
        page.wait_for_selector('.highcharts-container')
        
        # Extract data points
        data_points = page.evaluate('''() => {
            const chart = Highcharts.charts[0];
            return chart.series[0].data.map(point => ({
                date: new Date(point.x),
                value: point.y
            }));
        }''')
        
        # Find closest value to target date
        closest_value = find_closest_value(data_points, target_date)
        
        browser.close()
        return closest_value
```

#### Step 3: Rate Limiting
```python
import time
import random

def respectful_scraping():
    # Random delay between requests (2-5 seconds)
    delay = random.uniform(2, 5)
    time.sleep(delay)
    
    # Implement exponential backoff on errors
    # Track request count per hour
    # Respect robots.txt
```

### Player Name Matching Strategy

#### Fuzzy Matching
```python
from fuzzywuzzy import fuzz

def match_player_names(wiki_name, transfermarkt_name):
    # Calculate similarity score
    score = fuzz.ratio(wiki_name.lower(), transfermarkt_name.lower())
    
    # Also try without accents
    wiki_clean = remove_accents(wiki_name)
    tm_clean = remove_accents(transfermarkt_name)
    score_clean = fuzz.ratio(wiki_clean.lower(), tm_clean.lower())
    
    return max(score, score_clean) > 85  # 85% similarity threshold
```

#### Manual Review List
Maintain a CSV of manual mappings for difficult cases:
```csv
Wikipedia_Name,Transfermarkt_Name,Player_ID
Cristiano Ronaldo,Cristiano Ronaldo,8198
Neymar,Neymar Jr.,68290
```

### Data Caching Strategy

#### Cache Structure
```
data/cache/
├── player_searches/
│   └── {player_name_hash}.json
└── market_values/
    └── {player_id}_{year}.json
```

#### Cache Implementation
```python
import hashlib
import json
from pathlib import Path

def get_cached_search(player_name):
    cache_key = hashlib.md5(player_name.encode()).hexdigest()
    cache_file = Path(f'data/cache/player_searches/{cache_key}.json')
    
    if cache_file.exists():
        with open(cache_file) as f:
            return json.load(f)
    return None

def cache_search_result(player_name, result):
    cache_key = hashlib.md5(player_name.encode()).hexdigest()
    cache_file = Path(f'data/cache/player_searches/{cache_key}.json')
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(cache_file, 'w') as f:
        json.dump(result, f)
```

## Data Merging Methodology

### Matching Strategy
1. **Exact Match**: Player name + country + year
2. **Fuzzy Match**: Similar names + country + year
3. **Manual Review**: Unmatched players

### Merge Process
```python
def merge_datasets(rosters_df, market_values_df):
    merged = rosters_df.copy()
    merged['Market_Value_EUR'] = None
    merged['Market_Value_Date'] = None
    merged['Match_Confidence'] = None
    
    for idx, row in merged.iterrows():
        # Try exact match
        match = market_values_df[
            (market_values_df['Player'] == row['Player']) &
            (market_values_df['Country'] == row['Country']) &
            (market_values_df['Year'] == row['Year'])
        ]
        
        if not match.empty:
            merged.at[idx, 'Market_Value_EUR'] = match.iloc[0]['Market_Value_EUR']
            merged.at[idx, 'Match_Confidence'] = 'exact'
        else:
            # Try fuzzy match
            fuzzy_match = find_fuzzy_match(row, market_values_df)
            if fuzzy_match:
                merged.at[idx, 'Market_Value_EUR'] = fuzzy_match['value']
                merged.at[idx, 'Match_Confidence'] = 'fuzzy'
    
    return merged
```

## Ethical Considerations

### Compliance
- ✅ Respect robots.txt
- ✅ Implement rate limiting
- ✅ Use appropriate User-Agent
- ✅ Cache responses to minimize requests
- ✅ Public data only
- ✅ Educational/research purpose

### Attribution
- Cite Wikipedia as data source
- Cite Transfermarkt as market value source
- Include data collection date
- Provide methodology documentation

## Error Recovery

### Retry Logic
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def fetch_with_retry(url):
    response = requests.get(url)
    response.raise_for_status()
    return response
```

### Logging Strategy
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraping.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

## Testing Strategy

### Unit Tests
- Test individual extraction functions
- Test data validation
- Test name matching algorithms

### Integration Tests
- Test full scraping pipeline
- Test data merging
- Test error handling

### Data Quality Tests
- Verify completeness percentages
- Check for duplicates
- Validate data ranges
- Compare against known values

## Performance Optimization

### Parallel Processing
```python
from concurrent.futures import ThreadPoolExecutor

def scrape_all_years(years):
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = executor.map(scrape_year, years)
    return list(results)
```

### Memory Management
- Process data in chunks
- Use generators for large datasets
- Clear caches periodically

## Maintenance Plan

### Regular Updates
- Check for Wikipedia page structure changes
- Monitor Transfermarkt anti-scraping measures
- Update player name mappings
- Refresh market value data

### Version Control
- Tag data collection dates
- Track methodology changes
- Document breaking changes